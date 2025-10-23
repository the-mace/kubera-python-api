"""Basic usage examples for the Kubera API client."""

from kubera import KuberaClient

# Initialize client (automatically loads from ~/.env)
client = KuberaClient()

# Or provide credentials explicitly
# client = KuberaClient(api_key="your_key", secret="your_secret")

# Get all portfolios
portfolios = client.get_portfolios()
print(f"Found {len(portfolios)} portfolios:")
for portfolio in portfolios:
    print(f"  - {portfolio['name']} ({portfolio['currency']})")

# Get detailed data for first portfolio
if portfolios:
    portfolio_id = portfolios[0]["id"]
    portfolio = client.get_portfolio(portfolio_id)

    print(f"\nPortfolio: {portfolio['name']}")
    print(f"Net Worth: {portfolio.get('net_worth', {}).get('amount', 0)} {portfolio['currency']}")

    # List assets
    assets = portfolio.get("assets", [])
    print(f"\nAssets ({len(assets)}):")
    for asset in assets[:5]:  # Show first 5
        value = asset.get("value", {})
        print(f"  - {asset['name']}: {value.get('amount', 0)} {value.get('currency', '')}")

    # List debts
    debts = portfolio.get("debts", [])
    print(f"\nDebts ({len(debts)}):")
    for debt in debts[:5]:  # Show first 5
        value = debt.get("value", {})
        print(f"  - {debt['name']}: {value.get('amount', 0)} {value.get('currency', '')}")

# Update an item (uncomment to use)
# item_id = "your_asset_or_debt_id"
# updated = client.update_item(item_id, {"value": 50000, "description": "Updated via API"})
# print(f"Updated {updated['name']}")

# Clean up
client.close()
