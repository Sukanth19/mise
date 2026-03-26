from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.database import mongodb
from app.schemas import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from app.services.auth_service import AuthService
from app.repositories.user_repository import UserRepository

router = APIRouter(prefix="/api/auth", tags=["authentication"])


async def get_mongodb() -> AsyncIOMotorDatabase:
    """Get MongoDB database instance."""
    return await mongodb.get_database()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: AsyncIOMotorDatabase = Depends(get_mongodb)):
    """Register a new user with username and password."""
    user_repo = UserRepository(db)
    auth_service = AuthService(user_repo)
    
    # Check if username already exists
    existing_user = await auth_service.get_user_by_username(request.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already registered",
            headers={"error_code": "USERNAME_EXISTS"}
        )
    
    user = await auth_service.create_user(request.username, request.password)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: AsyncIOMotorDatabase = Depends(get_mongodb)):
    """Authenticate user and return JWT token."""
    user_repo = UserRepository(db)
    auth_service = AuthService(user_repo)
    
    user = await auth_service.authenticate_user(request.username, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"error_code": "INVALID_CREDENTIALS"}
        )
    
    access_token = auth_service.create_access_token(str(user["_id"]))
    return TokenResponse(access_token=access_token, token_type="bearer")
