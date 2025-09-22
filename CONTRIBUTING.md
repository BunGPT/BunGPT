# Contributing to BunGPT

Thank you for your interest in contributing to BunGPT! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Code Style](#code-style)
- [Documentation](#documentation)

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive feedback
- Respect different viewpoints and experiences

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/BunGPT.git
   cd BunGPT
   ```
3. **Add the upstream repository**:
   ```bash
   git remote add upstream https://github.com/BunGPT/BunGPT.git
   ```

## Development Setup

1. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install development dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

3. **Install pre-commit hooks**:
   ```bash
   pre-commit install
   ```

4. **Verify the setup**:
   ```bash
   pytest tests/
   ```

## Making Changes

1. **Create a new branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following our coding standards

3. **Add tests** for new functionality

4. **Update documentation** if needed

5. **Test your changes**:
   ```bash
   pytest
   black --check bungpt tests examples
   isort --check-only bungpt tests examples
   mypy bungpt
   flake8 bungpt tests examples
   ```

## Testing

We maintain a comprehensive test suite:

- **Unit tests**: Test individual components in isolation
- **Integration tests**: Test component interactions
- **End-to-end tests**: Test complete workflows

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=bungpt --cov-report=html

# Run specific test files
pytest tests/unit/test_config.py

# Run tests matching a pattern
pytest -k "test_tool"
```

### Writing Tests

- Use descriptive test names that explain what is being tested
- Follow the Arrange-Act-Assert pattern
- Mock external dependencies
- Test both success and failure cases
- Use pytest fixtures for common test data

Example test structure:
```python
def test_feature_should_do_something_when_condition():
    # Arrange
    input_data = create_test_data()
    
    # Act
    result = function_under_test(input_data)
    
    # Assert
    assert result.success is True
    assert result.value == expected_value
```

## Submitting Changes

1. **Push your changes** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create a Pull Request** on GitHub:
   - Use a clear, descriptive title
   - Describe what changes you made and why
   - Reference any related issues
   - Include screenshots for UI changes
   - Ensure all checks pass

3. **Address review feedback**:
   - Make requested changes
   - Push additional commits to your branch
   - Respond to reviewer comments

## Code Style

We use automated tools to maintain consistent code style:

### Python Code Style

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking

Configuration is in `pyproject.toml`.

### Naming Conventions

- **Functions and variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private methods**: `_leading_underscore`
- **Modules**: `lowercase` or `snake_case`

### Documentation Strings

Use Google-style docstrings:

```python
def example_function(param1: str, param2: int) -> bool:
    """Brief description of the function.
    
    Detailed description if needed.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When something goes wrong
    """
    pass
```

### Type Hints

- Use type hints for all function signatures
- Import types from `typing` module when needed
- Use `Optional[T]` for optional parameters
- Use `Union[T, U]` for union types (or `T | U` in Python 3.10+)

## Documentation

### Code Comments

- Write clear, concise comments explaining **why**, not **what**
- Update comments when code changes
- Remove outdated comments
- Use TODO comments sparingly and include your name/date

### README and Docs

- Update README.md for user-facing changes
- Add examples for new features
- Update API documentation
- Check that all links work

### Commit Messages

Use conventional commit format:

```
type(scope): brief description

Detailed explanation if needed

Fixes #issue-number
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Examples:
- `feat(tools): add browser search functionality`
- `fix(api): handle empty request body gracefully`
- `docs(readme): update installation instructions`

## Project Structure

```
BunGPT/
├── bungpt/                 # Main package
│   ├── core/              # Core functionality
│   ├── models/            # Model implementations
│   ├── tools/             # Tool system
│   ├── api/               # API server
│   ├── cli/               # Command-line interface
│   └── utils/             # Utility functions
├── tests/                 # Test suite
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── fixtures/          # Test data
├── examples/              # Example scripts
├── docs/                  # Documentation
└── configs/               # Configuration examples
```

## Review Process

All changes go through code review:

1. **Automated checks** must pass (tests, linting, type checking)
2. **Manual review** by maintainers
3. **Discussion** and iteration if needed
4. **Approval** and merge

### Review Criteria

- **Functionality**: Does it work as intended?
- **Code Quality**: Is it well-written and maintainable?
- **Tests**: Are there adequate tests?
- **Documentation**: Is it properly documented?
- **Performance**: Does it impact performance?
- **Security**: Are there security implications?

## Getting Help

- **GitHub Issues**: Report bugs or request features
- **GitHub Discussions**: Ask questions or discuss ideas
- **Code Review**: Ask for feedback on your changes

## Recognition

Contributors will be:

- Listed in the contributors section
- Credited in release notes for significant contributions
- Invited to join the contributors team for ongoing contributors

Thank you for contributing to BunGPT! 🚀