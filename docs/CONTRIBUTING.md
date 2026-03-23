# Contributing Guide

## Development Setup

1. Fork the repository
2. Clone your fork
3. Follow setup instructions in [SETUP.md](SETUP.md)
4. Create a feature branch

## Code Style

### Backend (Python)
- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Use meaningful variable names

### Frontend (TypeScript)
- Follow ESLint configuration
- Use TypeScript strict mode
- Prefer functional components
- Use meaningful component names

## Testing Requirements

All new features must include:
- Unit tests for core functionality
- Property-based tests for data transformations
- Integration tests for API endpoints

### Running Tests Before Commit

```bash
# Backend
cd backend
pytest --cov=app

# Frontend
cd frontend
npm test -- --coverage
```

## Commit Messages

Use conventional commits format:

```
feat: add recipe search functionality
fix: resolve image upload bug
docs: update API documentation
test: add property tests for auth
refactor: simplify recipe service
```

## Pull Request Process

1. Update documentation if needed
2. Ensure all tests pass
3. Update CHANGELOG if applicable
4. Request review from maintainers

## Code Review Guidelines

- Be respectful and constructive
- Focus on code quality and maintainability
- Suggest improvements, don't demand changes
- Approve when ready, request changes if needed
