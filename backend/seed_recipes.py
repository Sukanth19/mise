"""
Seed script to add filler recipes to the database
"""
from app.database import SessionLocal
from app.models import User, Recipe
from datetime import datetime
import random
import json

# Sample recipe data
RECIPES = [
    {
        "title": "Classic Spaghetti Carbonara",
        "ingredients": ["400g spaghetti", "200g pancetta", "4 eggs", "100g parmesan", "Black pepper", "Salt"],
        "steps": ["Boil pasta", "Fry pancetta", "Mix eggs and cheese", "Combine all", "Serve hot"],
        "tags": ["italian", "pasta", "quick"],
        "servings": 4,
        "visibility": "public"
    },
    {
        "title": "Chicken Tikka Masala",
        "ingredients": ["500g chicken", "Yogurt", "Tomato sauce", "Cream", "Garam masala", "Garlic", "Ginger"],
        "steps": ["Marinate chicken", "Grill chicken", "Make sauce", "Combine", "Simmer 20 mins"],
        "tags": ["indian", "curry", "spicy"],
        "servings": 4,
        "visibility": "public"
    },
    {
        "title": "Caesar Salad",
        "ingredients": ["Romaine lettuce", "Croutons", "Parmesan", "Caesar dressing", "Anchovies"],
        "steps": ["Wash lettuce", "Make dressing", "Toss ingredients", "Add croutons", "Serve"],
        "tags": ["salad", "healthy", "quick"],
        "servings": 2,
        "visibility": "public"
    },
    {
        "title": "Beef Tacos",
        "ingredients": ["Ground beef", "Taco shells", "Lettuce", "Tomatoes", "Cheese", "Sour cream", "Salsa"],
        "steps": ["Brown beef", "Season meat", "Warm shells", "Assemble tacos", "Add toppings"],
        "tags": ["mexican", "quick", "dinner"],
        "servings": 4,
        "visibility": "public"
    },
    {
        "title": "Margherita Pizza",
        "ingredients": ["Pizza dough", "Tomato sauce", "Mozzarella", "Fresh basil", "Olive oil"],
        "steps": ["Roll dough", "Add sauce", "Add cheese", "Bake at 450°F", "Add basil"],
        "tags": ["italian", "pizza", "vegetarian"],
        "servings": 2,
        "visibility": "public"
    },
    {
        "title": "Chocolate Chip Cookies",
        "ingredients": ["Flour", "Butter", "Sugar", "Eggs", "Chocolate chips", "Vanilla", "Baking soda"],
        "steps": ["Mix dry ingredients", "Cream butter and sugar", "Add eggs", "Fold in chips", "Bake 12 mins"],
        "tags": ["dessert", "baking", "sweet"],
        "servings": 24,
        "visibility": "public"
    },
    {
        "title": "Greek Salad",
        "ingredients": ["Tomatoes", "Cucumber", "Feta cheese", "Olives", "Red onion", "Olive oil", "Oregano"],
        "steps": ["Chop vegetables", "Add feta and olives", "Dress with oil", "Season", "Serve"],
        "tags": ["salad", "greek", "healthy", "vegetarian"],
        "servings": 4,
        "visibility": "public"
    },
    {
        "title": "Pad Thai",
        "ingredients": ["Rice noodles", "Shrimp", "Eggs", "Bean sprouts", "Peanuts", "Tamarind", "Fish sauce"],
        "steps": ["Soak noodles", "Stir-fry shrimp", "Add noodles", "Add sauce", "Garnish"],
        "tags": ["thai", "noodles", "asian"],
        "servings": 2,
        "visibility": "public"
    },
    {
        "title": "French Onion Soup",
        "ingredients": ["Onions", "Beef broth", "Butter", "Gruyere cheese", "Baguette", "Thyme"],
        "steps": ["Caramelize onions", "Add broth", "Simmer 30 mins", "Toast bread", "Top with cheese and broil"],
        "tags": ["french", "soup", "comfort"],
        "servings": 4,
        "visibility": "public"
    },
    {
        "title": "Banana Bread",
        "ingredients": ["Bananas", "Flour", "Sugar", "Eggs", "Butter", "Baking soda", "Vanilla"],
        "steps": ["Mash bananas", "Mix wet ingredients", "Add dry ingredients", "Pour in pan", "Bake 60 mins"],
        "tags": ["baking", "dessert", "breakfast"],
        "servings": 8,
        "visibility": "public"
    },
    {
        "title": "Chicken Stir Fry",
        "ingredients": ["Chicken breast", "Mixed vegetables", "Soy sauce", "Garlic", "Ginger", "Rice"],
        "steps": ["Cut chicken", "Stir-fry chicken", "Add vegetables", "Add sauce", "Serve over rice"],
        "tags": ["asian", "quick", "healthy"],
        "servings": 4,
        "visibility": "public"
    },
    {
        "title": "Caprese Salad",
        "ingredients": ["Tomatoes", "Mozzarella", "Basil", "Olive oil", "Balsamic vinegar", "Salt"],
        "steps": ["Slice tomatoes and mozzarella", "Arrange on plate", "Add basil", "Drizzle oil", "Season"],
        "tags": ["italian", "salad", "vegetarian", "quick"],
        "servings": 2,
        "visibility": "public"
    },
    {
        "title": "Beef Burgers",
        "ingredients": ["Ground beef", "Burger buns", "Lettuce", "Tomato", "Onion", "Cheese", "Pickles"],
        "steps": ["Form patties", "Season beef", "Grill burgers", "Toast buns", "Assemble"],
        "tags": ["american", "grilling", "dinner"],
        "servings": 4,
        "visibility": "public"
    },
    {
        "title": "Vegetable Curry",
        "ingredients": ["Mixed vegetables", "Coconut milk", "Curry paste", "Rice", "Garlic", "Ginger"],
        "steps": ["Sauté aromatics", "Add vegetables", "Add curry paste", "Add coconut milk", "Simmer"],
        "tags": ["indian", "vegetarian", "curry", "healthy"],
        "servings": 4,
        "visibility": "public"
    },
    {
        "title": "Pancakes",
        "ingredients": ["Flour", "Milk", "Eggs", "Sugar", "Baking powder", "Butter", "Maple syrup"],
        "steps": ["Mix dry ingredients", "Add wet ingredients", "Heat griddle", "Pour batter", "Flip and serve"],
        "tags": ["breakfast", "quick", "sweet"],
        "servings": 4,
        "visibility": "public"
    }
]

def seed_recipes():
    db = SessionLocal()
    try:
        # Get the first user (or create one if none exists)
        user = db.query(User).first()
        
        if not user:
            print("No users found. Creating a default user...")
            user = User(
                username="demo",
                email="demo@example.com",
                hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/1jrYK"  # password: demo123
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"Created demo user (username: demo, password: demo123)")
        
        # Check if recipes already exist
        existing_count = db.query(Recipe).count()
        if existing_count > 0:
            print(f"Database already has {existing_count} recipes. Adding more...")
        
        # Add recipes
        print(f"\nAdding {len(RECIPES)} recipes...")
        for recipe_data in RECIPES:
            recipe = Recipe(
                user_id=user.id,
                title=recipe_data["title"],
                ingredients=json.dumps(recipe_data["ingredients"]),
                steps=json.dumps(recipe_data["steps"]),
                tags=json.dumps(recipe_data["tags"]),
                servings=recipe_data["servings"],
                visibility=recipe_data["visibility"],
                is_favorite=random.choice([True, False]),
                created_at=datetime.utcnow()
            )
            db.add(recipe)
            print(f"  ✓ Added: {recipe_data['title']}")
        
        db.commit()
        print(f"\n✅ Successfully added {len(RECIPES)} recipes!")
        print(f"User ID: {user.id} (username: {user.username})")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🍳 Recipe Seeder")
    print("=" * 50)
    seed_recipes()
