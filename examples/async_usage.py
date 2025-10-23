"""Async usage examples for the Kubera API client."""

import asyncio

from kubera import KuberaClient


async def main() -> None:
    """Demonstrate async API usage."""
    # Use async context manager
    async with KuberaClient() as client:
        # Fetch all portfolios asynchronously
        portfolios = await client.aget_portfolios()
        print(f"Found {len(portfolios)} portfolios")

        # Fetch multiple portfolios concurrently
        if portfolios:
            tasks = [client.aget_portfolio(p["id"]) for p in portfolios]
            portfolio_data = await asyncio.gather(*tasks)

            for portfolio in portfolio_data:
                net_worth = portfolio.get("net_worth", {})
                print(f"{portfolio['name']}: {net_worth.get('amount', 0)} {portfolio['currency']}")

        # Update an item asynchronously
        # item_id = "your_asset_or_debt_id"
        # updated = await client.aupdate_item(item_id, {"value": 50000})
        # print(f"Updated {updated['name']}")


if __name__ == "__main__":
    asyncio.run(main())
