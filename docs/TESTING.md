# Testing Guide

## Testing Strategy

This project uses both traditional example-based testing and property-based testing to ensure robustness.

### Backend Testing (pytest + hypothesis)

**Test Structure:**
```
backend/tests/
├── conftest.py                    # Shared fixtures
├── test_auth_endpoints.py         # Auth API tests
├── test_auth_properties.py        # Auth property tests
├── test_recipe_endpoints.py       # Recipe API tests
├── test_recipe_properties.py      # Recipe property tests
├── test_image_endpoints.py        # Image API tests
├── test_image_properties.py       # Image property tests
└── test_integration.py            # End-to-end tests
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
```

### Frontend Testing (Jest + fast-check)

**Test Structure:**
```
frontend/
├── __tests__/                     # Integration tests
│   ├── animation-integration.test.tsx
│   ├── animation-performance.test.tsx
│   └── responsive-design.test.tsx
├── components/                    # Component tests
│   ├── AuthForm.test.tsx
│   ├── RecipeCard.test.tsx
│   ├── RecipeCard.property.test.tsx
│   └── ...
└── app/                          # Page tests
    └── dashboard/page.test.tsx
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
```

## Property-Based Testing

Property-based tests verify universal properties that should hold for all inputs.

**Backend Example (hypothesis):**
```python
from hypothesis import given, strategies as st

@given(st.text(min_size=1, max_size=100))
def test_username_roundtrip(username):
    # Property: Any valid username should survive encode/decode
    encoded = encode_username(username)
    decoded = decode_username(encoded)
    assert decoded == username
```

**Frontend Example (fast-check):**
```typescript
import fc from 'fast-check';

test('recipe title property', () => {
  fc.assert(
    fc.property(fc.string({ minLength: 1, maxLength: 200 }), (title) => {
      // Property: Any valid title should render without errors
      const { container } = render(<RecipeCard title={title} />);
      expect(container).toBeInTheDocument();
    })
  );
});
```

## Coverage Goals

- Backend: 80%+ coverage
- Frontend: 70%+ coverage

## Continuous Integration

Tests run automatically on:
- Pull requests
- Commits to main branch
- Pre-commit hooks (if configured)
