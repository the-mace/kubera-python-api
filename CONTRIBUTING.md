# Contributing to Kubera Python API

Thank you for your interest in contributing to the Kubera Python API client! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and constructive in all interactions
- Welcome newcomers and help them get started
- Focus on what's best for the community and the project

## Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/kubera-python-api.git
cd kubera-python-api
```

### 2. Set Up Development Environment

```bash
# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package in editable mode with dev dependencies
pip install -e ".[dev]"
```

### 3. Set Up Credentials for Testing

Create `~/.env` with your Kubera API credentials:

```bash
KUBERA_API_KEY=your_api_key_here
KUBERA_SECRET=your_secret_here
```

**Note**: Tests use mock responses by default. Real API credentials are only needed for manual testing.

## Development Workflow

### Creating a Branch

Use descriptive branch names:

```bash
# For new features
git checkout -b feature/add-portfolio-search

# For bug fixes
git checkout -b fix/authentication-error

# For documentation
git checkout -b docs/improve-readme
```

### Making Changes

1. **Write clear, focused commits**
   - One logical change per commit
   - Write descriptive commit messages

2. **Follow code style**
   - We use Ruff for formatting and linting
   - Type hints are required for all functions
   - Line length: 100 characters

3. **Add tests for new functionality**
   - Unit tests in `tests/`
   - Aim for >90% code coverage
   - Use pytest fixtures from `tests/fixtures.py`

4. **Update documentation**
   - Update README.md if adding new features
   - Add docstrings to new functions
   - Update examples/ if applicable

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_client.py

# Run with coverage report
pytest --cov=kubera --cov-report=term-missing

# Run only specific test
pytest tests/test_client.py::test_get_portfolios
```

### Code Quality Checks

Run these before submitting a PR:

```bash
# Format code
ruff format .

# Check for linting issues
ruff check .

# Fix auto-fixable issues
ruff check --fix .

# Type checking
mypy kubera

# All checks together
ruff check . && ruff format . && mypy kubera && pytest
```

## Pull Request Process

### Before Submitting

- [ ] All tests pass (`pytest`)
- [ ] Code is formatted (`ruff format .`)
- [ ] No linting errors (`ruff check .`)
- [ ] Type checking passes (`mypy kubera`)
- [ ] Coverage hasn't decreased
- [ ] Documentation is updated
- [ ] Commit messages are clear

### Submitting the PR

1. **Push your branch** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create a Pull Request** on GitHub with:
   - Clear title describing the change
   - Description explaining what and why
   - Reference any related issues (`Fixes #123`)
   - Screenshots/examples if applicable

3. **Respond to feedback**
   - Address review comments promptly
   - Push additional commits to your branch
   - Ask questions if anything is unclear

### PR Review Criteria

Your PR will be reviewed for:

- **Functionality**: Does it work as intended?
- **Tests**: Are there adequate tests?
- **Code Quality**: Is it well-structured and readable?
- **Documentation**: Are changes documented?
- **Backwards Compatibility**: Does it break existing code?

## Types of Contributions

### Bug Reports

See [README.md](README.md#reporting-bugs) for bug reporting guidelines.

**Include:**
- Python version
- Package version
- Error messages and stack traces
- Minimal code to reproduce
- Expected vs actual behavior

### Feature Requests

See [README.md](README.md#feature-requests) for feature request guidelines.

**Include:**
- Use case description
- Proposed API/interface
- Example usage code
- Why existing functionality doesn't work

### Code Contributions

**Good First Issues:**
- Look for issues labeled `good first issue`
- These are beginner-friendly tasks
- Ask questions if anything is unclear

**Common Areas:**
- Adding new API endpoints
- Improving error messages
- Adding CLI features
- Writing tests
- Improving documentation

### Documentation Improvements

Documentation PRs are highly valued!

- Fix typos or unclear explanations
- Add examples or use cases
- Improve API documentation
- Update outdated information

## Project Structure

```
kubera-python-api/
├── kubera/              # Main package
│   ├── __init__.py     # Package exports
│   ├── client.py       # KuberaClient implementation
│   ├── cli.py          # Command-line interface
│   ├── auth.py         # Authentication logic
│   ├── types.py        # Type definitions
│   ├── exceptions.py   # Custom exceptions
│   ├── formatters.py   # CLI output formatting
│   └── cache.py        # Portfolio cache management
├── tests/              # Test suite
│   ├── test_client.py  # Client tests
│   ├── test_auth.py    # Auth tests
│   ├── test_cli.py     # CLI tests
│   └── fixtures.py     # Test fixtures
├── examples/           # Usage examples
├── .github/            # GitHub configuration
├── pyproject.toml      # Project metadata
└── README.md           # User documentation
```

## Coding Standards

### Python Style

- Follow PEP 8 (enforced by Ruff)
- Use type hints for all function parameters and returns
- Write docstrings for public functions
- Keep functions focused and small

### Type Hints

```python
# Good
def get_portfolio(portfolio_id: str) -> PortfolioData:
    """Get detailed portfolio data."""
    ...

# Bad - no types
def get_portfolio(portfolio_id):
    ...
```

### Error Handling

- Use custom exceptions from `exceptions.py`
- Provide helpful error messages
- Include context in exception messages

```python
# Good
raise KuberaAuthenticationError(
    "Authentication failed. Check credentials and IP restrictions.",
    status_code=401
)

# Bad
raise Exception("Auth failed")
```

### Testing

- Test both success and error cases
- Use descriptive test names
- Use pytest fixtures for common setup
- Mock external API calls

```python
def test_get_portfolios_success(mock_httpx_client):
    """Test successful portfolio retrieval."""
    client = KuberaClient(api_key="test", secret="test")
    portfolios = client.get_portfolios()
    assert len(portfolios) > 0
```

### Commit Messages

Follow conventional commit format:

```
type(scope): brief description

Detailed explanation of the change.

Fixes #123
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Test additions or changes
- `refactor`: Code refactoring
- `style`: Code style changes
- `chore`: Maintenance tasks

**Examples:**
```
feat(client): add support for bulk portfolio updates

Add new update_portfolios() method to efficiently update multiple
portfolios in a single API call.

Fixes #45
```

```
fix(auth): handle missing timestamp in auth headers

Previously crashed when timestamp was None. Now properly validates
and raises KuberaAuthenticationError.

Fixes #67
```

## Questions?

- **General questions**: Use [GitHub Discussions](https://github.com/the-mace/kubera-python-api/discussions)
- **Bug reports**: [GitHub Issues](https://github.com/the-mace/kubera-python-api/issues)
- **Security issues**: Email maintainers directly (don't open public issues)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Thank You!

Your contributions make this project better for everyone. Thank you for taking the time to contribute!
