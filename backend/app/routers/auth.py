from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from app.models import User
import bcrypt
from jose import jwt
from datetime import datetime, timedelta
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["authentication"])


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
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return JWT token."""
    user = db.query(User).filter(User.username == request.username).first()
    
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"error_code": "INVALID_CREDENTIALS"}
        )
    
    access_token = create_access_token(user.id)
    return TokenResponse(access_token=access_token, token_type="bearer")
