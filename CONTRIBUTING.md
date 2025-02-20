# Contributing Guide

## Development Setup

1. Fork and clone the repository:
```bash
git clone https://github.com/your-username/claude-mcp-toolkit.git
cd claude-mcp-toolkit
```

2. Set up development environment:
- Follow instructions in `docs/setup.md`
- Install development dependencies

3. Create a new branch:
```bash
git checkout -b feature/your-feature
```

## Development Flow

1. Make your changes following our:
- Code style guide
- Architecture guidelines (`docs/architecture.md`)
- Test requirements

2. Test your changes:
```bash
# Backend tests
pytest

# Frontend tests
cd src/frontend
npm test
```

3. Update documentation:
- Update relevant docs in `/docs`
- Add comments to code
- Update README if needed

4. Commit changes:
```bash
git add .
git commit -m "feat: description of your changes"
```

5. Push and create PR:
```bash
git push origin feature/your-feature
```

## Code Style

1. Python (Backend):
- Follow PEP 8
- Use type hints
- Add docstrings
- Maximum line length: 88 characters

2. TypeScript (Frontend):
- Follow Prettier config
- Use TypeScript types
- Follow React best practices
- Use ESLint rules

## Testing

1. Backend Tests:
- Unit tests required
- Integration tests for API
- Minimum 80% coverage

2. Frontend Tests:
- Component tests
- Hook tests
- Integration tests
- E2E tests for critical flows

## Documentation

1. Code Documentation:
- Clear function/class documentation
- Inline comments for complex logic
- Type documentation
- Example usage

2. API Documentation:
- OpenAPI/Swagger docs
- Example requests/responses
- Error documentation

3. Architecture Documentation:
- Update `docs/architecture.md`
- Document new components
- Update diagrams if needed

## Pull Request Process

1. PR Requirements:
- Passes all tests
- Follows code style
- Has documentation
- Reviews addressed

2. Review Process:
- Code review required
- Documentation review
- Tests verified
- Performance checked

3. Merge Process:
- Squash and merge
- Clear commit message
- Delete branch after merge