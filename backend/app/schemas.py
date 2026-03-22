from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class RegisterRequest(BaseModel):
    username: str
    password: str = Field(..., min_length=8)


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class UserResponse(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


class RecipeCreate(BaseModel):
    title: str
    image_url: Optional[str] = None
    ingredients: List[str]
    steps: List[str]
    tags: Optional[List[str]] = None
    reference_link: Optional[str] = None


class RecipeUpdate(BaseModel):
    title: Optional[str] = None
    image_url: Optional[str] = None
    ingredients: Optional[List[str]] = None
    steps: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    reference_link: Optional[str] = None


class RecipeResponse(BaseModel):
    id: int
    user_id: int
    title: str
    image_url: Optional[str]
    ingredients: List[str]
    steps: List[str]
    tags: Optional[List[str]]
    reference_link: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm(cls, obj):
        """Custom ORM conversion to handle JSON deserialization."""
        import json
        data = {
            'id': obj.id,
            'user_id': obj.user_id,
            'title': obj.title,
            'image_url': obj.image_url,
            'ingredients': json.loads(obj.ingredients) if isinstance(obj.ingredients, str) else obj.ingredients,
            'steps': json.loads(obj.steps) if isinstance(obj.steps, str) else obj.steps,
            'tags': json.loads(obj.tags) if obj.tags and isinstance(obj.tags, str) else obj.tags,
            'reference_link': obj.reference_link,
            'created_at': obj.created_at,
            'updated_at': obj.updated_at
        }
        return cls(**data)


class ImageUploadResponse(BaseModel):
    url: str
