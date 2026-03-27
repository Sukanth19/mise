from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from app.models import User
import bcrypt
from jose import jwt
from datetime import datetime, timedelta
from app.config import settings
import re
from collections import defaultdict
from time import time

router = APIRouter(prefix="/api/auth", tags=["authentication"])

# Simple in-memory rate limiting (for production, use Redis)
login_attempts = defaultdict(list)
RATE_LIMIT_WINDOW = 300  # 5 minutes
MAX_ATTEMPTS = 5


def check_rate_limit(identifier: str) -> bool:
    """Check if the identifier has exceeded rate limit."""
    now = time()
    # Clean old attempts
    login_attempts[identifier] = [
        attempt_time for attempt_time in login_attempts[identifier]
        if now - attempt_time < RATE_LIMIT_WINDOW
    ]
    
    if len(login_attempts[identifier]) >= MAX_ATTEMPTS:
        return False
    
    login_attempts[identifier].append(now)
    return True


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password strength.
    Returns (is_valid, error_message).
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if len(password) > 128:
        return False, "Password must not exceed 128 characters"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    return True, ""


def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    password_bytes = password.encode('utf-8')[:72]  # bcrypt 72-byte limit
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against bcrypt hash."""
    password_bytes = password.encode('utf-8')[:72]  # bcrypt 72-byte limit
    hashed_bytes = hashed.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(user_id: int) -> str:
    """Create JWT access token."""
    expire = datetime.utcnow() + timedelta(hours=settings.access_token_expire_hours)
    to_encode = {"sub": str(user_id), "exp": expire}
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user with username and password."""
    # Validate password strength
    is_valid, error_msg = validate_password_strength(request.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
            headers={"error_code": "WEAK_PASSWORD"}
        )
    
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == request.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already registered",
            headers={"error_code": "USERNAME_EXISTS"}
        )
    
    # Create new user
    hashed_password = hash_password(request.password)
    user = User(username=request.username, password_hash=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return UserResponse(id=user.id, username=user.username)


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, req: Request, db: Session = Depends(get_db)):
    """Authenticate user and return JWT token."""
    # Rate limiting based on IP address
    client_ip = req.client.host if req.client else "unknown"
    identifier = f"{client_ip}:{request.username}"
    
    if not check_rate_limit(identifier):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later.",
            headers={"error_code": "RATE_LIMIT_EXCEEDED"}
        )
    
    user = db.query(User).filter(User.username == request.username).first()
    
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"error_code": "INVALID_CREDENTIALS"}
        )
    
    # Clear rate limit on successful login
    if identifier in login_attempts:
        login_attempts[identifier].clear()
    
    access_token = create_access_token(user.id)
    return TokenResponse(access_token=access_token, token_type="bearer")
