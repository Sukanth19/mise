import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from bson import ObjectId
from app.repositories.user_repository import UserRepository
from app.config import settings


class AuthService:
    """Authentication service for user management and JWT operations."""
    
    def __init__(self, user_repository: UserRepository):
        """
        Initialize auth service with user repository.
        
        Args:
            user_repository: UserRepository instance for data access
        """
        self.user_repository = user_repository
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a plain text password."""
        # Ensure password is within bcrypt's 72-byte limit
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a plain text password against a hashed password."""
        password_bytes = plain_password.encode('utf-8')
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    
    async def create_user(self, username: str, password: str) -> Dict[str, Any]:
        """
        Create a new user with hashed password.
        
        Args:
            username: Username for the new user
            password: Plain text password
            
        Returns:
            User document with _id, username, password_hash, created_at
        """
        password_hash = AuthService.hash_password(password)
        user_data = {
            "username": username,
            "password_hash": password_hash,
            "created_at": datetime.utcnow()
        }
        user_id = await self.user_repository.create(user_data)
        user = await self.user_repository.find_by_id(user_id)
        return user
    
    async def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a user by username.
        
        Args:
            username: Username to search for
            
        Returns:
            User document if found, None otherwise
        """
        return await self.user_repository.find_by_username(username)
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a user by ID.
        
        Args:
            user_id: ObjectId string of the user
            
        Returns:
            User document if found, None otherwise
        """
        return await self.user_repository.find_by_id(user_id)
    
    async def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate a user with username and password.
        
        Args:
            username: Username to authenticate
            password: Plain text password
            
        Returns:
            User document if authentication successful, None otherwise
        """
        user = await self.get_user_by_username(username)
        if not user:
            return None
        if not AuthService.verify_password(password, user["password_hash"]):
            return None
        return user
    
    @staticmethod
    def create_access_token(user_id: str) -> str:
        """
        Create a JWT access token with 24-hour expiration.
        
        Args:
            user_id: ObjectId string of the user
            
        Returns:
            JWT token string
        """
        from datetime import timezone
        expire = datetime.now(timezone.utc) + timedelta(hours=settings.access_token_expire_hours)
        to_encode = {"sub": str(user_id), "exp": expire}
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[str]:
        """
        Verify and decode a JWT token, returning the user_id.
        
        Args:
            token: JWT token string
            
        Returns:
            User ObjectId string if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            user_id: str = payload.get("sub")
            if user_id is None:
                return None
            return user_id
        except JWTError:
            return None
