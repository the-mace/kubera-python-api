# Test Suite

This directory contains comprehensive tests for the Kubera Python API client.

## Test Structure

### Test Files

- **`fixtures.py`** - Sanitized test fixtures based on real API responses
- **`test_auth.py`** - Tests for HMAC-SHA256 authentication
- **`test_client.py`** - Tests for client initialization and basic functionality
- **`test_client_api.py`** - Tests for synchronous API methods (get_portfolios, get_portfolio, update_item)
- **`test_client_async.py`** - Tests for asynchronous API methods
- **`test_cli.py`** - Tests for CLI commands (list, show, update)
- **`test_env_loading.py`** - Tests for environment variable loading

### Fixtures

The `fixtures.py` file contains sanitized test data based on actual Kubera API responses. The fixtures include:

- Portfolio list responses
- Detailed portfolio data with assets, debts, and insurance
- Different asset types (bank accounts, stocks, mutual funds)
- Error responses (401, 403, 429, 400)

All PII and financial data has been sanitized while preserving the actual API response structure.

## Running Tests

### Run All Tests
```bash
pytest
```

### Run with Verbose Output
```bash
pytest -v
```

### Run Specific Test File
```bash
pytest tests/test_client_api.py
```

### Run Specific Test
```bash
pytest tests/test_client_api.py::TestGetPortfolios::test_get_portfolios_success
```

### Run with Coverage
```bash
pytest --cov=kubera --cov-report=term-missing
```

### Run with Coverage HTML Report
```bash
pytest --cov=kubera --cov-report=html
open htmlcov/index.html
```

## Test Coverage

Current test coverage (as of last run):
- **Overall**: 50%
- **auth.py**: 100%
- **client.py**: 89%
- **exceptions.py**: 100%
- **types.py**: 100%
- **__init__.py**: 100%

Areas with lower coverage (not critical for API functionality):
- **formatters.py**: 17% (CLI output formatting - tested manually)
- **cache.py**: 21% (portfolio caching for CLI)
- **cli.py**: 63% (interactive mode and advanced CLI features)

## Test Categories

### Authentication Tests (`test_auth.py`)
- Signature generation for GET and POST requests
- Timestamp handling
- Header creation
- Signature consistency and variation

### Client Initialization Tests (`test_client.py`)
- Credentials from parameters, environment, and .env file
- Custom base URL and timeout
- Context manager support
- URL building and header creation

### API Method Tests (`test_client_api.py`)
- Portfolio listing (empty, success, errors)
- Portfolio details (success, not found)
- Item updates (success, partial, permission denied, validation errors)
- Error handling (401, 403, 429, 400, 500)
- Response unwrapping

### Async Tests (`test_client_async.py`)
- Async portfolio listing
- Async portfolio details
- Async item updates
- Async context manager

### CLI Tests (`test_cli.py`)
- List command (normal and raw output)
- Show command (normal, raw, tree output)
- Update command (single and multiple fields)
- Error handling and authentication failures
- Environment variable support

## Updating Fixtures

The fixtures in `fixtures.py` are based on actual API responses with sanitized data. If the API structure changes significantly, you may need to:

1. Make real API calls to see the new response structure
2. Update the fixture data structures in `fixtures.py` to match
3. Ensure all PII and financial data is sanitized

## Writing New Tests

When adding new tests:

1. Use the fixtures from `fixtures.py`
2. Mock HTTP responses using `unittest.mock`
3. Follow the existing test structure and naming conventions
4. Add docstrings to all test functions
5. Group related tests in classes
6. Test both success and error cases

Example:
```python
from tests.fixtures import PORTFOLIO_DETAIL_RESPONSE, wrap_api_response

def test_new_feature(client, mock_response):
    """Test description."""
    response = mock_response(200, wrap_api_response(PORTFOLIO_DETAIL_RESPONSE))

    with patch.object(client._client, 'get', return_value=response):
        result = client.new_method()

    assert result is not None
```

## Continuous Integration

Tests should be run in CI/CD pipelines before merging. Recommended commands:

```bash
# Lint code
ruff check .

# Type check
mypy kubera

# Run tests with coverage
pytest --cov=kubera --cov-report=term-missing

# Ensure minimum coverage (adjust threshold as needed)
pytest --cov=kubera --cov-fail-under=50
```
