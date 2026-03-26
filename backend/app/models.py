from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, Text, Boolean, Date, DECIMAL, CheckConstraint, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import ARRAY
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    recipes = relationship("Recipe", back_populates="user", foreign_keys="Recipe.user_id")


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(500), nullable=False, index=True)
    image_url = Column(String(1000), nullable=True)
    # Using Text for SQLite compatibility - will store JSON strings
    # In production with PostgreSQL, these would be ARRAY(Text)
    ingredients = Column(Text, nullable=False)
    steps = Column(Text, nullable=False)
    tags = Column(Text, nullable=True)
    reference_link = Column(String(1000), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # New columns for enhancements
    is_favorite = Column(Boolean, default=False)
    visibility = Column(String(20), default='private', index=True)
    servings = Column(Integer, default=1)
    source_recipe_id = Column(Integer, ForeignKey("recipes.id", ondelete="SET NULL"), nullable=True)
    source_author_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    __table_args__ = (
        CheckConstraint("visibility IN ('private', 'public', 'unlisted')", name='check_visibility'),
        Index('idx_recipe_user_created', 'user_id', 'created_at'),
    )
    
    # Relationships
    user = relationship("User", back_populates="recipes", foreign_keys=[user_id])
    nutrition_facts = relationship("NutritionFacts", back_populates="recipe", uselist=False)
    dietary_labels = relationship("DietaryLabel", back_populates="recipe")
    allergen_warnings = relationship("AllergenWarning", back_populates="recipe")
    ratings = relationship("RecipeRating", back_populates="recipe")
    notes = relationship("RecipeNote", back_populates="recipe")
    collection_recipes = relationship("CollectionRecipe", back_populates="recipe")
    meal_plans = relationship("MealPlan", back_populates="recipe")


class RecipeRating(Base):
    __tablename__ = "recipe_ratings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    rating = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('recipe_id', 'user_id', name='uq_recipe_user_rating'),
        CheckConstraint("rating >= 1 AND rating <= 5", name='check_rating_range'),
    )
    
    # Relationships
    recipe = relationship("Recipe", back_populates="ratings")


class RecipeNote(Base):
    __tablename__ = "recipe_notes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    note_text = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('idx_recipe_user', 'recipe_id', 'user_id'),
    )
    
    # Relationships
    recipe = relationship("Recipe", back_populates="notes")


class Collection(Base):
    __tablename__ = "collections"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    cover_image_url = Column(String(1000), nullable=True)
    parent_collection_id = Column(Integer, ForeignKey("collections.id", ondelete="CASCADE"), nullable=True, index=True)
    nesting_level = Column(Integer, default=0)
    share_token = Column(String(100), unique=True, nullable=True, index=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint("nesting_level <= 3", name='check_nesting_level'),
        Index('idx_collection_user_created', 'user_id', 'created_at'),
    )
    
    # Relationships
    collection_recipes = relationship("CollectionRecipe", back_populates="collection")


class CollectionRecipe(Base):
    __tablename__ = "collection_recipes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    collection_id = Column(Integer, ForeignKey("collections.id", ondelete="CASCADE"), nullable=False, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False, index=True)
    added_at = Column(TIMESTAMP, server_default=func.now())

    __table_args__ = (
        UniqueConstraint('collection_id', 'recipe_id', name='uq_collection_recipe'),
    )
    
    # Relationships
    collection = relationship("Collection", back_populates="collection_recipes")
    recipe = relationship("Recipe", back_populates="collection_recipes")


class MealPlan(Base):
    __tablename__ = "meal_plans"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False, index=True)
    meal_date = Column(Date, nullable=False, index=True)
    meal_time = Column(String(20), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    __table_args__ = (
        CheckConstraint("meal_time IN ('breakfast', 'lunch', 'dinner', 'snack')", name='check_meal_time'),
        Index('idx_user_meal_date', 'user_id', 'meal_date'),
    )
    
    # Relationships
    recipe = relationship("Recipe", back_populates="meal_plans")


class MealPlanTemplate(Base):
    __tablename__ = "meal_plan_templates"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())


class MealPlanTemplateItem(Base):
    __tablename__ = "meal_plan_template_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    template_id = Column(Integer, ForeignKey("meal_plan_templates.id", ondelete="CASCADE"), nullable=False, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False, index=True)
    day_offset = Column(Integer, nullable=False)
    meal_time = Column(String(20), nullable=False)

    __table_args__ = (
        CheckConstraint("meal_time IN ('breakfast', 'lunch', 'dinner', 'snack')", name='check_template_meal_time'),
    )


class ShoppingList(Base):
    __tablename__ = "shopping_lists"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    share_token = Column(String(100), unique=True, nullable=True, index=True)
    created_at = Column(TIMESTAMP, server_default=func.now())


class ShoppingListItem(Base):
    __tablename__ = "shopping_list_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    shopping_list_id = Column(Integer, ForeignKey("shopping_lists.id", ondelete="CASCADE"), nullable=False, index=True)
    ingredient_name = Column(String(255), nullable=False)
    quantity = Column(String(100), nullable=True)
    category = Column(String(50), default='other')
    is_checked = Column(Boolean, default=False)
    is_custom = Column(Boolean, default=False)
    recipe_id = Column(Integer, ForeignKey("recipes.id", ondelete="SET NULL"), nullable=True, index=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    __table_args__ = (
        CheckConstraint("category IN ('produce', 'dairy', 'meat', 'pantry', 'other')", name='check_category'),
    )


class NutritionFacts(Base):
    __tablename__ = "nutrition_facts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    calories = Column(DECIMAL(10, 2), nullable=True)
    protein_g = Column(DECIMAL(10, 2), nullable=True)
    carbs_g = Column(DECIMAL(10, 2), nullable=True)
    fat_g = Column(DECIMAL(10, 2), nullable=True)
    fiber_g = Column(DECIMAL(10, 2), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    recipe = relationship("Recipe", back_populates="nutrition_facts")


class DietaryLabel(Base):
    __tablename__ = "dietary_labels"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False, index=True)
    label = Column(String(50), nullable=False, index=True)

    __table_args__ = (
        UniqueConstraint('recipe_id', 'label', name='uq_recipe_dietary_label'),
        CheckConstraint("label IN ('vegan', 'vegetarian', 'gluten-free', 'dairy-free', 'keto', 'paleo', 'low-carb')", name='check_dietary_label'),
    )
    
    # Relationships
    recipe = relationship("Recipe", back_populates="dietary_labels")


class AllergenWarning(Base):
    __tablename__ = "allergen_warnings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False, index=True)
    allergen = Column(String(50), nullable=False, index=True)

    __table_args__ = (
        UniqueConstraint('recipe_id', 'allergen', name='uq_recipe_allergen'),
        CheckConstraint("allergen IN ('nuts', 'dairy', 'eggs', 'soy', 'wheat', 'fish', 'shellfish')", name='check_allergen'),
    )
    
    # Relationships
    recipe = relationship("Recipe", back_populates="allergen_warnings")


class UserFollow(Base):
    __tablename__ = "user_follows"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    follower_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    following_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    __table_args__ = (
        UniqueConstraint('follower_id', 'following_id', name='uq_follower_following'),
        CheckConstraint("follower_id != following_id", name='check_no_self_follow'),
    )


class RecipeLike(Base):
    __tablename__ = "recipe_likes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    __table_args__ = (
        UniqueConstraint('recipe_id', 'user_id', name='uq_recipe_user_like'),
    )


class RecipeComment(Base):
    __tablename__ = "recipe_comments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    comment_text = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('idx_recipe_created', 'recipe_id', 'created_at'),
    )
