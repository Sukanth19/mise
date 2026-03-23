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

# ============================================================================
# Rating Schemas
# ============================================================================

class RatingCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Rating value between 1 and 5")


class RatingUpdate(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Rating value between 1 and 5")


class RatingResponse(BaseModel):
    id: int
    recipe_id: int
    user_id: int
    rating: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Note Schemas
# ============================================================================

class NoteCreate(BaseModel):
    note_text: str = Field(..., min_length=1)


class NoteResponse(BaseModel):
    id: int
    recipe_id: int
    user_id: int
    note_text: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Collection Schemas
# ============================================================================

class CollectionCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    parent_collection_id: Optional[int] = None


class CollectionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    cover_image_url: Optional[str] = None


class CollectionResponse(BaseModel):
    id: int
    user_id: int
    name: str
    description: Optional[str]
    cover_image_url: Optional[str]
    parent_collection_id: Optional[int]
    nesting_level: int
    share_token: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Meal Planning Schemas
# ============================================================================

class MealPlanCreate(BaseModel):
    recipe_id: int
    meal_date: str = Field(..., description="Date in YYYY-MM-DD format")
    meal_time: str = Field(..., pattern="^(breakfast|lunch|dinner|snack)$")


class MealPlanUpdate(BaseModel):
    meal_date: Optional[str] = Field(None, description="Date in YYYY-MM-DD format")
    meal_time: Optional[str] = Field(None, pattern="^(breakfast|lunch|dinner|snack)$")


class MealPlanResponse(BaseModel):
    id: int
    user_id: int
    recipe_id: int
    meal_date: str
    meal_time: str
    created_at: datetime

    class Config:
        from_attributes = True


class TemplateItemCreate(BaseModel):
    recipe_id: int
    day_offset: int = Field(..., ge=0)
    meal_time: str = Field(..., pattern="^(breakfast|lunch|dinner|snack)$")


class TemplateCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    items: List[TemplateItemCreate]


class TemplateItemResponse(BaseModel):
    id: int
    template_id: int
    recipe_id: int
    day_offset: int
    meal_time: str

    class Config:
        from_attributes = True


class TemplateResponse(BaseModel):
    id: int
    user_id: int
    name: str
    description: Optional[str]
    items: List[TemplateItemResponse]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Shopping List Schemas
# ============================================================================

class ShoppingListCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    recipe_ids: Optional[List[int]] = None
    meal_plan_start_date: Optional[str] = Field(None, description="Date in YYYY-MM-DD format")
    meal_plan_end_date: Optional[str] = Field(None, description="Date in YYYY-MM-DD format")


class ShoppingListItemResponse(BaseModel):
    id: int
    shopping_list_id: int
    ingredient_name: str
    quantity: Optional[str]
    category: str
    is_checked: bool
    is_custom: bool
    recipe_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class ShoppingListResponse(BaseModel):
    id: int
    user_id: int
    name: str
    share_token: Optional[str]
    items: List[ShoppingListItemResponse]
    created_at: datetime

    class Config:
        from_attributes = True


class CustomItemCreate(BaseModel):
    ingredient_name: str = Field(..., min_length=1, max_length=255)
    quantity: Optional[str] = None
    category: Optional[str] = Field(None, pattern="^(produce|dairy|meat|pantry|other)$")


# ============================================================================
# Nutrition Schemas
# ============================================================================

class NutritionCreate(BaseModel):
    calories: Optional[float] = Field(None, ge=0)
    protein_g: Optional[float] = Field(None, ge=0)
    carbs_g: Optional[float] = Field(None, ge=0)
    fat_g: Optional[float] = Field(None, ge=0)
    fiber_g: Optional[float] = Field(None, ge=0)


class NutritionUpdate(BaseModel):
    calories: Optional[float] = Field(None, ge=0)
    protein_g: Optional[float] = Field(None, ge=0)
    carbs_g: Optional[float] = Field(None, ge=0)
    fat_g: Optional[float] = Field(None, ge=0)
    fiber_g: Optional[float] = Field(None, ge=0)


class NutritionResponse(BaseModel):
    id: int
    recipe_id: int
    calories: Optional[float]
    protein_g: Optional[float]
    carbs_g: Optional[float]
    fat_g: Optional[float]
    fiber_g: Optional[float]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DietaryLabelsRequest(BaseModel):
    labels: List[str] = Field(..., description="List of dietary labels")


class AllergensRequest(BaseModel):
    allergens: List[str] = Field(..., description="List of allergens")


class DailyNutrition(BaseModel):
    date: str
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float


class NutritionSummaryResponse(BaseModel):
    daily_totals: List[DailyNutrition]
    weekly_total: NutritionResponse
    missing_nutrition_count: int


# ============================================================================
# Social Schemas
# ============================================================================

class CommentCreate(BaseModel):
    comment_text: str = Field(..., min_length=1)


class CommentResponse(BaseModel):
    id: int
    recipe_id: int
    user_id: int
    comment_text: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PublicRecipeResponse(BaseModel):
    id: int
    user_id: int
    title: str
    image_url: Optional[str]
    ingredients: List[str]
    steps: List[str]
    tags: Optional[List[str]]
    reference_link: Optional[str]
    visibility: str
    author: UserResponse
    likes_count: int
    comments: List[CommentResponse]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserFollowResponse(BaseModel):
    id: int
    follower_id: int
    following_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ShareMetadataResponse(BaseModel):
    title: str
    description: str
    image_url: Optional[str]
    url: str
