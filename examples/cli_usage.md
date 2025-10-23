# Kubera CLI Usage Examples

This document demonstrates how to use the `kubera` command-line interface.

## Installation

After installing the package, the `kubera` command will be available:

```bash
pip install git+https://github.com/the-mace/kubera-python-api.git
```

## Important Notes

⚠️ **API Key Permissions**
- The `update` command requires an API key with **update permissions enabled**
- Read-only API keys will receive a 403 Forbidden error when attempting updates
- List and show commands work with read-only keys

⚠️ **IP Address Restrictions**
- Some API keys may be restricted to specific IP addresses
- If you receive 401 authentication errors, verify your IP is in the allowlist
- Contact Kubera support to modify IP restrictions

## Basic Commands

### Test Connection

Test your API connection and verify credentials (recommended first step):

```bash
# Human-readable format with diagnostics
kubera test

# Raw JSON output
kubera test --raw
```

**Output Example:**
```
Testing Kubera API connection...

→ Loading credentials...
→ Fetching portfolios...
✓ Successfully connected to Kubera API!
✓ Found 2 portfolio(s)

Portfolios:
  1. Personal Portfolio (ID: abc-123, Currency: USD)
  2. Business Portfolio (ID: def-456, Currency: EUR)

→ Fetching detailed data for first portfolio...
✓ Portfolio: Personal Portfolio
  - Assets: 15
  - Debts: 3
  - Insurance: 2
  - Net Worth: 250000.00 USD

==================================================
✓ All tests passed! Your Kubera API client is working correctly.
```

Use this command to:
- Verify your credentials are correct
- Check API connectivity
- Diagnose authentication issues
- Confirm IP address restrictions are not blocking you

### List All Portfolios

```bash
# Human-readable format
kubera list

# Raw JSON output
kubera list --raw
```

### Show Portfolio Details

```bash
# Show detailed portfolio information
kubera show PORTFOLIO_ID

# Show in tree view
kubera show PORTFOLIO_ID --tree

# Show as raw JSON
kubera show PORTFOLIO_ID --raw
```

### Update an Item

**Note:** Requires API key with update permissions!

```bash
# Update just the value
kubera update ITEM_ID --value 50000

# Update multiple fields
kubera update ITEM_ID --name "New Name" --value 50000 --description "Updated"

# Update with raw JSON output
kubera update ITEM_ID --value 50000 --raw
```

If you receive a 403 error, your API key doesn't have update permissions enabled.

### Interactive Mode

Launch an interactive session to explore portfolios:

```bash
kubera interactive
```

## Authentication

Credentials can be provided in multiple ways:

### 1. Environment File (Recommended)

Create `~/.env`:
```bash
KUBERA_API_KEY=your_api_key
KUBERA_SECRET=your_secret
```

### 2. Environment Variables

```bash
export KUBERA_API_KEY=your_api_key
export KUBERA_SECRET=your_secret
kubera list
```

### 3. Command-Line Options

```bash
kubera --api-key YOUR_KEY --secret YOUR_SECRET list
```

## Output Formats

### Human-Readable Format (Default)

The default output is formatted using Rich tables for easy reading:

```bash
$ kubera list
                          Portfolios (2)
┏━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ ID         ┃ Name            ┃ Currency ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ abc123     │ Main Portfolio  │ USD      │
│ def456     │ Savings         │ EUR      │
└────────────┴─────────────────┴──────────┘
```

### Raw JSON Format

Use `--raw` for machine-readable output:

```bash
$ kubera list --raw
[
  {
    "id": "abc123",
    "name": "Main Portfolio",
    "currency": "USD"
  },
  {
    "id": "def456",
    "name": "Savings",
    "currency": "EUR"
  }
]
```

## Examples

### Complete Workflow

```bash
# 1. Test connection (recommended first step)
kubera test

# 2. List portfolios to get IDs
kubera list

# 3. View details of first portfolio
kubera show abc123

# 4. View as tree for hierarchical view
kubera show abc123 --tree

# 5. Export to JSON for processing
kubera show abc123 --raw > portfolio.json

# 6. Update an asset value
kubera update asset_xyz --value 100000

# 7. Launch interactive mode
kubera interactive
```

### Using in Scripts

The `--raw` flag makes the CLI perfect for scripting:

```bash
#!/bin/bash

# Get all portfolio IDs
portfolio_ids=$(kubera list --raw | jq -r '.[].id')

# Loop through and export each
for id in $portfolio_ids; do
    echo "Exporting $id..."
    kubera show "$id" --raw > "portfolio_${id}.json"
done
```

### Getting Help

```bash
# General help
kubera --help

# Command-specific help
kubera list --help
kubera show --help
kubera update --help
kubera interactive --help

# Check version
kubera --version
```
