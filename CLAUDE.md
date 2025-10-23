# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a modern Python client library for the Kubera Data API v3. It provides both synchronous and asynchronous interfaces for interacting with Kubera portfolio data, with full type hints and comprehensive error handling.

## Installation and Setup

### Install for Development
```bash
pip install -e ".[dev]"
```

### Install from GitHub
```bash
pip install git+https://github.com/the-mace/kubera-python-api.git
```

### Environment Setup
Credentials are loaded from `~/.env`:
```bash
KUBERA_API_KEY=your_api_key
KUBERA_SECRET=your_secret
```

## Development Commands

### Testing
```bash
pytest                    # Run all tests
pytest -v                 # Verbose output
pytest --cov=kubera      # With coverage report
```

### Code Quality
```bash
ruff check .             # Lint code
ruff format .            # Format code
mypy kubera              # Type checking
```

### Running Examples
```bash
# Python examples
python examples/basic_usage.py
python examples/async_usage.py
python examples/context_manager.py

# CLI examples
kubera list
kubera show <portfolio-id>
kubera interactive
```

## Project Structure

```
kubera-python-api/
├── kubera/                  # Main package
│   ├── __init__.py         # Package exports
│   ├── client.py           # KuberaClient implementation
│   ├── cli.py              # Command-line interface
│   ├── formatters.py       # CLI output formatters
│   ├── auth.py             # HMAC-SHA256 authentication
│   ├── types.py            # TypedDict definitions
│   └── exceptions.py       # Custom exceptions
├── examples/               # Usage examples
│   ├── *.py                # Python library examples
│   └── cli_usage.md        # CLI documentation
├── tests/                  # Test suite
├── pyproject.toml         # Modern Python packaging
└── README.md              # User documentation
```

## Command-Line Interface

The package includes a `kubera` CLI command installed via the `[project.scripts]` entry point.

### CLI Commands
- `kubera list` - List all portfolios
- `kubera show <id>` - Show detailed portfolio information
- `kubera update <id>` - Update an asset or debt item
- `kubera interactive` - Interactive exploration mode

### CLI Features
- Human-readable output using Rich library for tables and colors
- `--raw` flag for JSON output (useful for scripting)
- `--tree` flag for hierarchical tree view
- Lazy client initialization (only connects when needed)

## Architecture

### Authentication Flow
- Uses HMAC-SHA256 signature-based authentication
- Signature generation: `HMAC(api_key + timestamp + method + path + body, secret)`
- Three headers required: `x-api-token`, `x-timestamp`, `x-signature`
- Body must be compact JSON (no spaces) for signature calculation

### Client Design
- **Dual API**: Both sync and async methods (async methods prefixed with `a`)
- **Context Managers**: Supports both `with` and `async with` for automatic cleanup
- **Error Handling**: Custom exception hierarchy for different error types
- **Type Safety**: Full type hints using `TypedDict` for API responses

### Key Modules

**`client.py`** - Main client class
- `KuberaClient`: Primary interface with sync/async methods
- `get_portfolios()` / `aget_portfolios()`: List all portfolios
- `get_portfolio(id)` / `aget_portfolio(id)`: Get portfolio details
- `update_item(id, updates)` / `aupdate_item(id, updates)`: Update assets/debts

**`auth.py`** - Authentication utilities
- `generate_signature()`: Creates HMAC-SHA256 signature
- `create_auth_headers()`: Generates complete auth headers

**`types.py`** - Type definitions
- `PortfolioSummary`: Portfolio list response type
- `PortfolioData`: Detailed portfolio response type
- `UpdateItemRequest`: Item update request type
- `ValueDict`, `ConnectionDict`, `ItemData`: Nested data structures

**`exceptions.py`** - Exception hierarchy
- `KuberaAPIError`: Base exception
- `KuberaAuthenticationError`: Auth failures (401)
- `KuberaRateLimitError`: Rate limit exceeded (429)
- `KuberaValidationError`: Invalid requests (400)

**`cli.py`** - Command-line interface
- `cli()`: Main Click group with credential handling
- `get_client()`: Lazy client initialization
- `list()`, `show()`, `update()`, `interactive()`: CLI commands

**`formatters.py`** - Output formatting
- `print_portfolios()`: Format portfolio list with Rich tables
- `print_portfolio()`: Format detailed portfolio view
- `print_asset_tree()`: Hierarchical tree view
- `print_item()`, `print_success()`, `print_error()`: Utility formatters

## API Endpoints

All endpoints use `https://api.kubera.com` as base URL:

1. **GET** `/api/v3/data/portfolio` - List all portfolios
2. **GET** `/api/v3/data/portfolio/{id}` - Get portfolio details
3. **POST** `/api/v3/data/item/{id}` - Update asset/debt item (requires update permissions)

### API Key Restrictions

**Update Permissions:**
- The POST `/api/v3/data/item/{id}` endpoint requires API keys with update permissions
- Read-only API keys will receive 403 Forbidden errors on update attempts
- List and show operations work with read-only keys

**IP Address Restrictions:**
- Some API keys may be restricted to specific IP addresses
- 401 Authentication errors may indicate IP address not in allowlist
- Users should verify their IP is allowed if seeing authentication failures

## Rate Limits

- 30 requests per minute (global limit)
- Essential tier: 100 requests/day (UTC)
- Black tier: 1000 requests/day (UTC)

## Common Issues and Error Handling

### Authentication Errors (401)
- Invalid API key or secret
- IP address not in allowlist (if IP restrictions enabled)
- Error messages include hints about checking credentials and IP restrictions

### Permission Errors (403)
- Attempting updates with read-only API key
- API key lacks required permissions for operation
- Error messages explain update permission requirements

### Rate Limit Errors (429)
- Exceeded requests per minute or daily limits
- Error messages include current rate limit information

## Development Guidelines

### Adding New Endpoints
1. Add method signature to `KuberaClient` in `client.py`
2. Implement both sync and async versions
3. Add type definitions to `types.py` if needed
4. Update error handling in `_handle_response()` if needed
5. Add example usage to `examples/`
6. Update README.md with new method documentation

### Type Hints
- Use `TypedDict` for API response structures
- Use `total=False` for optional fields
- All functions must have complete type annotations
- Run `mypy kubera` to verify type correctness

### Testing
- Use `pytest` for all tests
- Use `pytest-asyncio` for async test support
- Mock HTTP requests using `httpx` test utilities
- Aim for >90% code coverage

### Code Style
- Follow PEP 8 (enforced by Ruff)
- Line length: 100 characters
- Use Ruff for formatting and linting
- Docstrings required for all public methods
