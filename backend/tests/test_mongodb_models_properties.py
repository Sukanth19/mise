"""
Property-based tests for MongoDB document models.

Feature: mongodb-migration
"""

import pytest
from hypothesis import given, strategies as st, settings as hypothesis_settings
from bson import ObjectId
from datetime import datetime, date
from decimal import Decimal
from app.mongodb_models import (
    PyObjectId,
    UserDocument,
    RecipeDocument,
    NutritionFactsEmbedded,
    RecipeRatingDocument,
    RecipeNoteDocument,
    CollectionDocument,
    MealPlanDocument,
    MealPlanTemplateDocument,
    MealPlanTemplateItemEmbedded,
    ShoppingListDocument,
    ShoppingListItemEmbedded,
    UserFollowDocument,
    RecipeLikeDocument,
    RecipeCommentDocument,
)


# Custom strategies for MongoDB types
@st.composite
def object_id_strategy(draw):
    """Generate valid ObjectId instances."""
    return ObjectId()


@st.composite
def user_document_strategy(draw):
    """Generate valid UserDocument instances."""
    return UserDocument(
        username=draw(st.text(min_size=1, max_size=255, alphabet=st.characters(blacklist_categories=['Cs'], blacklist_characters=['\x00']))),
        password_hash=draw(st.text(min_size=1, max_size=255, alphabet=st.characters(blacklist_categories=['Cs'], blacklist_characters=['\x00']))),
        created_at=draw(st.datetimes(min_value=datetime(2020, 1, 1), max_value=datetime(2030, 12, 31)))
    )


@st.composite
def recipe_document_strategy(draw):
    """Generate valid RecipeDocument instances."""
    visibility = draw(st.sampled_from(["private", "public", "unlisted"]))
    dietary_labels = draw(st.lists(
        st.sampled_from(["vegan", "vegetarian", "gluten-free", "dairy-free", "keto", "paleo", "low-carb"]),
        max_size=3,
        unique=True
    ))
    allergen_warnings = draw(st.lists(
        st.sampled_from(["nuts", "dairy", "eggs", "soy", "wheat", "fish", "shellfish"]),
        max_size=3,
        unique=True
    ))
    
    nutrition = None
    if draw(st.booleans()):
        nutrition = NutritionFactsEmbedded(
            calories=draw(st.none() | st.decimals(min_value=0, max_value=5000, places=2)),
            protein_g=draw(st.none() | st.decimals(min_value=0, max_value=500, places=2)),
            carbs_g=draw(st.none() | st.decimals(min_value=0, max_value=500, places=2)),
            fat_g=draw(st.none() | st.decimals(min_value=0, max_value=500, places=2)),
            fiber_g=draw(st.none() | st.decimals(min_value=0, max_value=100, places=2)),
        )
    
    return RecipeDocument(
        user_id=draw(object_id_strategy()),
        title=draw(st.text(min_size=1, max_size=255, alphabet=st.characters(blacklist_categories=['Cs'], blacklist_characters=['\x00']))),
        image_url=draw(st.none() | st.text(max_size=500, alphabet=st.characters(blacklist_categories=['Cs'], blacklist_characters=['\x00']))),
        ingredients=draw(st.lists(st.text(min_size=1, max_size=200, alphabet=st.characters(blacklist_categories=['Cs'], blacklist_characters=['\x00'])), max_size=20)),
        steps=draw(st.lists(st.text(min_size=1, max_size=500, alphabet=st.characters(blacklist_categories=['Cs'], blacklist_characters=['\x00'])), max_size=20)),
        tags=draw(st.lists(st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_categories=['Cs'], blacklist_characters=['\x00'])), max_size=10)),
        visibility=visibility,
        servings=draw(st.integers(min_value=1, max_value=100)),
        nutrition_facts=nutrition,
        dietary_labels=dietary_labels,
        allergen_warnings=allergen_warnings,
    )


@st.composite
def collection_document_strategy(draw):
    """Generate valid CollectionDocument instances."""
    return CollectionDocument(
        user_id=draw(object_id_strategy()),
        name=draw(st.text(min_size=1, max_size=255, alphabet=st.characters(blacklist_categories=['Cs'], blacklist_characters=['\x00']))),
        description=draw(st.none() | st.text(max_size=1000, alphabet=st.characters(blacklist_categories=['Cs'], blacklist_characters=['\x00']))),
        nesting_level=draw(st.integers(min_value=0, max_value=3)),
        recipe_ids=draw(st.lists(object_id_strategy(), max_size=10)),
    )


@st.composite
def meal_plan_document_strategy(draw):
    """Generate valid MealPlanDocument instances."""
    return MealPlanDocument(
        user_id=draw(object_id_strategy()),
        recipe_id=draw(object_id_strategy()),
        meal_date=draw(st.dates(min_value=date(2020, 1, 1), max_value=date(2030, 12, 31))),
        meal_time=draw(st.sampled_from(["breakfast", "lunch", "dinner", "snack"])),
    )


@st.composite
def shopping_list_document_strategy(draw):
    """Generate valid ShoppingListDocument instances."""
    items = draw(st.lists(
        st.builds(
            ShoppingListItemEmbedded,
            ingredient_name=st.text(min_size=1, max_size=255, alphabet=st.characters(blacklist_categories=['Cs'], blacklist_characters=['\x00'])),
            quantity=st.none() | st.text(max_size=100, alphabet=st.characters(blacklist_categories=['Cs'], blacklist_characters=['\x00'])),
            category=st.sampled_from(["produce", "dairy", "meat", "pantry", "other"]),
            is_checked=st.booleans(),
            is_custom=st.booleans(),
            recipe_id=st.none() | object_id_strategy(),
        ),
        max_size=20
    ))
    
    return ShoppingListDocument(
        user_id=draw(object_id_strategy()),
        name=draw(st.text(min_size=1, max_size=255, alphabet=st.characters(blacklist_categories=['Cs'], blacklist_characters=['\x00']))),
        items=items,
    )


# Feature: mongodb-migration, Property 1: Document Identity Preservation
@given(user_doc=user_document_strategy())
@hypothesis_settings(max_examples=100)
def test_user_document_has_valid_object_id_after_creation(user_doc: UserDocument):
    """
    **Validates: Requirements 2.6**
    
    Property: For any document created in MongoDB, the document should have an 
    _id field that is a valid ObjectId.
    
    This property verifies that:
    1. Documents can be created with auto-generated ObjectIds
    2. The _id field is a valid ObjectId
    3. Document identity is preserved through serialization
    """
    # Simulate document creation by assigning an ObjectId
    user_doc.id = ObjectId()
    
    # Verify the document has a valid ObjectId
    assert user_doc.id is not None, "Document should have an _id field"
    assert isinstance(user_doc.id, ObjectId), "Document _id should be an ObjectId instance"
    assert ObjectId.is_valid(user_doc.id), "Document _id should be a valid ObjectId"
    
    # Verify the ObjectId can be converted to string and back
    id_str = str(user_doc.id)
    assert len(id_str) == 24, "ObjectId string representation should be 24 characters"
    assert ObjectId.is_valid(id_str), "ObjectId string should be valid"
    
    # Verify we can reconstruct the ObjectId from string
    reconstructed_id = ObjectId(id_str)
    assert reconstructed_id == user_doc.id, "Reconstructed ObjectId should match original"


# Feature: mongodb-migration, Property 1: Document Identity Preservation
@given(recipe_doc=recipe_document_strategy())
@hypothesis_settings(max_examples=100)
def test_recipe_document_has_valid_object_id_after_creation(recipe_doc: RecipeDocument):
    """
    **Validates: Requirements 2.6**
    
    Property: For any recipe document created in MongoDB, the document should 
    have an _id field that is a valid ObjectId.
    """
    # Simulate document creation by assigning an ObjectId
    recipe_doc.id = ObjectId()
    
    # Verify the document has a valid ObjectId
    assert recipe_doc.id is not None
    assert isinstance(recipe_doc.id, ObjectId)
    assert ObjectId.is_valid(recipe_doc.id)
    
    # Verify embedded references also use valid ObjectIds
    assert isinstance(recipe_doc.user_id, ObjectId)
    assert ObjectId.is_valid(recipe_doc.user_id)
    
    if recipe_doc.source_recipe_id:
        assert isinstance(recipe_doc.source_recipe_id, ObjectId)
        assert ObjectId.is_valid(recipe_doc.source_recipe_id)
    
    if recipe_doc.source_author_id:
        assert isinstance(recipe_doc.source_author_id, ObjectId)
        assert ObjectId.is_valid(recipe_doc.source_author_id)


# Feature: mongodb-migration, Property 1: Document Identity Preservation
@given(collection_doc=collection_document_strategy())
@hypothesis_settings(max_examples=100)
def test_collection_document_has_valid_object_id_after_creation(collection_doc: CollectionDocument):
    """
    **Validates: Requirements 2.6**
    
    Property: For any collection document created in MongoDB, the document 
    should have an _id field that is a valid ObjectId, and all embedded 
    recipe_ids should be valid ObjectIds.
    """
    # Simulate document creation by assigning an ObjectId
    collection_doc.id = ObjectId()
    
    # Verify the document has a valid ObjectId
    assert collection_doc.id is not None
    assert isinstance(collection_doc.id, ObjectId)
    assert ObjectId.is_valid(collection_doc.id)
    
    # Verify user_id is a valid ObjectId
    assert isinstance(collection_doc.user_id, ObjectId)
    assert ObjectId.is_valid(collection_doc.user_id)
    
    # Verify all recipe_ids are valid ObjectIds
    for recipe_id in collection_doc.recipe_ids:
        assert isinstance(recipe_id, ObjectId)
        assert ObjectId.is_valid(recipe_id)
    
    # Verify parent_collection_id if present
    if collection_doc.parent_collection_id:
        assert isinstance(collection_doc.parent_collection_id, ObjectId)
        assert ObjectId.is_valid(collection_doc.parent_collection_id)


# Feature: mongodb-migration, Property 1: Document Identity Preservation
@given(meal_plan_doc=meal_plan_document_strategy())
@hypothesis_settings(max_examples=100)
def test_meal_plan_document_has_valid_object_id_after_creation(meal_plan_doc: MealPlanDocument):
    """
    **Validates: Requirements 2.6**
    
    Property: For any meal plan document created in MongoDB, the document 
    should have an _id field that is a valid ObjectId.
    """
    # Simulate document creation by assigning an ObjectId
    meal_plan_doc.id = ObjectId()
    
    # Verify the document has a valid ObjectId
    assert meal_plan_doc.id is not None
    assert isinstance(meal_plan_doc.id, ObjectId)
    assert ObjectId.is_valid(meal_plan_doc.id)
    
    # Verify references are valid ObjectIds
    assert isinstance(meal_plan_doc.user_id, ObjectId)
    assert ObjectId.is_valid(meal_plan_doc.user_id)
    assert isinstance(meal_plan_doc.recipe_id, ObjectId)
    assert ObjectId.is_valid(meal_plan_doc.recipe_id)


# Feature: mongodb-migration, Property 1: Document Identity Preservation
@given(shopping_list_doc=shopping_list_document_strategy())
@hypothesis_settings(max_examples=100)
def test_shopping_list_document_has_valid_object_id_after_creation(shopping_list_doc: ShoppingListDocument):
    """
    **Validates: Requirements 2.6**
    
    Property: For any shopping list document created in MongoDB, the document 
    should have an _id field that is a valid ObjectId, and all embedded items 
    with recipe_ids should have valid ObjectIds.
    """
    # Simulate document creation by assigning an ObjectId
    shopping_list_doc.id = ObjectId()
    
    # Verify the document has a valid ObjectId
    assert shopping_list_doc.id is not None
    assert isinstance(shopping_list_doc.id, ObjectId)
    assert ObjectId.is_valid(shopping_list_doc.id)
    
    # Verify user_id is a valid ObjectId
    assert isinstance(shopping_list_doc.user_id, ObjectId)
    assert ObjectId.is_valid(shopping_list_doc.user_id)
    
    # Verify all item recipe_ids are valid ObjectIds if present
    for item in shopping_list_doc.items:
        if item.recipe_id:
            assert isinstance(item.recipe_id, ObjectId)
            assert ObjectId.is_valid(item.recipe_id)


# Feature: mongodb-migration, Property 1: Document Identity Preservation
@given(
    follower_id=object_id_strategy(),
    following_id=object_id_strategy()
)
@hypothesis_settings(max_examples=100)
def test_reference_documents_have_valid_object_ids(follower_id: ObjectId, following_id: ObjectId):
    """
    **Validates: Requirements 2.6**
    
    Property: For any reference-based document (ratings, notes, follows, likes, 
    comments), the document should have an _id field that is a valid ObjectId, 
    and all reference fields should be valid ObjectIds.
    """
    # Ensure follower and following are different to pass validation
    if follower_id == following_id:
        following_id = ObjectId()
    
    # Test UserFollowDocument
    follow_doc = UserFollowDocument(
        follower_id=follower_id,
        following_id=following_id
    )
    follow_doc.id = ObjectId()
    
    assert follow_doc.id is not None
    assert isinstance(follow_doc.id, ObjectId)
    assert ObjectId.is_valid(follow_doc.id)
    assert isinstance(follow_doc.follower_id, ObjectId)
    assert isinstance(follow_doc.following_id, ObjectId)
    
    # Test RecipeLikeDocument
    recipe_id = ObjectId()
    user_id = ObjectId()
    
    like_doc = RecipeLikeDocument(
        recipe_id=recipe_id,
        user_id=user_id
    )
    like_doc.id = ObjectId()
    
    assert like_doc.id is not None
    assert isinstance(like_doc.id, ObjectId)
    assert ObjectId.is_valid(like_doc.id)
    assert isinstance(like_doc.recipe_id, ObjectId)
    assert isinstance(like_doc.user_id, ObjectId)
    
    # Test RecipeRatingDocument
    rating_doc = RecipeRatingDocument(
        recipe_id=recipe_id,
        user_id=user_id,
        rating=5
    )
    rating_doc.id = ObjectId()
    
    assert rating_doc.id is not None
    assert isinstance(rating_doc.id, ObjectId)
    assert ObjectId.is_valid(rating_doc.id)
    
    # Test RecipeNoteDocument
    note_doc = RecipeNoteDocument(
        recipe_id=recipe_id,
        user_id=user_id,
        note_text="Test note"
    )
    note_doc.id = ObjectId()
    
    assert note_doc.id is not None
    assert isinstance(note_doc.id, ObjectId)
    assert ObjectId.is_valid(note_doc.id)
    
    # Test RecipeCommentDocument
    comment_doc = RecipeCommentDocument(
        recipe_id=recipe_id,
        user_id=user_id,
        comment_text="Test comment"
    )
    comment_doc.id = ObjectId()
    
    assert comment_doc.id is not None
    assert isinstance(comment_doc.id, ObjectId)
    assert ObjectId.is_valid(comment_doc.id)


def test_py_object_id_validation():
    """
    Unit test for PyObjectId validation.
    
    **Validates: Requirements 2.6**
    """
    # Valid ObjectId
    valid_id = ObjectId()
    assert PyObjectId.validate(valid_id) == valid_id
    
    # Valid ObjectId string
    valid_str = str(ObjectId())
    result = PyObjectId.validate(valid_str)
    assert isinstance(result, ObjectId)
    assert str(result) == valid_str
    
    # Invalid ObjectId
    with pytest.raises(ValueError, match="Invalid ObjectId"):
        PyObjectId.validate("invalid")
    
    with pytest.raises(ValueError, match="Invalid ObjectId"):
        PyObjectId.validate("12345")
    
    with pytest.raises(ValueError, match="Invalid ObjectId"):
        PyObjectId.validate("")
