# Kubera Python API Client

[![CI](https://github.com/the-mace/kubera-python-api/actions/workflows/ci.yml/badge.svg)](https://github.com/the-mace/kubera-python-api/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Modern, type-safe Python client for the [Kubera](https://www.kubera.com/) Data API v3.

## Features

- 🚀 **Modern Python** - Built with Python 3.10+ features, full type hints
- 🔄 **Async Support** - Both synchronous and asynchronous APIs
- 🔒 **Type Safe** - Comprehensive type definitions with TypedDict
- 🎯 **Easy to Use** - Simple, intuitive interface with Python library and CLI
- 🔐 **Secure Authentication** - HMAC-SHA256 signature-based auth
- 📦 **Zero Config** - Automatically loads credentials from `~/.env`
- 💻 **Command-Line Interface** - Interactive CLI with beautiful output formatting
- 🧪 **Well Tested** - Comprehensive test coverage
- 📖 **Well Documented** - Clear examples and API docs

## Installation

Install directly from GitHub:

```bash
pip install git+https://github.com/the-mace/kubera-python-api.git
```

Or for development:

```bash
git clone https://github.com/the-mace/kubera-python-api.git
cd kubera-python-api
pip install -e ".[dev]"
```

## Quick Start

### Setup Credentials

Add your Kubera API credentials to `~/.env`. Both formats are supported:

**Standard format:**
```bash
KUBERA_API_KEY=your_api_key_here
KUBERA_SECRET=your_secret_here
```

**Shell export format (for sourcing):**
```bash
export KUBERA_API_KEY=your_api_key_here
export KUBERA_SECRET=your_secret_here
```

The library automatically detects and handles both formats, so you can use the same `~/.env` file that you source in your shell.

**Using sourced environment variables:**

If you prefer to source your `.env` file in your shell:
```bash
source ~/.env
kubera list  # Will use the exported variables
```

**Important Notes:**
- **Update Permissions**: The `update_item()` method requires your API key to have update permissions enabled. Read-only API keys will receive a 403 error.
- **IP Restrictions**: Some API keys may be restricted to specific IP addresses. If you receive authentication errors, verify your IP address is allowed.

### Basic Usage

```python
from kubera import KuberaClient

# Initialize client (auto-loads from ~/.env)
client = KuberaClient()

# Get all portfolios
portfolios = client.get_portfolios()
for portfolio in portfolios:
    print(f"{portfolio['name']} - {portfolio['currency']}")

# Get detailed portfolio data
portfolio = client.get_portfolio(portfolios[0]['id'])
print(f"Net Worth: {portfolio['net_worth']['amount']}")

# Update an asset or debt
client.update_item(
    item_id="asset_id",
    updates={"value": 50000, "description": "Updated value"}
)

# Clean up
client.close()
```

### Using Context Manager

```python
from kubera import KuberaClient

with KuberaClient() as client:
    portfolios = client.get_portfolios()
    # Client automatically closed after block
```

### Async Usage

```python
import asyncio
from kubera import KuberaClient

async def main():
    async with KuberaClient() as client:
        # Use async methods (prefixed with 'a')
        portfolios = await client.aget_portfolios()
        portfolio = await client.aget_portfolio(portfolios[0]['id'])

        # Update asynchronously
        await client.aupdate_item(
            item_id="asset_id",
            updates={"value": 50000}
        )

asyncio.run(main())
```

## Command-Line Interface

The package includes a full-featured CLI for interactive exploration:

```bash
# Test your API connection (recommended first step)
kubera test

# List all portfolios (with indexes)
kubera list

# Show portfolio summary - use index or full GUID
kubera show 1
kubera show 4
kubera show <portfolio-guid>

# Show portfolio as tree view
kubera show 1 --tree

# Drill down into a specific sheet to see individual items with gains
kubera drill 4 asset "Investments"
kubera drill 1 asset "Bank Accounts"
kubera drill 2 debt "Credit Cards"

# Update an asset or debt
kubera update <item-id> --value 50000

# Interactive mode
kubera interactive

# Get raw JSON output
kubera test --raw
kubera list --raw
kubera show 1 --raw
kubera drill 4 asset "Investments" --raw
```

### Portfolio Index vs. GUID

All commands accept either:
- **Index number** (e.g., `1`, `2`, `3`) - shown in `kubera list` output
- **Full GUID** (e.g., `fee3014c-64d4-40cd-b78b-a0447295102b`)

The system automatically detects which you're using. Indexes are cached locally in `~/.kubera/portfolio_cache.json` when you run `kubera list`.

### CLI Features

- **Beautiful Output** - Rich formatting with tables and colors
- **Two-Level Navigation** - Overview with `show`, detailed view with `drill`
- **Gain Calculations** - Shows cost basis, overall gains (value & percentage)
- **Raw JSON Mode** - Perfect for scripting with `--raw` flag
- **Tree View** - Hierarchical visualization with `--tree`
- **Interactive Mode** - Step-by-step exploration of portfolios

### Insurance Data Note

**Important:** Insurance information displayed by this library represents life insurance coverage amounts (death benefits), not the cash value or premium amounts of insurance policies. These amounts are shown separately from net worth calculations as they represent future payouts, not current assets.

If you need to track the cash value of insurance policies (e.g., whole life insurance cash value), you should enter those amounts under Assets in the Kubera UI, not in the Insurance section.

To view insurance information in the Kubera web UI, navigate to: **Beneficiary → Insurance**

### Drill Command Details

The `drill` command provides detailed item-level information for a specific sheet:

```bash
kubera drill <portfolio-id> <category> <sheet-name>
```

**Features:**
- Shows all individual items within a sheet
- **Groups items by sections** (e.g., "Brokerage Account", "Retirement - 401K")
- Displays current value, quantity, and ticker
- Calculates cost basis (when available)
- Shows overall gains in both dollar amount and percentage
- Color-coded gains (green for positive, red for negative)
- Summary totals at sheet and section levels
- Filters out parent account entries to avoid duplication

**Example Output:**
```
Personal Portfolio
Asset: Investments

Total Value: USD 250,450.00 | Cost Basis: USD 185,000.00 | Gain: +USD 65,450.00 (+35.38%)

Total Items: 4 across 2 section(s)

Brokerage Account (2 items)
Value: USD 175,250.00 | Cost: USD 135,000.00 | Gain: +USD 40,250.00 (+29.81%)
┌──────────────┬──────────────┬────────┬──────────┬────────────┬──────────────┬──────────┐
│ Name         │ Value        │ Ticker │ Quantity │ Cost Basis │ Gain/Loss    │ Gain %   │
├──────────────┼──────────────┼────────┼──────────┼────────────┼──────────────┼──────────┤
│ Acme Corp    │ USD 52,500.00│ ACME   │      500 │ USD 40,000 │ +USD 12,500  │ +31.25%  │
│ Tech Global  │ USD 38,750.00│ TECH   │      250 │ USD 30,000 │ +USD 8,750   │ +29.17%  │
└──────────────┴──────────────┴────────┴──────────┴────────────┴──────────────┴──────────┘

Retirement Account - 401K (2 items)
Value: USD 75,200.00
┌──────────────┬──────────────┬────────┬──────────┬────────────┬──────────────┬──────────┐
│ Name         │ Value        │ Ticker │ Quantity │ Cost Basis │ Gain/Loss    │ Gain %   │
├──────────────┼──────────────┼────────┼──────────┼────────────┼──────────────┼──────────┤
│ SP500 INDEX  │ USD 45,000.00│ SPY    │   150.00 │            │              │          │
│ BOND FUND    │ USD 30,200.00│ BND    │   375.00 │            │              │          │
└──────────────┴──────────────┴────────┴──────────┴────────────┴──────────────┴──────────┘
```

**Section Grouping:**
Items within a sheet are automatically grouped by their section (e.g., different brokerage accounts, retirement accounts). Each section shows:
- Section name and item count
- Section-level totals and gains
- Individual items in that section

**Note:** Daily gains are not available from the Kubera API. Only overall gains (current value vs. cost basis) are calculated.

See [CLI Usage Examples](examples/cli_usage.md) for detailed documentation.

### Explicit Credentials

```python
from kubera import KuberaClient

client = KuberaClient(
    api_key="your_api_key",
    secret="your_secret"
)
```

## API Reference

### Client Methods

#### `get_portfolios() -> list[PortfolioSummary]`
Get list of all portfolios.

**Returns:** List of portfolio summaries with `id`, `name`, and `currency`.

#### `get_portfolio(portfolio_id: str) -> PortfolioData`
Get comprehensive data for a specific portfolio.

**Parameters:**
- `portfolio_id`: The portfolio ID from `get_portfolios()`

**Returns:** Complete portfolio data including assets, debts, insurance, net worth, and allocation.

#### `update_item(item_id: str, updates: UpdateItemRequest) -> dict`
Update an asset or debt item.

**Parameters:**
- `item_id`: The asset or debt ID
- `updates`: Dictionary with fields to update:
  - `name` (str): Item name
  - `description` (str): Item description
  - `value` (float): Item value
  - `cost` (float): Item cost basis

**Returns:** Updated item data.

**Note:** Requires an API key with update permissions enabled. Read-only keys will fail with a 403 error.

### Async Methods

All sync methods have async equivalents prefixed with `a`:
- `aget_portfolios()`
- `aget_portfolio(portfolio_id)`
- `aupdate_item(item_id, updates)`

## Error Handling

```python
from kubera import (
    KuberaClient,
    KuberaAPIError,
    KuberaAuthenticationError,
    KuberaRateLimitError,
    KuberaValidationError,
)

try:
    client = KuberaClient()
    portfolios = client.get_portfolios()
except KuberaAuthenticationError as e:
    print(f"Authentication failed: {e.message}")
    # Check: 1) Credentials are correct, 2) IP address is allowed
except KuberaRateLimitError as e:
    print(f"Rate limit exceeded: {e.message}")
except KuberaValidationError as e:
    print(f"Invalid request: {e.message}")
except KuberaAPIError as e:
    print(f"API error: {e.message} (status: {e.status_code})")
    # 403 errors on updates mean API key lacks update permissions
```

### Common Error Scenarios

**Authentication Errors (401)**
- Invalid API key or secret
- IP address not in allowlist (if IP restrictions are enabled)

**Forbidden Errors (403)**
- Attempting to update with a read-only API key
- API key doesn't have permission for the requested operation

**Rate Limit Errors (429)**
- Exceeded 30 requests per minute
- Exceeded daily limit (100 for Essential, 1000 for Black tier)

## Rate Limits

- **Global:** 30 requests per minute
- **Kubera Essential:** 100 requests per day (UTC)
- **Kubera Black:** 1000 requests per day (UTC)

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/the-mace/kubera-python-api.git
cd kubera-python-api

# Install with dev dependencies
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

### Code Quality

```bash
# Format and lint
ruff check .
ruff format .

# Type checking
mypy kubera
```

## Examples

See the [examples/](examples/) directory for more usage examples:

### Python Library
- [`basic_usage.py`](examples/basic_usage.py) - Basic synchronous usage
- [`async_usage.py`](examples/async_usage.py) - Asynchronous usage with concurrent requests
- [`context_manager.py`](examples/context_manager.py) - Using context managers for cleanup

### Command-Line Interface
- [`cli_usage.md`](examples/cli_usage.md) - Complete CLI documentation and examples

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support & Issues

### Reporting Bugs

Found a bug? Please help us improve by reporting it!

1. **Check existing issues** at [GitHub Issues](https://github.com/the-mace/kubera-python-api/issues) to avoid duplicates
2. **Create a new issue** using our bug report template
3. **Include the following information:**
   - Python version (`python --version`)
   - Package version (`pip show kubera-api`)
   - Error messages and full stack traces
   - Minimal code example to reproduce the issue
   - Expected vs actual behavior

### Feature Requests

Have an idea for a new feature or enhancement?

1. **Open a feature request** at [GitHub Issues](https://github.com/the-mace/kubera-python-api/issues)
2. **Describe your use case** - what problem would this solve?
3. **Provide examples** of how you'd like to use the feature

### Questions & Support

- **API Questions**: Refer to [Kubera's official documentation](https://www.kubera.com/)
- **Library Usage**: Check the [examples/](examples/) directory and this README
- **Discussion**: Use [GitHub Discussions](https://github.com/the-mace/kubera-python-api/discussions) for questions and community support

## Contributing

Contributions are welcome! We appreciate your help in making this library better.

### Getting Started

1. **Fork the repository** and clone your fork
2. **Install development dependencies**: `pip install -e ".[dev]"`
3. **Create a branch** for your changes: `git checkout -b feature/your-feature-name`
4. **Make your changes** and add tests
5. **Run the test suite**: `pytest`
6. **Check code quality**: `ruff check . && ruff format . && mypy kubera`
7. **Submit a Pull Request** with a clear description of your changes

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

### Development Workflow

```bash
# Run tests
pytest -v

# Run tests with coverage
pytest --cov=kubera --cov-report=term-missing

# Check code formatting and linting
ruff check .
ruff format .

# Type checking
mypy kubera
```

## API Key Restrictions

See [API_RESTRICTIONS.md](API_RESTRICTIONS.md) for detailed information about:
- Read-only vs update permissions
- IP address restrictions
- Error handling and troubleshooting

## API Documentation Discrepancies

This library was built based on real API responses and testing. Several discrepancies were found between the [official API documentation](https://docs.google.com/document/d/1G6YjL27eOrfBQZPS6H91ZFDGZ97YnS6Ra5Nnsth7CYg/view) and actual API behavior:

### Response Structure Differences

**Documentation states:**
```json
{
  "data": {
    "asset": [],
    "debt": [],
    "assetTotal": "number",
    "debtTotal": "number",
    "netWorth": "number"
  }
}
```

**Actual API returns:**
```json
{
  "data": {
    "asset": [],
    "debt": [],
    "insurance": [],
    "netWorth": {"amount": number, "currency": string},
    "totalAssets": {"amount": number, "currency": string},
    "totalDebts": {"amount": number, "currency": string}
  }
}
```

**Key differences:**
1. **Value objects**: Financial values are returned as `{amount, currency}` objects, not simple numbers
2. **Field naming**:
   - API returns `totalAssets` and `totalDebts` (camelCase with "total" prefix)
   - Documentation shows `assetTotal` and `debtTotal`
3. **Missing fields**: Documentation doesn't mention the `insurance` array which is present in responses

### Asset/Debt Object Fields

The documentation provides a minimal field list, but actual API responses include many additional fields that are critical for proper portfolio management:

**Additional fields found in real API responses:**
- `sectionId`, `sectionName` - Organizational grouping within sheets
- `sheetId`, `sheetName` - Parent sheet information
- `category` - Item category (asset/debt/insurance)
- `tickerId`, `tickerSubType`, `tickerSector` - Enhanced ticker information
- `exchange` - Stock exchange information
- `investable` - Liquidity classification (non_investable/investable_easy_convert/investable_cash)
- `isin` - International Securities Identification Number
- `subType` - Detailed type classification (cash, stock, mutual fund, mortgage, life, etc.)
- `holdingsCount` - Number of sub-holdings
- `rate` - Current price information as `{price, currency}` object
- `costBasisForTax` - Tax-specific cost basis (separate from `cost`)
- `taxRate`, `taxStatus`, `taxOnUnrealizedGain` - Comprehensive tax information
- `parent` - Parent account information as `{id, name}` object
- `liquidity` - Liquidity classification (high/medium/low)
- `sector` - Sector classification
- `geography` - Geographic allocation `{country, region}`
- `assetClass` - Asset class classification (cash, stock, fund, etc.)
- `purchaseDate` - Purchase date in YYYY-MM-DD format
- `holdingPeriodInDays` - Days held
- `isManual` - Whether item is manually tracked or aggregator-connected
- `irr` - Internal rate of return (as decimal, e.g., 1.1359 = 113.59%)

### Connection Object Structure

**Documentation shows:** Basic aggregator information

**Actual API returns:**
```json
{
  "aggregator": "plaid|yodlee|mx",
  "providerName": "Institution Name",
  "lastUpdated": "ISO-8601 timestamp or null",
  "id": "connection_id",
  "accountId": "account_id"
}
```

The connection object provides detailed aggregator information including specific connection IDs and account IDs for tracking.

### Rate Limits

The rate limits are correctly documented and match actual API behavior:
- 30 requests per minute (global)
- 100 requests per day for Essential tier (UTC)
- 1000 requests per day for Black tier (UTC)

### Testing Basis

These discrepancies were identified by comparing:
- Real API responses captured in test fixtures (`tests/fixtures.py`)
- Comprehensive test suite (`tests/test_client_api.py`)
- Official API documentation (dated October 2024)

The library implementation is based on actual API behavior and has been tested against real Kubera API responses with sanitized data.

**Note:** If you encounter response structures different from what this library expects, please file an issue with the response details.

## Related Projects

### Kubera Reporting

[**kubera-reporting**](https://github.com/the-mace/kubera-reporting) builds on this API library to provide advanced reporting capabilities for your Kubera portfolios:

- **Excel Report Generation** - Create comprehensive Excel workbooks with multiple sheets
- **Historical Tracking** - Track portfolio changes over time
- **Portfolio Comparisons** - Compare multiple portfolios side-by-side
- **Automated Snapshots** - Schedule automated portfolio snapshots
- **Custom Analytics** - Calculate additional metrics and visualizations
- **Export Capabilities** - Generate reports in multiple formats

If you need more than basic API access and want to generate reports or track your portfolio history, check out the kubera-reporting project.

## Support

For API documentation and support, visit [Kubera's official documentation](https://www.kubera.com/).
