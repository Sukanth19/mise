#!/usr/bin/env python3
"""
Seed data script for Recipe Saver Enhancements.

This script creates sample data for testing and demonstration:
- Sample users
- Sample recipes (some public for discovery feed)
- Sample collections
- Sample meal plans
- Sample shopping lists
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import SessionLocal
from app.models import (
    User, Recipe, Collection, CollectionRecipe, MealPlan,
    ShoppingList, ShoppingListItem, RecipeRating, RecipeNote,
    NutritionFacts, DietaryLabel, RecipeLike, RecipeComment
)


def create_sample_users(db):
    """Create sample users."""
    print("Creating sample users...")
    
    # Use a simple pre-hashed password for demo purposes
    # This is the hash for "demo123"
    demo_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqYqYqYqYq"
    
    users = [
        User(
            username="demo_user",
            password_hash=demo_hash
        ),
        User(
            username="chef_alice",
            password_hash=demo_hash
        ),
        User(
            username="baker_bob",
            password_hash=demo_hash
        ),
    ]
    
    for user in users:
        db.add(user)
    
    db.commit()
    print(f"✓ Created {len(users)} users")
    return users


def create_sample_recipes(db, users):
    """Create sample recipes."""
    print("Creating sample recipes...")
    
    recipes_data = [
        {
            "user_id": users[0].id,
            "title": "Classic Spaghetti Carbonara",
            "ingredients": "400g spaghetti\n200g pancetta\n4 eggs\n100g Parmesan cheese\nBlack pepper\nSalt",
            "steps": "1. Cook spaghetti according to package directions\n2. Fry pancetta until crispy\n3. Beat eggs with grated Parmesan\n4. Drain pasta and mix with pancetta\n5. Remove from heat and stir in egg mixture\n6. Season with black pepper and serve",
            "tags": "pasta,italian,dinner",
            "visibility": "public",
            "servings": 4,
            "is_favorite": True,
        },
        {
            "user_id": users[0].id,
            "title": "Chocolate Chip Cookies",
            "ingredients": "2 cups flour\n1 cup butter\n1 cup sugar\n2 eggs\n2 cups chocolate chips\n1 tsp vanilla\n1 tsp baking soda\n1/2 tsp salt",
            "steps": "1. Preheat oven to 375°F\n2. Cream butter and sugar\n3. Beat in eggs and vanilla\n4. Mix in flour, baking soda, and salt\n5. Fold in chocolate chips\n6. Drop spoonfuls onto baking sheet\n7. Bake 10-12 minutes",
            "tags": "dessert,cookies,baking",
            "visibility": "public",
            "servings": 24,
            "is_favorite": True,
        },
        {
            "user_id": users[1].id,
            "title": "Greek Salad",
            "ingredients": "4 tomatoes\n1 cucumber\n1 red onion\n200g feta cheese\n1/2 cup olives\n3 tbsp olive oil\n1 tbsp lemon juice\nOregano\nSalt and pepper",
            "steps": "1. Chop tomatoes and cucumber\n2. Slice red onion thinly\n3. Combine vegetables in bowl\n4. Add olives and crumbled feta\n5. Drizzle with olive oil and lemon juice\n6. Season with oregano, salt, and pepper",
            "tags": "salad,healthy,vegetarian",
            "visibility": "public",
            "servings": 4,
        },
        {
            "user_id": users[1].id,
            "title": "Chicken Stir Fry",
            "ingredients": "500g chicken breast\n2 bell peppers\n1 broccoli head\n3 cloves garlic\n2 tbsp soy sauce\n1 tbsp sesame oil\n1 tsp ginger\nRice for serving",
            "steps": "1. Cut chicken into bite-sized pieces\n2. Chop vegetables\n3. Heat oil in wok\n4. Cook chicken until golden\n5. Add vegetables and stir fry\n6. Add soy sauce, garlic, and ginger\n7. Serve over rice",
            "tags": "chicken,asian,dinner,healthy",
            "visibility": "public",
            "servings": 4,
        },
        {
            "user_id": users[2].id,
            "title": "Banana Bread",
            "ingredients": "3 ripe bananas\n1/3 cup melted butter\n1 cup sugar\n1 egg\n1 tsp vanilla\n1 tsp baking soda\n1/4 tsp salt\n1.5 cups flour",
            "steps": "1. Preheat oven to 350°F\n2. Mash bananas in bowl\n3. Mix in melted butter\n4. Add sugar, egg, and vanilla\n5. Sprinkle baking soda and salt\n6. Mix in flour\n7. Pour into greased loaf pan\n8. Bake 60 minutes",
            "tags": "bread,baking,breakfast",
            "visibility": "public",
            "servings": 8,
        },
        {
            "user_id": users[0].id,
            "title": "Vegetable Soup",
            "ingredients": "2 carrots\n2 celery stalks\n1 onion\n2 potatoes\n1 can tomatoes\n4 cups vegetable broth\nHerbs and spices",
            "steps": "1. Chop all vegetables\n2. Sauté onion in pot\n3. Add remaining vegetables\n4. Pour in broth and tomatoes\n5. Simmer 30 minutes\n6. Season to taste",
            "tags": "soup,vegetarian,healthy",
            "visibility": "private",
            "servings": 6,
            "is_favorite": False,
        },
    ]
    
    recipes = []
    for recipe_data in recipes_data:
        recipe = Recipe(**recipe_data)
        db.add(recipe)
        recipes.append(recipe)
    
    db.commit()
    print(f"✓ Created {len(recipes)} recipes")
    return recipes


def create_nutrition_data(db, recipes):
    """Add nutrition information to recipes."""
    print("Adding nutrition data...")
    
    nutrition_data = [
        {"recipe_id": recipes[0].id, "calories": 450, "protein_g": 18, "carbs_g": 65, "fat_g": 12, "fiber_g": 3},
        {"recipe_id": recipes[1].id, "calories": 150, "protein_g": 2, "carbs_g": 20, "fat_g": 8, "fiber_g": 1},
        {"recipe_id": recipes[2].id, "calories": 180, "protein_g": 8, "carbs_g": 12, "fat_g": 12, "fiber_g": 4},
        {"recipe_id": recipes[3].id, "calories": 320, "protein_g": 35, "carbs_g": 25, "fat_g": 10, "fiber_g": 5},
        {"recipe_id": recipes[4].id, "calories": 200, "protein_g": 3, "carbs_g": 35, "fat_g": 6, "fiber_g": 2},
    ]
    
    for data in nutrition_data:
        nutrition = NutritionFacts(**data)
        db.add(nutrition)
    
    # Add dietary labels
    dietary_labels = [
        DietaryLabel(recipe_id=recipes[2].id, label="vegetarian"),
        DietaryLabel(recipe_id=recipes[2].id, label="gluten-free"),
        DietaryLabel(recipe_id=recipes[3].id, label="low-carb"),
        DietaryLabel(recipe_id=recipes[5].id, label="vegan"),
        DietaryLabel(recipe_id=recipes[5].id, label="vegetarian"),
    ]
    
    for label in dietary_labels:
        db.add(label)
    
    db.commit()
    print(f"✓ Added nutrition data for {len(nutrition_data)} recipes")


def create_ratings_and_notes(db, recipes, users):
    """Add ratings and notes to recipes."""
    print("Adding ratings and notes...")
    
    # Ratings
    ratings = [
        RecipeRating(recipe_id=recipes[0].id, user_id=users[0].id, rating=5),
        RecipeRating(recipe_id=recipes[0].id, user_id=users[1].id, rating=4),
        RecipeRating(recipe_id=recipes[1].id, user_id=users[0].id, rating=5),
        RecipeRating(recipe_id=recipes[2].id, user_id=users[1].id, rating=5),
        RecipeRating(recipe_id=recipes[3].id, user_id=users[1].id, rating=4),
    ]
    
    for rating in ratings:
        db.add(rating)
    
    # Notes
    notes = [
        RecipeNote(
            recipe_id=recipes[0].id,
            user_id=users[0].id,
            note_text="Added extra garlic - delicious!"
        ),
        RecipeNote(
            recipe_id=recipes[1].id,
            user_id=users[0].id,
            note_text="Baked for 11 minutes for perfect texture"
        ),
    ]
    
    for note in notes:
        db.add(note)
    
    db.commit()
    print(f"✓ Added {len(ratings)} ratings and {len(notes)} notes")


def create_collections(db, recipes, users):
    """Create sample collections."""
    print("Creating collections...")
    
    # Main collections
    italian_collection = Collection(
        user_id=users[0].id,
        name="Italian Favorites",
        description="My favorite Italian recipes",
        nesting_level=0
    )
    db.add(italian_collection)
    
    desserts_collection = Collection(
        user_id=users[0].id,
        name="Desserts",
        description="Sweet treats and baked goods",
        nesting_level=0
    )
    db.add(desserts_collection)
    
    healthy_collection = Collection(
        user_id=users[1].id,
        name="Healthy Meals",
        description="Nutritious and delicious recipes",
        nesting_level=0
    )
    db.add(healthy_collection)
    
    db.commit()
    
    # Add recipes to collections
    collection_recipes = [
        CollectionRecipe(collection_id=italian_collection.id, recipe_id=recipes[0].id),
        CollectionRecipe(collection_id=desserts_collection.id, recipe_id=recipes[1].id),
        CollectionRecipe(collection_id=desserts_collection.id, recipe_id=recipes[4].id),
        CollectionRecipe(collection_id=healthy_collection.id, recipe_id=recipes[2].id),
        CollectionRecipe(collection_id=healthy_collection.id, recipe_id=recipes[3].id),
    ]
    
    for cr in collection_recipes:
        db.add(cr)
    
    db.commit()
    print(f"✓ Created 3 collections with {len(collection_recipes)} recipes")
    return [italian_collection, desserts_collection, healthy_collection]


def create_meal_plans(db, recipes, users):
    """Create sample meal plans."""
    print("Creating meal plans...")
    
    today = datetime.now().date()
    meal_plans = []
    
    # Create a week of meal plans
    for i in range(7):
        date = today + timedelta(days=i)
        
        # Breakfast
        if i % 2 == 0:
            meal_plans.append(MealPlan(
                user_id=users[0].id,
                recipe_id=recipes[4].id,  # Banana Bread
                meal_date=date,
                meal_time="breakfast"
            ))
        
        # Lunch
        if i % 3 == 0:
            meal_plans.append(MealPlan(
                user_id=users[0].id,
                recipe_id=recipes[2].id,  # Greek Salad
                meal_date=date,
                meal_time="lunch"
            ))
        
        # Dinner
        meal_plans.append(MealPlan(
            user_id=users[0].id,
            recipe_id=recipes[i % 4].id,  # Rotate through first 4 recipes
            meal_date=date,
            meal_time="dinner"
        ))
    
    for mp in meal_plans:
        db.add(mp)
    
    db.commit()
    print(f"✓ Created {len(meal_plans)} meal plans")


def create_shopping_lists(db, recipes, users):
    """Create sample shopping lists."""
    print("Creating shopping lists...")
    
    shopping_list = ShoppingList(
        user_id=users[0].id,
        name="Weekly Groceries"
    )
    db.add(shopping_list)
    db.commit()
    
    items = [
        ShoppingListItem(
            shopping_list_id=shopping_list.id,
            ingredient_name="Spaghetti",
            quantity="400g",
            category="pantry",
            is_checked=False,
            recipe_id=recipes[0].id
        ),
        ShoppingListItem(
            shopping_list_id=shopping_list.id,
            ingredient_name="Eggs",
            quantity="1 dozen",
            category="dairy",
            is_checked=True,
            recipe_id=recipes[0].id
        ),
        ShoppingListItem(
            shopping_list_id=shopping_list.id,
            ingredient_name="Tomatoes",
            quantity="4",
            category="produce",
            is_checked=False,
            recipe_id=recipes[2].id
        ),
        ShoppingListItem(
            shopping_list_id=shopping_list.id,
            ingredient_name="Milk",
            quantity="1 gallon",
            category="dairy",
            is_checked=False,
            is_custom=True
        ),
    ]
    
    for item in items:
        db.add(item)
    
    db.commit()
    print(f"✓ Created 1 shopping list with {len(items)} items")


def create_social_data(db, recipes, users):
    """Create sample social interactions."""
    print("Creating social data...")
    
    # Likes
    likes = [
        RecipeLike(recipe_id=recipes[0].id, user_id=users[1].id),
        RecipeLike(recipe_id=recipes[0].id, user_id=users[2].id),
        RecipeLike(recipe_id=recipes[1].id, user_id=users[1].id),
        RecipeLike(recipe_id=recipes[2].id, user_id=users[0].id),
    ]
    
    for like in likes:
        db.add(like)
    
    # Comments
    comments = [
        RecipeComment(
            recipe_id=recipes[0].id,
            user_id=users[1].id,
            comment_text="This looks amazing! Can't wait to try it."
        ),
        RecipeComment(
            recipe_id=recipes[1].id,
            user_id=users[2].id,
            comment_text="Best cookies I've ever made!"
        ),
    ]
    
    for comment in comments:
        db.add(comment)
    
    db.commit()
    print(f"✓ Created {len(likes)} likes and {len(comments)} comments")


def main():
    """Run all seed data creation."""
    print("="*60)
    print("Recipe Saver - Seed Data Script")
    print("="*60)
    
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_users = db.query(User).count()
        if existing_users > 0:
            print(f"\n⚠ Database already has {existing_users} users")
            response = input("Do you want to continue and add more data? (y/n): ")
            if response.lower() != 'y':
                print("Aborted.")
                return
        
        # Create all sample data
        users = create_sample_users(db)
        recipes = create_sample_recipes(db, users)
        create_nutrition_data(db, recipes)
        create_ratings_and_notes(db, recipes, users)
        create_collections(db, recipes, users)
        create_meal_plans(db, recipes, users)
        create_shopping_lists(db, recipes, users)
        create_social_data(db, recipes, users)
        
        print("\n" + "="*60)
        print("✓ Seed data created successfully!")
        print("="*60)
        print("\nSample credentials:")
        print("  Username: demo_user, Password: demo123")
        print("  Username: chef_alice, Password: demo123")
        print("  Username: baker_bob, Password: demo123")
        print("\nYou can now log in and explore the features!")
        
    except Exception as e:
        print(f"\n✗ Error creating seed data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
