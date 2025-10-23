"""Example using context manager for automatic cleanup."""

from kubera import KuberaClient

# Synchronous context manager
with KuberaClient() as client:
    portfolios = client.get_portfolios()
    print(f"Found {len(portfolios)} portfolios")

    if portfolios:
        portfolio = client.get_portfolio(portfolios[0]["id"])
        print(f"Portfolio: {portfolio['name']}")
        print(f"Assets: {len(portfolio.get('assets', []))}")
        print(f"Debts: {len(portfolio.get('debts', []))}")

# Client is automatically closed
