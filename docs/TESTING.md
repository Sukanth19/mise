# Testing Guide

## Testing Strategy

This project uses both traditional example-based testing and property-based testing to ensure robustness.

**Dual Testing Approach:**

- **Unit Tests** validate specific examples, edge cases, and error conditions
- **Property-Based Tests** validate universal properties that should hold across all inputs

Both approaches are complementary and necessary for comprehensive coverage.

### Backend Testing (pytest + Hypothesis)

**Test Structure:**

```text
backend/tests/
├── conftest.py                           # Shared fixtures
├── test_auth_endpoints.py                # Auth API tests
├── test_auth_properties.py               # Auth property tests
├── test_recipe_endpoints.py              # Recipe API tests
├── test_recipe_properties.py             # Recipe property tests
├── test_rating_endpoints.py              # Rating API tests
├── test_rating_properties.py             # Rating property tests
├── test_collection_endpoints.py          # Collection API tests
├── test_collection_properties.py         # Collection property tests
├── test_meal_plan_endpoints.py           # Meal planning API tests
├── test_meal_plan_properties.py          # Meal planning property tests
├── test_shopping_list_endpoints.py       # Shopping list API tests
├── test_shopping_list_properties.py      # Shopping list property tests
├── test_nutrition_endpoints.py           # Nutrition API tests
├── test_nutrition_properties.py          # Nutrition property tests
├── test_social_endpoints.py              # Social features API tests
├── test_social_properties.py             # Social features property tests
├── test_filter_properties.py             # Filtering property tests
├── test_image_endpoints.py               # Image API tests
├── test_image_properties.py              # Image property tests
└── test_integration.py                   # End-to-end tests
```

**Running Tests:**

```bash
cd backend
source venv/bin/activate

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth_endpoints.py

# Run verbose
pytest -v

# Run property tests only
pytest -k "property"

# Run with specific number of property test iterations
pytest --hypothesis-iterations=1000
```

### Frontend Testing (Jest + fast-check)

**Test Structure:**

```text
frontend/
├── __tests__/                            # Integration tests
│   ├── animation-integration.test.tsx
│   ├── animation-performance.test.tsx
│   ├── responsive-design.test.tsx
│   ├── collection-workflow.test.tsx
│   ├── meal-planning-workflow.test.tsx
│   └── social-workflow.test.tsx
├── components/                           # Component tests
│   ├── AuthForm.test.tsx
│   ├── RecipeCard.test.tsx
│   ├── RecipeCard.property.test.tsx
│   ├── CollectionCard.test.tsx
│   ├── CollectionCard.property.test.tsx
│   ├── MealPlannerCalendar.test.tsx
│   ├── ShoppingListItem.test.tsx
│   ├── NutritionDisplay.test.tsx
│   ├── DiscoveryFeed.test.tsx
│   └── ...
└── app/                                  # Page tests
    ├── dashboard/page.test.tsx
    ├── collections/page.test.tsx
    ├── meal-planner/page.test.tsx
    └── discover/page.test.tsx
```

**Running Tests:**

```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm test -- --watch

# Run specific test file
npm test -- AuthForm.test.tsx

# Run property tests only
npm test -- property.test.tsx

# Run integration tests only
npm test -- __tests__/
```

## Property-Based Testing

Property-based tests verify universal properties that should hold for all inputs. Instead of testing specific examples, they generate hundreds of random test cases to find edge cases you might not think of.

**Backend Example (Hypothesis):**

```python
from hypothesis import given, strategies as st

# Feature: recipe-saver-enhancements, Property 32: Ingredient consolidation
@given(st.lists(
    st.tuples(
        st.text(min_size=1, max_size=50),  # ingredient name
        st.text(min_size=1, max_size=20)   # quantity
    ),
    min_size=1,
    max_size=20
))
def test_ingredient_consolidation_property(ingredients):
    """
    Property: Identical ingredient names (case-insensitive) should be 
    combined into a single shopping list item.
    """
    # Create recipes with ingredients
    recipes = create_test_recipes_with_ingredients(ingredients)
    
    # Generate shopping list
    shopping_list = shopping_list_generator.create_shopping_list(
        user_id=1,
        name="Test List",
        recipe_ids=[r.id for r in recipes],
        meal_plan_dates=None
    )
    
    # Check consolidation: case-insensitive matching
    ingredient_names = [ing[0].lower() for ing in ingredients]
    unique_names = set(ingredient_names)
    
    list_item_names = [item.ingredient_name.lower() for item in shopping_list.items]
    
    # Each unique ingredient should appear exactly once
    for name in unique_names:
        assert list_item_names.count(name) == 1
```

**Frontend Example (fast-check):**

```typescript
import fc from 'fast-check';

// Feature: recipe-saver-enhancements, Property 20: Collection user isolation
test('collections are associated with authenticated user', () => {
  fc.assert(
    fc.property(
      fc.record({
        id: fc.integer({ min: 1 }),
        user_id: fc.integer({ min: 1 }),
        name: fc.string({ minLength: 1, maxLength: 100 }),
        description: fc.option(fc.string()),
        nesting_level: fc.integer({ min: 0, max: 3 }),
      }),
      (collection) => {
        const { container } = render(
          <CollectionCard 
            collection={collection} 
            currentUserId={collection.user_id} 
          />
        );
        
        // Collection should be editable by owner
        expect(container.querySelector('[data-testid="edit-button"]'))
          .toBeInTheDocument();
        
        // Re-render with different user
        const { container: otherUserContainer } = render(
          <CollectionCard 
            collection={collection} 
            currentUserId={collection.user_id + 1} 
          />
        );
        
        // Collection should not be editable by other user
        expect(otherUserContainer.querySelector('[data-testid="edit-button"]'))
          .not.toBeInTheDocument();
      }
    ),
    { numRuns: 100 }
  );
});
```

## Property Test Configuration

**Backend (Hypothesis):**

Configure in `backend/pytest.ini` or `backend/pyproject.toml`:

```ini
[tool.pytest.ini_options]
addopts = "--hypothesis-show-statistics"

[tool.hypothesis]
max_examples = 100
deadline = None
```

**Frontend (fast-check):**

Configure in test files:

```typescript
fc.assert(
  fc.property(...),
  { 
    numRuns: 100,  // Number of test iterations
    verbose: true  // Show counterexamples
  }
);
```

## New Feature Test Coverage

### Collections (Requirements 10-13)

- **Unit Tests:** Collection CRUD, nesting validation, share token generation
- **Property Tests:** User isolation, nesting level validation, cascading deletion, share token uniqueness

### Meal Planning (Requirements 14-17)

- **Unit Tests:** Meal plan CRUD, template application, iCal export format
- **Property Tests:** Meal time validation, template application correctness, iCal format validation

### Shopping Lists (Requirements 18-23)

- **Unit Tests:** List generation, item check-off, custom items, sharing
- **Property Tests:** Ingredient consolidation, quantity summation, categorization, shared list synchronization

### Nutrition Tracking (Requirements 24-28)

- **Unit Tests:** Nutrition facts CRUD, dietary labels, allergen warnings, meal plan summaries
- **Property Tests:** Nutrition validation, per-serving calculation, meal plan summation

### Social Features (Requirements 29-36)

- **Unit Tests:** Visibility controls, likes, comments, follows, forking, URL import, QR codes
- **Property Tests:** Visibility filtering, discovery feed ordering, follow/like round trips, fork independence

### Filtering and Sorting (Requirements 4, 26, 27)

- **Unit Tests:** Specific filter combinations
- **Property Tests:** Favorite filtering, tag filtering, rating threshold, dietary labels, allergen exclusion, combined filters

## Coverage Goals

- Backend: 80%+ coverage
- Frontend: 70%+ coverage
- All correctness properties must have property-based tests
- All error conditions must have unit tests

## Running Property Tests with High Iterations

For thorough testing before releases:

**Backend:**

```bash
pytest --hypothesis-iterations=1000 -k "property"
```

**Frontend:**

Edit test files to increase `numRuns` to 1000+ for release testing.

## Continuous Integration

Tests run automatically on:

- Pull requests
- Commits to main branch
- Pre-commit hooks (if configured)

**CI Configuration:**

- Run all unit tests on every PR
- Run property tests with 100 iterations on every PR
- Run property tests with 1000 iterations on main branch
- Fail builds on test failures or coverage drops below thresholds
