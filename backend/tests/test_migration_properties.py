"""Property-based tests for MySQL migration script."""
import os
os.environ["DATABASE_URL"] = "sqlite:///./test_migration.db"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing"

from hypothesis import given, strategies as st, settings as hyp_settings, HealthCheck
from datetime import timedelta
import pytest
import uuid
import json
import sys
import tempfile
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add parent directory to path to import migrate_to_mysql
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from migrate_to_mysql import DatabaseMigrator
from app.database import Base
from app.models import User, Recipe, NutritionFacts, RecipeRating


# Property 10: Migration Record Count Preservation
@given(
    num_users=st.integers(min_value=1, max_value=5),
    num_recipes_per_user=st.integers(min_value=0, max_value=3)
)
@hyp_settings(max_examples=20, deadline=timedelta(milliseconds=10000), suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_migration_record_count_preservation_property(num_users, num_recipes_per_user):
    """
    Property 10: Migration Record Count Preservation
    
    For any source database table, the number of records in the target MySQL 
    table after migration should equal the source count.
    
    **Validates: Requirements 5.2**
    """
    # Create temporary database files
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as source_file:
        source_path = source_file.name
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as target_file:
        target_path = target_file.name
    
    source_url = f"sqlite:///{source_path}"
    target_url = f"sqlite:///{target_path}"
    
    try:
        # Create source database
        source_engine = create_engine(source_url)
        Base.metadata.create_all(bind=source_engine)
        SourceSession = sessionmaker(bind=source_engine)
        source_session = SourceSession()
        
        # Create target database
        target_engine = create_engine(target_url)
        Base.metadata.create_all(bind=target_engine)
        
        # Populate source database
        for i in range(num_users):
            user = User(
                username=f"user_{uuid.uuid4().hex[:8]}",
                password_hash=f"hash_{i}"
            )
            source_session.add(user)
            source_session.flush()
            
            # Add recipes for this user
            for j in range(num_recipes_per_user):
                recipe = Recipe(
                    user_id=user.id,
                    title=f"Recipe {i}_{j}",
                    ingredients=json.dumps(["ingredient1", "ingredient2"]),
                    steps=json.dumps(["step1", "step2"]),
                    visibility="private"
                )
                source_session.add(recipe)
        
        source_session.commit()
        
        # Count records in source
        source_user_count = source_session.query(User).count()
        source_recipe_count = source_session.query(Recipe).count()
        
        # Run migration
        migrator = DatabaseMigrator(
            source_url=source_url,
            target_url=target_url,
            dry_run=False,
            incremental=False
        )
        migrator.connect()
        migrator.migrate_users()
        migrator.migrate_recipes()
        migrator.disconnect()
        
        # Count records in target
        TargetSession = sessionmaker(bind=target_engine)
        target_session = TargetSession()
        target_user_count = target_session.query(User).count()
        target_recipe_count = target_session.query(Recipe).count()
        
        # Verify counts match
        assert target_user_count == source_user_count, \
            f"User count mismatch: source={source_user_count}, target={target_user_count}"
        assert target_recipe_count == source_recipe_count, \
            f"Recipe count mismatch: source={source_recipe_count}, target={target_recipe_count}"
        
        target_session.close()
        source_session.close()
        source_engine.dispose()
        target_engine.dispose()
        
    finally:
        # Clean up test databases
        try:
            os.unlink(source_path)
            os.unlink(target_path)
        except:
            pass


# Property 11: Migration Data Preservation
@given(
    username=st.text(min_size=1, max_size=20, alphabet=st.characters(min_codepoint=97, max_codepoint=122)),
    title=st.text(min_size=1, max_size=50, alphabet=st.characters(min_codepoint=32, max_codepoint=126)),
    num_ingredients=st.integers(min_value=1, max_value=3),
    num_steps=st.integers(min_value=1, max_value=3)
)
@hyp_settings(max_examples=20, deadline=timedelta(milliseconds=10000), suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_migration_data_preservation_property(username, title, num_ingredients, num_steps):
    """
    Property 11: Migration Data Preservation
    
    For any record in the source database, the migrated MySQL record should 
    preserve all field values.
    
    **Validates: Requirements 5.3**
    """
    # Create temporary database files
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as source_file:
        source_path = source_file.name
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as target_file:
        target_path = target_file.name
    
    source_url = f"sqlite:///{source_path}"
    target_url = f"sqlite:///{target_path}"
    
    try:
        # Create source database
        source_engine = create_engine(source_url)
        Base.metadata.create_all(bind=source_engine)
        SourceSession = sessionmaker(bind=source_engine)
        source_session = SourceSession()
        
        # Create target database
        target_engine = create_engine(target_url)
        Base.metadata.create_all(bind=target_engine)
        
        # Create user in source
        user = User(
            username=username,
            password_hash="test_hash_123"
        )
        source_session.add(user)
        source_session.flush()
        
        # Create recipe in source
        ingredients = [f"ingredient_{i}" for i in range(num_ingredients)]
        steps = [f"step_{i}" for i in range(num_steps)]
        
        recipe = Recipe(
            user_id=user.id,
            title=title,
            ingredients=json.dumps(ingredients),
            steps=json.dumps(steps),
            tags=json.dumps(["tag1", "tag2"]),
            reference_link="https://example.com/recipe",
            is_favorite=True,
            visibility="public",
            servings=4
        )
        source_session.add(recipe)
        source_session.commit()
        
        # Run migration
        migrator = DatabaseMigrator(
            source_url=source_url,
            target_url=target_url,
            dry_run=False,
            incremental=False
        )
        migrator.connect()
        migrator.migrate_users()
        migrator.migrate_recipes()
        migrator.disconnect()
        
        # Retrieve migrated data
        TargetSession = sessionmaker(bind=target_engine)
        target_session = TargetSession()
        
        # Find migrated user (may have different ID)
        migrated_user = target_session.query(User).filter(User.username == username).first()
        assert migrated_user is not None, "User should be migrated"
        assert migrated_user.username == username, "Username should be preserved"
        assert migrated_user.password_hash == "test_hash_123", "Password hash should be preserved"
        
        # Find migrated recipe
        migrated_recipe = target_session.query(Recipe).filter(Recipe.title == title).first()
        assert migrated_recipe is not None, "Recipe should be migrated"
        assert migrated_recipe.title == title, "Title should be preserved"
        assert json.loads(migrated_recipe.ingredients) == ingredients, "Ingredients should be preserved"
        assert json.loads(migrated_recipe.steps) == steps, "Steps should be preserved"
        assert json.loads(migrated_recipe.tags) == ["tag1", "tag2"], "Tags should be preserved"
        assert migrated_recipe.reference_link == "https://example.com/recipe", "Reference link should be preserved"
        assert migrated_recipe.is_favorite == True, "is_favorite should be preserved"
        assert migrated_recipe.visibility == "public", "Visibility should be preserved"
        assert migrated_recipe.servings == 4, "Servings should be preserved"
        
        target_session.close()
        source_session.close()
        source_engine.dispose()
        target_engine.dispose()
        
    finally:
        # Clean up test databases
        try:
            os.unlink(source_path)
            os.unlink(target_path)
        except:
            pass


# Property 12: Migration Relationship Preservation
@given(
    num_users=st.integers(min_value=2, max_value=3),
    num_recipes_per_user=st.integers(min_value=1, max_value=2)
)
@hyp_settings(max_examples=20, deadline=timedelta(milliseconds=10000), suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_migration_relationship_preservation_property(num_users, num_recipes_per_user):
    """
    Property 12: Migration Relationship Preservation
    
    For any foreign key relationship in the source database, the migrated 
    MySQL records should maintain the relationship.
    
    **Validates: Requirements 5.4**
    """
    # Create temporary database files
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as source_file:
        source_path = source_file.name
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as target_file:
        target_path = target_file.name
    
    source_url = f"sqlite:///{source_path}"
    target_url = f"sqlite:///{target_path}"
    
    try:
        # Create source database
        source_engine = create_engine(source_url)
        Base.metadata.create_all(bind=source_engine)
        SourceSession = sessionmaker(bind=source_engine)
        source_session = SourceSession()
        
        # Create target database
        target_engine = create_engine(target_url)
        Base.metadata.create_all(bind=target_engine)
        
        # Populate source database with users and recipes
        source_relationships = []  # Track (username, recipe_title) pairs
        
        for i in range(num_users):
            username = f"user_{uuid.uuid4().hex[:8]}"
            user = User(
                username=username,
                password_hash=f"hash_{i}"
            )
            source_session.add(user)
            source_session.flush()
            
            for j in range(num_recipes_per_user):
                recipe_title = f"Recipe_{username}_{j}"
                recipe = Recipe(
                    user_id=user.id,
                    title=recipe_title,
                    ingredients=json.dumps(["ingredient1"]),
                    steps=json.dumps(["step1"]),
                    visibility="private"
                )
                source_session.add(recipe)
                source_session.flush()
                
                # Add nutrition facts (one-to-one relationship)
                nutrition = NutritionFacts(
                    recipe_id=recipe.id,
                    calories=500.0,
                    protein_g=20.0,
                    carbs_g=50.0,
                    fat_g=15.0
                )
                source_session.add(nutrition)
                
                source_relationships.append((username, recipe_title))
        
        source_session.commit()
        
        # Run migration
        migrator = DatabaseMigrator(
            source_url=source_url,
            target_url=target_url,
            dry_run=False,
            incremental=False
        )
        migrator.connect()
        migrator.migrate_users()
        migrator.migrate_recipes()
        migrator.migrate_nutrition_facts()
        migrator.disconnect()
        
        # Verify relationships in target
        TargetSession = sessionmaker(bind=target_engine)
        target_session = TargetSession()
        
        for username, recipe_title in source_relationships:
            # Find user
            user = target_session.query(User).filter(User.username == username).first()
            assert user is not None, f"User {username} should be migrated"
            
            # Find recipe
            recipe = target_session.query(Recipe).filter(Recipe.title == recipe_title).first()
            assert recipe is not None, f"Recipe {recipe_title} should be migrated"
            
            # Verify foreign key relationship
            assert recipe.user_id == user.id, \
                f"Recipe {recipe_title} should reference user {username} (user_id mismatch)"
            
            # Verify one-to-one relationship with nutrition facts
            nutrition = target_session.query(NutritionFacts).filter(
                NutritionFacts.recipe_id == recipe.id
            ).first()
            assert nutrition is not None, f"Nutrition facts for recipe {recipe_title} should be migrated"
            assert nutrition.recipe_id == recipe.id, "Nutrition facts should reference correct recipe"
        
        target_session.close()
        source_session.close()
        source_engine.dispose()
        target_engine.dispose()
        
    finally:
        # Clean up test databases
        try:
            os.unlink(source_path)
            os.unlink(target_path)
        except:
            pass


# Property 13: Migration Constraint Preservation
@given(
    username=st.text(min_size=1, max_size=20, alphabet=st.characters(min_codepoint=97, max_codepoint=122)),
    rating=st.integers(min_value=1, max_value=5)
)
@hyp_settings(max_examples=20, deadline=timedelta(milliseconds=10000), suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_migration_constraint_preservation_property(username, rating):
    """
    Property 13: Migration Constraint Preservation
    
    For any constraint in the source database (unique, not null, check), 
    the migrated MySQL schema should enforce the same constraint.
    
    **Validates: Requirements 5.5**
    """
    from sqlalchemy.exc import IntegrityError
    
    # Create temporary database files
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as source_file:
        source_path = source_file.name
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as target_file:
        target_path = target_file.name
    
    source_url = f"sqlite:///{source_path}"
    target_url = f"sqlite:///{target_path}"
    
    try:
        # Create source database
        source_engine = create_engine(source_url)
        Base.metadata.create_all(bind=source_engine)
        SourceSession = sessionmaker(bind=source_engine)
        source_session = SourceSession()
        
        # Create target database
        target_engine = create_engine(target_url)
        Base.metadata.create_all(bind=target_engine)
        
        # Create user and recipe in source
        user = User(
            username=username,
            password_hash="test_hash"
        )
        source_session.add(user)
        source_session.flush()
        
        recipe = Recipe(
            user_id=user.id,
            title="Test Recipe",
            ingredients=json.dumps(["ingredient1"]),
            steps=json.dumps(["step1"]),
            visibility="private"
        )
        source_session.add(recipe)
        source_session.flush()
        
        # Add rating
        rating_obj = RecipeRating(
            recipe_id=recipe.id,
            user_id=user.id,
            rating=rating
        )
        source_session.add(rating_obj)
        source_session.commit()
        
        # Run migration
        migrator = DatabaseMigrator(
            source_url=source_url,
            target_url=target_url,
            dry_run=False,
            incremental=False
        )
        migrator.connect()
        migrator.migrate_users()
        migrator.migrate_recipes()
        migrator.migrate_relationship_table('recipe_ratings', {'recipe_id': 'recipes', 'user_id': 'users'})
        migrator.disconnect()
        
        # Test constraints in target database
        TargetSession = sessionmaker(bind=target_engine)
        target_session = TargetSession()
        
        # Test 1: UNIQUE constraint on username
        duplicate_user = User(
            username=username,  # Same username
            password_hash="different_hash"
        )
        target_session.add(duplicate_user)
        
        with pytest.raises(IntegrityError):
            target_session.commit()
        target_session.rollback()
        
        # Test 2: NOT NULL constraint on required fields
        user_without_username = User(
            username=None,  # NULL username
            password_hash="hash"
        )
        target_session.add(user_without_username)
        
        with pytest.raises(IntegrityError):
            target_session.commit()
        target_session.rollback()
        
        # Test 3: UNIQUE constraint on (recipe_id, user_id) for ratings
        migrated_user = target_session.query(User).filter(User.username == username).first()
        migrated_recipe = target_session.query(Recipe).filter(Recipe.title == "Test Recipe").first()
        
        duplicate_rating = RecipeRating(
            recipe_id=migrated_recipe.id,
            user_id=migrated_user.id,
            rating=3  # Different rating value, but same user+recipe
        )
        target_session.add(duplicate_rating)
        
        with pytest.raises(IntegrityError):
            target_session.commit()
        target_session.rollback()
        
        target_session.close()
        source_session.close()
        source_engine.dispose()
        target_engine.dispose()
        
    finally:
        # Clean up test databases
        try:
            os.unlink(source_path)
            os.unlink(target_path)
        except:
            pass


# Property 21: Reverse Migration Round Trip
@given(
    username=st.text(min_size=1, max_size=20, alphabet=st.characters(min_codepoint=97, max_codepoint=122)),
    title=st.text(min_size=1, max_size=50, alphabet=st.characters(min_codepoint=32, max_codepoint=126)),
    num_ingredients=st.integers(min_value=1, max_value=3),
    num_steps=st.integers(min_value=1, max_value=3),
    servings=st.integers(min_value=1, max_value=10),
    is_favorite=st.booleans()
)
@hyp_settings(max_examples=20, deadline=timedelta(milliseconds=15000), suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_reverse_migration_round_trip_property(username, title, num_ingredients, num_steps, servings, is_favorite):
    """
    Property 21: Reverse Migration Round Trip
    
    For any record in MySQL, reverse migrating to SQLite and then 
    forward migrating back to MySQL should produce an equivalent record.
    
    **Validates: Requirements 12.3**
    """
    from migrate_from_mysql import ReverseDatabaseMigrator
    
    # Create temporary database files
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as mysql_file:
        mysql_path = mysql_file.name
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as intermediate_file:
        intermediate_path = intermediate_file.name
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as final_file:
        final_path = final_file.name
    
    mysql_url = f"sqlite:///{mysql_path}"
    intermediate_url = f"sqlite:///{intermediate_path}"
    final_mysql_url = f"sqlite:///{final_path}"
    
    try:
        # Step 1: Create initial MySQL database with test data
        mysql_engine = create_engine(mysql_url)
        Base.metadata.create_all(bind=mysql_engine)
        MySQLSession = sessionmaker(bind=mysql_engine)
        mysql_session = MySQLSession()
        
        # Create user in MySQL
        user = User(
            username=username,
            password_hash="test_hash_123"
        )
        mysql_session.add(user)
        mysql_session.flush()
        
        # Create recipe in MySQL
        ingredients = [f"ingredient_{i}" for i in range(num_ingredients)]
        steps = [f"step_{i}" for i in range(num_steps)]
        
        recipe = Recipe(
            user_id=user.id,
            title=title,
            ingredients=json.dumps(ingredients),
            steps=json.dumps(steps),
            tags=json.dumps(["tag1", "tag2"]),
            reference_link="https://example.com/recipe",
            is_favorite=is_favorite,
            visibility="public",
            servings=servings
        )
        mysql_session.add(recipe)
        mysql_session.flush()
        
        # Add nutrition facts
        nutrition = NutritionFacts(
            recipe_id=recipe.id,
            calories=500.0,
            protein_g=20.0,
            carbs_g=50.0,
            fat_g=15.0,
            fiber_g=5.0
        )
        mysql_session.add(nutrition)
        mysql_session.commit()
        
        # Store original data for comparison
        original_user_id = user.id
        original_recipe_id = recipe.id
        original_username = user.username
        original_password_hash = user.password_hash
        original_title = recipe.title
        original_ingredients = json.loads(recipe.ingredients)
        original_steps = json.loads(recipe.steps)
        original_tags = json.loads(recipe.tags)
        original_reference_link = recipe.reference_link
        original_is_favorite = recipe.is_favorite
        original_visibility = recipe.visibility
        original_servings = recipe.servings
        original_calories = nutrition.calories
        original_protein = nutrition.protein_g
        original_carbs = nutrition.carbs_g
        original_fat = nutrition.fat_g
        original_fiber = nutrition.fiber_g
        
        mysql_session.close()
        mysql_engine.dispose()
        
        # Step 2: Reverse migrate from MySQL to SQLite
        intermediate_engine = create_engine(intermediate_url)
        Base.metadata.create_all(bind=intermediate_engine)
        intermediate_engine.dispose()
        
        reverse_migrator = ReverseDatabaseMigrator(
            source_url=mysql_url,
            target_url=intermediate_url,
            dry_run=False,
            incremental=False
        )
        reverse_migrator.connect()
        reverse_migrator.migrate_all()
        reverse_migrator.disconnect()
        
        # Step 3: Forward migrate from SQLite back to MySQL
        final_mysql_engine = create_engine(final_mysql_url)
        Base.metadata.create_all(bind=final_mysql_engine)
        final_mysql_engine.dispose()
        
        forward_migrator = DatabaseMigrator(
            source_url=intermediate_url,
            target_url=final_mysql_url,
            dry_run=False,
            incremental=False
        )
        forward_migrator.connect()
        forward_migrator.migrate_all()
        forward_migrator.disconnect()
        
        # Step 4: Verify data equivalence after round trip
        FinalSession = sessionmaker(bind=create_engine(final_mysql_url))
        final_session = FinalSession()
        
        # Find migrated user (may have different ID)
        final_user = final_session.query(User).filter(User.username == original_username).first()
        assert final_user is not None, "User should exist after round trip"
        assert final_user.username == original_username, "Username should be preserved"
        assert final_user.password_hash == original_password_hash, "Password hash should be preserved"
        
        # Find migrated recipe
        final_recipe = final_session.query(Recipe).filter(Recipe.title == original_title).first()
        assert final_recipe is not None, "Recipe should exist after round trip"
        assert final_recipe.title == original_title, "Title should be preserved"
        assert json.loads(final_recipe.ingredients) == original_ingredients, "Ingredients should be preserved"
        assert json.loads(final_recipe.steps) == original_steps, "Steps should be preserved"
        assert json.loads(final_recipe.tags) == original_tags, "Tags should be preserved"
        assert final_recipe.reference_link == original_reference_link, "Reference link should be preserved"
        assert final_recipe.is_favorite == original_is_favorite, "is_favorite should be preserved"
        assert final_recipe.visibility == original_visibility, "Visibility should be preserved"
        assert final_recipe.servings == original_servings, "Servings should be preserved"
        
        # Verify nutrition facts relationship
        final_nutrition = final_session.query(NutritionFacts).filter(
            NutritionFacts.recipe_id == final_recipe.id
        ).first()
        assert final_nutrition is not None, "Nutrition facts should exist after round trip"
        assert final_nutrition.calories == original_calories, "Calories should be preserved"
        assert final_nutrition.protein_g == original_protein, "Protein should be preserved"
        assert final_nutrition.carbs_g == original_carbs, "Carbs should be preserved"
        assert final_nutrition.fat_g == original_fat, "Fat should be preserved"
        assert final_nutrition.fiber_g == original_fiber, "Fiber should be preserved"
        
        final_session.close()
        
    finally:
        # Clean up test databases
        try:
            os.unlink(mysql_path)
            os.unlink(intermediate_path)
            os.unlink(final_path)
        except:
            pass
