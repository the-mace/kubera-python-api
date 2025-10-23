"""Command-line interface for Kubera API."""

import sys

import click

from kubera.cache import load_portfolio_cache, resolve_portfolio_id, save_portfolio_cache
from kubera.client import KuberaClient
from kubera.exceptions import KuberaAPIError
from kubera.formatters import (
    print_asset_tree,
    print_error,
    print_item,
    print_portfolio,
    print_portfolios,
    print_sheet_detail,
    print_success,
)


@click.group()
@click.version_option(version="0.1.0", prog_name="kubera")
@click.option(
    "--api-key",
    envvar="KUBERA_API_KEY",
    help="Kubera API key (or set KUBERA_API_KEY env var)",
)
@click.option(
    "--secret", envvar="KUBERA_SECRET", help="Kubera API secret (or set KUBERA_SECRET env var)"
)
@click.pass_context
def cli(ctx: click.Context, api_key: str | None, secret: str | None) -> None:
    """Kubera API command-line interface.

    Interactive tool for exploring your Kubera portfolio data.

    Credentials can be provided via:
    - Command-line options: --api-key and --secret
    - Environment variables: KUBERA_API_KEY and KUBERA_SECRET
    - Config file: ~/.env

    NOTES:
    - Update operations require API keys with update permissions enabled
    - Some API keys may be IP address restricted
    """
    ctx.ensure_object(dict)
    # Store credentials for lazy client initialization
    ctx.obj["api_key"] = api_key
    ctx.obj["secret"] = secret


def get_client(ctx: click.Context) -> KuberaClient:
    """Get or create a Kubera client from context.

    Args:
        ctx: Click context

    Returns:
        Initialized KuberaClient

    Raises:
        SystemExit: If client initialization fails
    """
    if "client" not in ctx.obj:
        try:
            ctx.obj["client"] = KuberaClient(
                api_key=ctx.obj.get("api_key"), secret=ctx.obj.get("secret")
            )
        except KuberaAPIError as e:
            print_error(f"Failed to initialize client: {e.message}")
            sys.exit(1)
    return ctx.obj["client"]


@cli.command()
@click.option("--raw", is_flag=True, help="Output raw JSON instead of formatted text")
@click.pass_context
def list(ctx: click.Context, raw: bool) -> None:
    """List all portfolios.

    Shows a summary of all your portfolios including their IDs, names, and currencies.
    Portfolio indexes can be used in other commands instead of GUIDs.

    Examples:
        kubera list
        kubera list --raw
    """
    client = get_client(ctx)

    try:
        portfolios = client.get_portfolios()
        # Save to cache for index-based lookups
        save_portfolio_cache(portfolios)
        print_portfolios(portfolios, raw=raw)  # type: ignore[arg-type]
    except KuberaAPIError as e:
        print_error(f"Failed to fetch portfolios: {e.message}")
        sys.exit(1)
    finally:
        client.close()


@cli.command()
@click.argument("portfolio_id")
@click.option("--raw", is_flag=True, help="Output raw JSON instead of formatted text")
@click.option("--tree", is_flag=True, help="Show as tree view")
@click.pass_context
def show(ctx: click.Context, portfolio_id: str, raw: bool, tree: bool) -> None:
    """Show detailed portfolio information.

    Displays comprehensive information about a specific portfolio including:
    - Net worth
    - Assets with values and tickers
    - Debts
    - Insurance
    - Documents

    PORTFOLIO_ID: The portfolio index (e.g., 1, 2, 3) or full ID

    Examples:
        kubera show 1
        kubera show abc123
        kubera show 1 --raw
        kubera show 2 --tree
    """
    client = get_client(ctx)

    try:
        # Resolve index to ID if needed
        resolved_id = resolve_portfolio_id(portfolio_id)
        if not resolved_id:
            print_error(
                f"Invalid portfolio identifier: '{portfolio_id}'. "
                f"Run 'kubera list' to see available portfolios."
            )
            sys.exit(1)

        portfolio = client.get_portfolio(resolved_id)

        if tree:
            print_asset_tree(portfolio)  # type: ignore[arg-type]
        else:
            print_portfolio(portfolio, raw=raw)  # type: ignore[arg-type]
    except KuberaAPIError as e:
        print_error(f"Failed to fetch portfolio: {e.message}")
        sys.exit(1)
    finally:
        client.close()


@cli.command()
@click.argument("portfolio_id")
@click.argument("category")
@click.argument("sheet_name")
@click.option("--raw", is_flag=True, help="Output raw JSON instead of formatted text")
@click.pass_context
def drill(
    ctx: click.Context, portfolio_id: str, category: str, sheet_name: str, raw: bool
) -> None:
    """Drill down into a specific sheet within a category.

    Shows detailed information for all items in a specific sheet, including:
    - Current value
    - Cost basis (if available)
    - Overall gains (value and percentage)
    - Daily gains (if available)
    - Quantity and ticker information

    PORTFOLIO_ID: The portfolio index (e.g., 1, 2, 3) or full ID
    CATEGORY: The category (asset, debt, insurance)
    SHEET_NAME: The sheet name (e.g., "Bank Accounts", "Investments")

    Examples:
        kubera drill 1 asset "Bank Accounts"
        kubera drill 2 asset "Investments"
        kubera drill 1 debt "Credit Cards"
    """
    client = get_client(ctx)

    try:
        # Resolve index to ID if needed
        resolved_id = resolve_portfolio_id(portfolio_id)
        if not resolved_id:
            print_error(
                f"Invalid portfolio identifier: '{portfolio_id}'. "
                f"Run 'kubera list' to see available portfolios."
            )
            sys.exit(1)

        portfolio = client.get_portfolio(resolved_id)

        # Get the items from the specified category
        if category.lower() == "asset":
            items = portfolio.get("asset", portfolio.get("assets", []))
        elif category.lower() == "debt":
            items = portfolio.get("debt", portfolio.get("debts", []))
        elif category.lower() == "insurance":
            items = portfolio.get("insurance", [])
        else:
            print_error(f"Invalid category: {category}. Use 'asset', 'debt', or 'insurance'")
            sys.exit(1)

        # Filter items by sheet name (case-insensitive)
        sheet_items = [
            item
            for item in items
            if item.get("sheetName", "").lower() == sheet_name.lower()
        ]

        if not sheet_items:
            print_error(
                f"No items found in sheet '{sheet_name}' for category '{category}'. "
                f"Check sheet name with 'kubera show {portfolio_id}'"
            )
            sys.exit(1)

        print_sheet_detail(
            sheet_items, sheet_name, category, portfolio.get("name", "Portfolio"), raw
        )

    except KuberaAPIError as e:
        print_error(f"Failed to fetch portfolio: {e.message}")
        sys.exit(1)
    finally:
        client.close()


@cli.command()
@click.argument("item_id")
@click.option("--name", help="New name for the item")
@click.option("--description", help="New description for the item")
@click.option("--value", type=float, help="New value for the item")
@click.option("--cost", type=float, help="New cost basis for the item")
@click.option("--raw", is_flag=True, help="Output raw JSON instead of formatted text")
@click.pass_context
def update(
    ctx: click.Context,
    item_id: str,
    name: str | None,
    description: str | None,
    value: float | None,
    cost: float | None,
    raw: bool,
) -> None:
    """Update an asset or debt item.

    Updates one or more fields of an existing asset or debt. Only provide the
    fields you want to update.

    ITEM_ID: The asset or debt ID

    IMPORTANT: This command requires an API key with UPDATE PERMISSIONS enabled.
    Read-only API keys will fail with a 403 error.

    Examples:
        kubera update item123 --value 50000
        kubera update item123 --name "Updated Name" --description "New description"
        kubera update item123 --value 50000 --cost 45000
    """
    client = get_client(ctx)

    # Build updates dictionary
    updates: dict[str, str | float] = {}
    if name is not None:
        updates["name"] = name
    if description is not None:
        updates["description"] = description
    if value is not None:
        updates["value"] = value
    if cost is not None:
        updates["cost"] = cost

    if not updates:
        print_error("No updates specified. Use --name, --description, --value, or --cost")
        sys.exit(1)

    try:
        updated_item = client.update_item(item_id, updates)  # type: ignore
        print_success(f"Successfully updated item: {updated_item.get('name', item_id)}")
        print_item(updated_item, raw=raw)
    except KuberaAPIError as e:
        print_error(f"Failed to update item: {e.message}")
        sys.exit(1)
    finally:
        client.close()


@cli.command()
@click.option("--raw", is_flag=True, help="Output raw JSON instead of formatted text")
@click.pass_context
def test(ctx: click.Context, raw: bool) -> None:
    """Test API connection and verify credentials.

    Tests your Kubera API connection by attempting to fetch portfolio data.
    Useful for diagnosing authentication issues or verifying initial setup.

    Examples:
        kubera test              # Human-readable output
        kubera test --raw        # JSON output
    """
    import json

    client = get_client(ctx)

    try:
        if not raw:
            click.echo("Testing Kubera API connection...\n")
            click.echo("→ Loading credentials...")

        # Test 1: Fetch portfolios
        if not raw:
            click.echo("→ Fetching portfolios...")
        portfolios = client.get_portfolios()

        if not raw:
            print_success(f"✓ Successfully connected to Kubera API!")
            print_success(f"✓ Found {len(portfolios)} portfolio(s)")

            if portfolios:
                click.echo("\nPortfolios:")
                for i, portfolio in enumerate(portfolios, 1):
                    click.echo(
                        f"  {i}. {portfolio['name']} "
                        f"(ID: {portfolio['id']}, Currency: {portfolio['currency']})"
                    )

                # Test 2: Fetch detailed data for first portfolio
                click.echo("\n→ Fetching detailed data for first portfolio...")
                portfolio_id = portfolios[0]["id"]
                portfolio_data = client.get_portfolio(portfolio_id)

                print_success(f"✓ Portfolio: {portfolio_data['name']}")
                click.echo(f"  - Assets: {len(portfolio_data.get('assets', []))}")
                click.echo(f"  - Debts: {len(portfolio_data.get('debts', []))}")
                click.echo(f"  - Insurance: {len(portfolio_data.get('insurance', []))}")

                net_worth = portfolio_data.get("net_worth", {})
                if net_worth:
                    amount = net_worth.get("amount", "N/A")
                    currency = portfolio_data["currency"]
                    click.echo(f"  - Net Worth: {amount} {currency}")

                click.echo("\n" + "=" * 50)
                print_success("✓ All tests passed! Your Kubera API client is working correctly.")
            else:
                click.echo("\nNo portfolios found (account may be empty).")
                print_success("✓ Connection successful, but no portfolios available.")

        else:
            # Raw JSON output
            result = {
                "status": "success",
                "portfolios_count": len(portfolios),
                "portfolios": portfolios,
            }

            if portfolios:
                portfolio_id = portfolios[0]["id"]
                portfolio_data = client.get_portfolio(portfolio_id)
                result["sample_portfolio"] = portfolio_data

            click.echo(json.dumps(result, indent=2))

    except KuberaAPIError as e:
        if raw:
            error_data = {
                "status": "error",
                "error": e.message,
                "status_code": e.status_code,
            }
            click.echo(json.dumps(error_data, indent=2))
        else:
            print_error(f"✗ API Error: {e.message}")
            if e.status_code:
                click.echo(f"  Status Code: {e.status_code}")
            click.echo("\nPlease check:")
            click.echo("  1. Your credentials in ~/.env are correct")
            click.echo("  2. KUBERA_API_KEY and KUBERA_SECRET are set")
            click.echo("  3. Your API key has not exceeded rate limits")
            click.echo("  4. Your IP address is allowed (if IP restrictions are enabled)")
            click.echo(
                "  5. API key has required permissions (read for list/show, "
                "update for modifications)"
            )
        sys.exit(1)
    except Exception as e:
        if raw:
            error_data = {"status": "error", "error": str(e)}
            click.echo(json.dumps(error_data, indent=2))
        else:
            print_error(f"✗ Unexpected error: {e}")
            click.echo("\nPlease check:")
            click.echo("  1. ~/.env file exists and contains KUBERA_API_KEY and KUBERA_SECRET")
            click.echo("  2. The credentials are valid")
        sys.exit(1)
    finally:
        client.close()


@cli.command()
@click.pass_context
def interactive(ctx: click.Context) -> None:
    """Interactive mode for exploring portfolios.

    Launches an interactive session where you can browse portfolios
    and their contents step by step.

    Examples:
        kubera interactive
    """
    client = get_client(ctx)

    try:
        # Get portfolios
        portfolios = client.get_portfolios()

        if not portfolios:
            print_error("No portfolios found.")
            return

        # Save to cache and show portfolios
        save_portfolio_cache(portfolios)
        print_portfolios(portfolios)  # type: ignore[arg-type]

        # Let user choose a portfolio
        click.echo("\nEnter portfolio index or ID to view details (or 'q' to quit): ", nl=False)
        portfolio_choice = input().strip()

        if portfolio_choice.lower() == "q":
            return

        # Resolve index to ID if needed
        resolved_id = resolve_portfolio_id(portfolio_choice)
        if not resolved_id:
            print_error(f"Invalid portfolio identifier: '{portfolio_choice}'")
            return

        portfolio = client.get_portfolio(resolved_id)

        print_portfolio(portfolio)  # type: ignore[arg-type]

        # Ask if user wants tree view
        click.echo("\nShow as tree view? (y/n): ", nl=False)
        if input().strip().lower() == "y":
            print_asset_tree(portfolio)  # type: ignore[arg-type]

    except KuberaAPIError as e:
        print_error(f"Error: {e.message}")
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo("\n\nGoodbye!")
    finally:
        client.close()


if __name__ == "__main__":
    cli()
