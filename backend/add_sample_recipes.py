#!/usr/bin/env python3
"""
Script to add sample recipes to the database.

This script creates a demo user and adds 10 diverse sample recipes including:
- Classic Margherita Pizza
- Chicken Tikka Masala
- Avocado Toast with Poached Egg
- Beef Tacos
- Caesar Salad
- Chocolate Chip Cookies
- Greek Salad
- Pad Thai
- Banana Bread
- Caprese Salad

Usage:
    cd backend
    source venv/bin/activate  # On Windows: venv\\Scripts\\activate
    python add_sample_recipes.py

Login credentials after running:
    Username: demo
    Password: demo1234

The script is idempotent - it won't duplicate recipes if run multiple times.
"""
import json
import sys
from pathlib import Path

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Base, User, Recipe
import bcrypt

# Sample recipes data
SAMPLE_RECIPES = [
    {
        "title": "Classic Margherita Pizza",
        "ingredients": [
            "1 pizza dough ball",
            "1/2 cup tomato sauce",
            "8 oz fresh mozzarella cheese, sliced",
            "Fresh basil leaves",
            "2 tbsp olive oil",
            "Salt to taste"
        ],
        "steps": [
            "Preheat oven to 475°F (245°C) with a pizza stone if available",
            "Roll out pizza dough on a floured surface to desired thickness",
            "Spread tomato sauce evenly over the dough, leaving a 1-inch border",
            "Arrange mozzarella slices on top of the sauce",
            "Drizzle with olive oil and sprinkle with salt",
            "Bake for 12-15 minutes until crust is golden and cheese is bubbly",
            "Remove from oven and top with fresh basil leaves",
            "Slice and serve hot"
        ],
        "tags": ["Italian", "Pizza", "Vegetarian", "Quick"],
        "image_url": None,
        "reference_link": None
    },
    {
        "title": "Chicken Tikka Masala",
        "ingredients": [
            "1.5 lbs chicken breast, cubed",
            "1 cup plain yogurt",
            "2 tbsp tikka masala spice blend",
            "1 onion, diced",
            "4 cloves garlic, minced",
            "1 tbsp ginger, grated",
            "1 can (14 oz) crushed tomatoes",
            "1 cup heavy cream",
            "2 tbsp butter",
            "Fresh cilantro for garnish",
            "Salt to taste"
        ],
        "steps": [
            "Marinate chicken in yogurt and half the spice blend for 30 minutes",
            "Heat butter in a large pan over medium-high heat",
            "Cook chicken until browned, then remove and set aside",
            "In the same pan, sauté onion until soft, about 5 minutes",
            "Add garlic and ginger, cook for 1 minute",
            "Stir in remaining spices and cook for 30 seconds",
            "Add crushed tomatoes and simmer for 10 minutes",
            "Return chicken to pan, add cream, and simmer for 15 minutes",
            "Garnish with cilantro and serve with rice or naan"
        ],
        "tags": ["Indian", "Chicken", "Curry", "Dinner"],
        "image_url": None,
        "reference_link": None
    },
    {
        "title": "Avocado Toast with Poached Egg",
        "ingredients": [
            "2 slices sourdough bread",
            "1 ripe avocado",
            "2 eggs",
            "1 tbsp white vinegar",
            "Red pepper flakes",
            "Salt and black pepper",
            "Olive oil",
            "Fresh herbs (optional)"
        ],
        "steps": [
            "Toast bread until golden and crispy",
            "Bring a pot of water to a gentle simmer, add vinegar",
            "Crack eggs into small bowls",
            "Create a gentle whirlpool in the water and slide eggs in",
            "Poach for 3-4 minutes until whites are set",
            "Meanwhile, mash avocado with salt, pepper, and olive oil",
            "Spread avocado mixture on toasted bread",
            "Top with poached eggs",
            "Sprinkle with red pepper flakes and fresh herbs",
            "Serve immediately"
        ],
        "tags": ["Breakfast", "Healthy", "Quick", "Vegetarian"],
        "image_url": None,
        "reference_link": None
    },
    {
        "title": "Beef Tacos",
        "ingredients": [
            "1 lb ground beef",
            "1 packet taco seasoning",
            "8 taco shells",
            "1 cup shredded lettuce",
            "1 cup diced tomatoes",
            "1 cup shredded cheddar cheese",
            "1/2 cup sour cream",
            "1/4 cup diced onions",
            "Salsa",
            "Lime wedges"
        ],
        "steps": [
            "Brown ground beef in a large skillet over medium-high heat",
            "Drain excess fat",
            "Add taco seasoning and water according to package directions",
            "Simmer for 5 minutes until sauce thickens",
            "Warm taco shells according to package directions",
            "Fill shells with seasoned beef",
            "Top with lettuce, tomatoes, cheese, sour cream, and onions",
            "Serve with salsa and lime wedges"
        ],
        "tags": ["Mexican", "Beef", "Quick", "Dinner"],
        "image_url": None,
        "reference_link": None
    },
    {
        "title": "Caesar Salad",
        "ingredients": [
            "1 large head romaine lettuce, chopped",
            "1/2 cup Caesar dressing",
            "1/2 cup grated Parmesan cheese",
            "1 cup croutons",
            "2 anchovy fillets (optional)",
            "Black pepper to taste",
            "Lemon wedges"
        ],
        "steps": [
            "Wash and thoroughly dry romaine lettuce",
            "Chop lettuce into bite-sized pieces",
            "Place lettuce in a large bowl",
            "Add Caesar dressing and toss to coat evenly",
            "Add Parmesan cheese and toss again",
            "Top with croutons",
            "Add anchovy fillets if desired",
            "Finish with freshly ground black pepper",
            "Serve with lemon wedges"
        ],
        "tags": ["Salad", "Side Dish", "Quick", "Vegetarian"],
        "image_url": None,
        "reference_link": None
    },
    {
        "title": "Chocolate Chip Cookies",
        "ingredients": [
            "2 1/4 cups all-purpose flour",
            "1 tsp baking soda",
            "1 tsp salt",
            "1 cup butter, softened",
            "3/4 cup granulated sugar",
            "3/4 cup brown sugar",
            "2 large eggs",
            "2 tsp vanilla extract",
            "2 cups chocolate chips"
        ],
        "steps": [
            "Preheat oven to 375°F (190°C)",
            "Mix flour, baking soda, and salt in a bowl",
            "In another bowl, cream butter and both sugars until fluffy",
            "Beat in eggs and vanilla",
            "Gradually stir in flour mixture",
            "Fold in chocolate chips",
            "Drop rounded tablespoons of dough onto ungreased baking sheets",
            "Bake for 9-11 minutes until golden brown",
            "Cool on baking sheet for 2 minutes, then transfer to wire rack",
            "Enjoy warm or store in airtight container"
        ],
        "tags": ["Dessert", "Baking", "Cookies", "Sweet"],
        "image_url": None,
        "reference_link": None
    },
    {
        "title": "Greek Salad",
        "ingredients": [
            "4 large tomatoes, cut into wedges",
            "1 cucumber, sliced",
            "1 red onion, thinly sliced",
            "1 green bell pepper, chopped",
            "1 cup Kalamata olives",
            "8 oz feta cheese, cubed",
            "1/4 cup olive oil",
            "2 tbsp red wine vinegar",
            "1 tsp dried oregano",
            "Salt and pepper to taste"
        ],
        "steps": [
            "Combine tomatoes, cucumber, onion, and bell pepper in a large bowl",
            "Add Kalamata olives",
            "In a small bowl, whisk together olive oil, vinegar, oregano, salt, and pepper",
            "Pour dressing over vegetables and toss gently",
            "Top with feta cheese cubes",
            "Let sit for 10 minutes to allow flavors to meld",
            "Serve at room temperature"
        ],
        "tags": ["Greek", "Salad", "Healthy", "Vegetarian"],
        "image_url": None,
        "reference_link": None
    },
    {
        "title": "Pad Thai",
        "ingredients": [
            "8 oz rice noodles",
            "2 tbsp vegetable oil",
            "2 cloves garlic, minced",
            "8 oz shrimp or chicken",
            "2 eggs, beaten",
            "3 tbsp fish sauce",
            "2 tbsp tamarind paste",
            "2 tbsp brown sugar",
            "1 cup bean sprouts",
            "3 green onions, chopped",
            "1/4 cup peanuts, crushed",
            "Lime wedges",
            "Fresh cilantro"
        ],
        "steps": [
            "Soak rice noodles in warm water for 30 minutes, then drain",
            "Heat oil in a wok or large pan over high heat",
            "Add garlic and protein, cook until done",
            "Push to one side, add eggs and scramble",
            "Add noodles, fish sauce, tamarind paste, and sugar",
            "Toss everything together for 2-3 minutes",
            "Add bean sprouts and green onions, toss briefly",
            "Serve topped with crushed peanuts, lime wedges, and cilantro"
        ],
        "tags": ["Thai", "Noodles", "Asian", "Dinner"],
        "image_url": None,
        "reference_link": None
    },
    {
        "title": "Banana Bread",
        "ingredients": [
            "3 ripe bananas, mashed",
            "1/3 cup melted butter",
            "3/4 cup sugar",
            "1 egg, beaten",
            "1 tsp vanilla extract",
            "1 tsp baking soda",
            "Pinch of salt",
            "1 1/2 cups all-purpose flour",
            "1/2 cup chopped walnuts (optional)"
        ],
        "steps": [
            "Preheat oven to 350°F (175°C)",
            "Grease a 9x5 inch loaf pan",
            "In a mixing bowl, mash bananas with a fork",
            "Mix in melted butter",
            "Stir in sugar, egg, and vanilla",
            "Sprinkle baking soda and salt over mixture and mix",
            "Add flour and stir until just combined",
            "Fold in walnuts if using",
            "Pour batter into prepared loaf pan",
            "Bake for 60-65 minutes until a toothpick comes out clean",
            "Cool in pan for 10 minutes, then turn out onto wire rack"
        ],
        "tags": ["Baking", "Dessert", "Breakfast", "Sweet"],
        "image_url": None,
        "reference_link": None
    },
    {
        "title": "Caprese Salad",
        "ingredients": [
            "4 large ripe tomatoes, sliced",
            "16 oz fresh mozzarella, sliced",
            "Fresh basil leaves",
            "3 tbsp extra virgin olive oil",
            "2 tbsp balsamic vinegar",
            "Salt and pepper to taste"
        ],
        "steps": [
            "Arrange tomato and mozzarella slices alternating on a platter",
            "Tuck basil leaves between slices",
            "Drizzle with olive oil and balsamic vinegar",
            "Season with salt and freshly ground black pepper",
            "Let sit for 5 minutes before serving",
            "Serve at room temperature"
        ],
        "tags": ["Italian", "Salad", "Quick", "Vegetarian"],
        "image_url": None,
        "reference_link": None
    }
]


def hash_password(password: str) -> str:
    """Hash a plain text password using bcrypt."""
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def get_or_create_demo_user(db: Session) -> User:
    """Get or create a demo user for the sample recipes."""
    demo_user = db.query(User).filter(User.username == "demo").first()
    
    if not demo_user:
        print("Creating demo user...")
        demo_user = User(
            username="demo",
            password_hash=hash_password("demo1234")
        )
        db.add(demo_user)
        db.commit()
        db.refresh(demo_user)
        print(f"✓ Demo user created (username: demo, password: demo1234)")
    else:
        print(f"✓ Demo user already exists (ID: {demo_user.id})")
    
    return demo_user


def add_sample_recipes(db: Session, user: User):
    """Add sample recipes to the database."""
    print(f"\nAdding sample recipes for user '{user.username}'...")
    
    # Check how many recipes already exist
    existing_count = db.query(Recipe).filter(Recipe.user_id == user.id).count()
    print(f"User currently has {existing_count} recipes")
    
    added_count = 0
    for recipe_data in SAMPLE_RECIPES:
        # Check if recipe with this title already exists for this user
        existing = db.query(Recipe).filter(
            Recipe.user_id == user.id,
            Recipe.title == recipe_data["title"]
        ).first()
        
        if existing:
            print(f"  ⊘ Skipping '{recipe_data['title']}' (already exists)")
            continue
        
        # Create new recipe
        recipe = Recipe(
            user_id=user.id,
            title=recipe_data["title"],
            ingredients=json.dumps(recipe_data["ingredients"]),
            steps=json.dumps(recipe_data["steps"]),
            tags=json.dumps(recipe_data["tags"]) if recipe_data["tags"] else None,
            image_url=recipe_data.get("image_url"),
            reference_link=recipe_data.get("reference_link"),
            is_favorite=False,
            visibility='private',
            servings=4
        )
        
        db.add(recipe)
        added_count += 1
        print(f"  ✓ Added '{recipe_data['title']}'")
    
    db.commit()
    print(f"\n✓ Successfully added {added_count} new recipes!")
    print(f"✓ Total recipes for user: {existing_count + added_count}")


def main():
    """Main function to run the script."""
    print("=" * 60)
    print("Sample Recipe Importer")
    print("=" * 60)
    
    # Create tables if they don't exist
    print("\nEnsuring database tables exist...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables ready")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Get or create demo user
        user = get_or_create_demo_user(db)
        
        # Add sample recipes
        add_sample_recipes(db, user)
        
        print("\n" + "=" * 60)
        print("Done! You can now log in with:")
        print("  Username: demo")
        print("  Password: demo1234")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
