"""
MongoDB document models using Pydantic for validation.

This module defines Pydantic models for MongoDB documents that replace
the SQLAlchemy models. The models follow MongoDB best practices:
- Embed one-to-one relationships (e.g., Recipe -> NutritionFacts)
- Embed small arrays (e.g., dietary_labels, allergen_warnings)
- Use references for many-to-many relationships
- Use ObjectId for document identifiers
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime, date
from bson import ObjectId
from decimal import Decimal


class PyObjectId(ObjectId):
    """
    Custom ObjectId type for Pydantic validation.
    
    This class extends bson.ObjectId to work with Pydantic's validation system.
    It allows ObjectId fields to be validated and serialized properly.
    """
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        """
        Validate that the value is a valid ObjectId.
        
        Args:
            v: Value to validate (can be str, ObjectId, or bytes)
            
        Returns:
            ObjectId instance
            
        Raises:
            ValueError: If the value is not a valid ObjectId
        """
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)
    
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        """Pydantic v2 compatibility for schema generation."""
        from pydantic_core import core_schema
        return core_schema.union_schema([
            core_schema.is_instance_schema(ObjectId),
            core_schema.chain_schema([
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(cls.validate),
            ])
        ])


class UserDocument(BaseModel):
    """
    User document model.
    
    Represents a user account in the system.
    """
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    username: str = Field(..., min_length=1, max_length=255)
    password_hash: str = Field(..., min_length=1, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class NutritionFactsEmbedded(BaseModel):
    """
    Embedded nutrition facts within a recipe document.
    
    This is embedded in RecipeDocument rather than being a separate collection.
    """
    calories: Optional[Decimal] = None
    protein_g: Optional[Decimal] = None
    carbs_g: Optional[Decimal] = None
    fat_g: Optional[Decimal] = None
    fiber_g: Optional[Decimal] = None
    
    class Config:
        arbitrary_types_allowed = True


class RecipeDocument(BaseModel):
    """
    Recipe document model with embedded nutrition, labels, and allergens.
    
    Embeds:
    - nutrition_facts: One-to-one relationship
    - dietary_labels: Small array of labels
    - allergen_warnings: Small array of allergens
    """
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: PyObjectId
    title: str = Field(..., min_length=1, max_length=255)
    image_url: Optional[str] = Field(None, max_length=500)
    ingredients: List[str] = Field(default_factory=list)
    steps: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    reference_link: Optional[str] = Field(None, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_favorite: bool = False
    visibility: str = Field(default="private")
    servings: int = Field(default=1, ge=1)
    source_recipe_id: Optional[PyObjectId] = None
    source_author_id: Optional[PyObjectId] = None
    
    # Embedded one-to-one relationship
    nutrition_facts: Optional[NutritionFactsEmbedded] = None
    
    # Embedded arrays for labels and allergens
    dietary_labels: List[str] = Field(default_factory=list)
    allergen_warnings: List[str] = Field(default_factory=list)
    
    @field_validator("visibility")
    @classmethod
    def validate_visibility(cls, v):
        """Validate visibility is one of the allowed values."""
        allowed = ["private", "public", "unlisted"]
        if v not in allowed:
            raise ValueError(f"visibility must be one of {allowed}")
        return v
    
    @field_validator("dietary_labels")
    @classmethod
    def validate_dietary_labels(cls, v):
        """Validate dietary labels are from allowed set."""
        allowed = ["vegan", "vegetarian", "gluten-free", "dairy-free", "keto", "paleo", "low-carb"]
        for label in v:
            if label not in allowed:
                raise ValueError(f"dietary label '{label}' not in allowed set: {allowed}")
        return v
    
    @field_validator("allergen_warnings")
    @classmethod
    def validate_allergen_warnings(cls, v):
        """Validate allergen warnings are from allowed set."""
        allowed = ["nuts", "dairy", "eggs", "soy", "wheat", "fish", "shellfish"]
        for allergen in v:
            if allergen not in allowed:
                raise ValueError(f"allergen '{allergen}' not in allowed set: {allowed}")
        return v
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, Decimal: float}


class RecipeRatingDocument(BaseModel):
    """
    Recipe rating document model.
    
    Stored as a separate collection with references to recipe and user.
    """
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    recipe_id: PyObjectId
    user_id: PyObjectId
    rating: int = Field(..., ge=1, le=5)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class RecipeNoteDocument(BaseModel):
    """
    Recipe note document model.
    
    Stored as a separate collection with references to recipe and user.
    """
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    recipe_id: PyObjectId
    user_id: PyObjectId
    note_text: str = Field(..., min_length=1)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class CollectionDocument(BaseModel):
    """
    Collection document model with embedded recipe_ids array.
    
    Embeds:
    - recipe_ids: Array of ObjectIds referencing recipes
    """
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: PyObjectId
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    cover_image_url: Optional[str] = Field(None, max_length=500)
    parent_collection_id: Optional[PyObjectId] = None
    nesting_level: int = Field(default=0, ge=0, le=3)
    recipe_ids: List[PyObjectId] = Field(default_factory=list)
    share_token: Optional[str] = Field(None, max_length=100)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class MealPlanDocument(BaseModel):
    """
    Meal plan document model.
    
    References recipe and user via ObjectIds.
    """
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: PyObjectId
    recipe_id: PyObjectId
    meal_date: date
    meal_time: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @field_validator("meal_time")
    @classmethod
    def validate_meal_time(cls, v):
        """Validate meal_time is one of the allowed values."""
        allowed = ["breakfast", "lunch", "dinner", "snack"]
        if v not in allowed:
            raise ValueError(f"meal_time must be one of {allowed}")
        return v
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class MealPlanTemplateItemEmbedded(BaseModel):
    """
    Embedded meal plan template item within a template document.
    """
    recipe_id: PyObjectId
    day_offset: int = Field(..., ge=0)
    meal_time: str
    
    @field_validator("meal_time")
    @classmethod
    def validate_meal_time(cls, v):
        """Validate meal_time is one of the allowed values."""
        allowed = ["breakfast", "lunch", "dinner", "snack"]
        if v not in allowed:
            raise ValueError(f"meal_time must be one of {allowed}")
        return v
    
    class Config:
        arbitrary_types_allowed = True


class MealPlanTemplateDocument(BaseModel):
    """
    Meal plan template document model with embedded items.
    
    Embeds:
    - items: Array of template items
    """
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: PyObjectId
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    items: List[MealPlanTemplateItemEmbedded] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class ShoppingListItemEmbedded(BaseModel):
    """
    Embedded shopping list item within a shopping list document.
    """
    ingredient_name: str = Field(..., min_length=1, max_length=255)
    quantity: Optional[str] = Field(None, max_length=100)
    category: str = Field(default="other")
    is_checked: bool = False
    is_custom: bool = False
    recipe_id: Optional[PyObjectId] = None
    
    @field_validator("category")
    @classmethod
    def validate_category(cls, v):
        """Validate category is one of the allowed values."""
        allowed = ["produce", "dairy", "meat", "pantry", "other"]
        if v not in allowed:
            raise ValueError(f"category must be one of {allowed}")
        return v
    
    class Config:
        arbitrary_types_allowed = True


class ShoppingListDocument(BaseModel):
    """
    Shopping list document model with embedded items.
    
    Embeds:
    - items: Array of shopping list items
    """
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: PyObjectId
    name: str = Field(..., min_length=1, max_length=255)
    share_token: Optional[str] = Field(None, max_length=100)
    items: List[ShoppingListItemEmbedded] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class UserFollowDocument(BaseModel):
    """
    User follow document model.
    
    Stored as a separate collection with references to follower and following users.
    """
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    follower_id: PyObjectId
    following_id: PyObjectId
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @field_validator("following_id")
    @classmethod
    def validate_no_self_follow(cls, v, info):
        """Validate that a user cannot follow themselves."""
        if "follower_id" in info.data and v == info.data["follower_id"]:
            raise ValueError("Users cannot follow themselves")
        return v
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class RecipeLikeDocument(BaseModel):
    """
    Recipe like document model.
    
    Stored as a separate collection with references to recipe and user.
    """
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    recipe_id: PyObjectId
    user_id: PyObjectId
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class RecipeCommentDocument(BaseModel):
    """
    Recipe comment document model.
    
    Stored as a separate collection with references to recipe and user.
    """
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    recipe_id: PyObjectId
    user_id: PyObjectId
    comment_text: str = Field(..., min_length=1)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
