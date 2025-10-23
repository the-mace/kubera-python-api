"""Output formatters for CLI."""

import json
from typing import Any

from rich.console import Console
from rich.table import Table
from rich.tree import Tree


def format_currency(amount: float | None, currency: str) -> str:
    """Format a currency value for display.

    Args:
        amount: The numeric amount
        currency: The currency code

    Returns:
        Formatted currency string
    """
    if amount is None:
        return "N/A"
    return f"{currency} {amount:,.2f}"


def format_number(value: float | int | str) -> str:
    """Format a number with commas for display.

    Args:
        value: The numeric value

    Returns:
        Formatted number string with commas
    """
    if not value:
        return ""
    if isinstance(value, str):
        try:
            value = float(value)
        except ValueError:
            return str(value)
    if isinstance(value, float):
        # Remove trailing zeros after decimal point
        formatted = f"{value:,.4f}".rstrip('0').rstrip('.')
        return formatted
    return f"{value:,}"


def print_portfolios(portfolios: list[dict[str, Any]], raw: bool = False) -> None:
    """Print portfolio list in human-readable or raw format.

    Args:
        portfolios: List of portfolio dictionaries
        raw: If True, output raw JSON
    """
    if raw:
        print(json.dumps(portfolios, indent=2))
        return

    console = Console()

    if not portfolios:
        console.print("[yellow]No portfolios found.[/yellow]")
        return

    table = Table(title=f"Portfolios ({len(portfolios)})", show_header=True)
    table.add_column("#", style="magenta", justify="right")
    table.add_column("Name", style="green")
    table.add_column("Currency", style="yellow")
    table.add_column("ID", style="dim cyan")

    for idx, portfolio in enumerate(portfolios, 1):
        table.add_row(
            str(idx),
            portfolio.get("name", "N/A"),
            portfolio.get("currency", "N/A"),
            portfolio.get("id", "N/A"),
        )

    console.print(table)
    console.print("\n[dim]Tip: Use the index number (e.g., 'kubera show 1') instead of the full ID[/dim]")


def print_portfolio(portfolio: dict[str, Any], raw: bool = False) -> None:
    """Print detailed portfolio information.

    Shows top-level categories (Assets, Debts, etc.) and sheets with totals,
    but not individual items.

    Args:
        portfolio: Portfolio dictionary
        raw: If True, output raw JSON
    """
    if raw:
        print(json.dumps(portfolio, indent=2))
        return

    console = Console()

    # Header
    console.print(f"\n[bold cyan]{portfolio.get('name', 'Portfolio')}[/bold cyan]")
    console.print(f"[dim]ID: {portfolio.get('id', 'N/A')}[/dim]")

    # Net Worth - API returns netWorth as a number
    net_worth_amount = portfolio.get("netWorth")
    if net_worth_amount is not None:
        # Currency is at portfolio level, not in netWorth
        currency = "USD"  # Kubera API seems to use USD as base
        console.print(
            f"\n[bold green]Net Worth:[/bold green] {format_currency(net_worth_amount, currency)}"
        )

    # Assets - API uses 'asset' not 'assets'
    assets = portfolio.get("asset", portfolio.get("assets", []))
    if assets:
        asset_total = portfolio.get("assetTotal")
        total_str = f" - Total: {format_currency(asset_total, 'USD')}" if asset_total is not None else ""
        console.print(f"\n[bold]Assets ({len(assets)} items){total_str}[/bold]")

        # Group by sheet
        by_sheet: dict[str, tuple[list[Any], float]] = {}
        for asset in assets:
            sheet = asset.get("sheetName", "Other")
            value = asset.get("value", {})
            amount = value.get("amount", 0) or 0

            if sheet not in by_sheet:
                by_sheet[sheet] = ([], 0)
            items, total = by_sheet[sheet]
            items.append(asset)
            by_sheet[sheet] = (items, total + amount)

        # Display sheets with totals
        sheet_table = Table(show_header=True, show_lines=False)
        sheet_table.add_column("Sheet", style="cyan")
        sheet_table.add_column("Items", justify="right")
        sheet_table.add_column("Total Value", style="green", justify="right")

        for sheet_name, (items, total) in by_sheet.items():
            currency = items[0].get("value", {}).get("currency", "USD") if items else "USD"
            sheet_table.add_row(
                sheet_name,
                str(len(items)),
                format_currency(total, currency)
            )

        console.print(sheet_table)

    # Debts - API uses 'debt' not 'debts'
    debts = portfolio.get("debt", portfolio.get("debts", []))
    if debts:
        debt_total = portfolio.get("debtTotal")
        total_str = f" - Total: {format_currency(debt_total, 'USD')}" if debt_total is not None else ""
        console.print(f"\n[bold]Debts ({len(debts)} items){total_str}[/bold]")

        # Group by sheet
        by_sheet_debt: dict[str, tuple[list[Any], float]] = {}
        for debt in debts:
            sheet = debt.get("sheetName", "Other")
            value = debt.get("value", {})
            amount = value.get("amount", 0) or 0

            if sheet not in by_sheet_debt:
                by_sheet_debt[sheet] = ([], 0)
            items, total = by_sheet_debt[sheet]
            items.append(debt)
            by_sheet_debt[sheet] = (items, total + amount)

        # Display sheets with totals
        debt_sheet_table = Table(show_header=True, show_lines=False)
        debt_sheet_table.add_column("Sheet", style="cyan")
        debt_sheet_table.add_column("Items", justify="right")
        debt_sheet_table.add_column("Total Value", style="red", justify="right")

        for sheet_name, (items, total) in by_sheet_debt.items():
            currency = items[0].get("value", {}).get("currency", "USD") if items else "USD"
            debt_sheet_table.add_row(
                sheet_name,
                str(len(items)),
                format_currency(total, currency)
            )

        console.print(debt_sheet_table)

    # Insurance
    insurance = portfolio.get("insurance", [])
    if insurance:
        # Calculate total
        ins_total = sum(ins.get("value", {}).get("amount", 0) or 0 for ins in insurance)
        total_str = f" - Total: {format_currency(ins_total, 'USD')}" if ins_total else ""
        console.print(f"\n[bold]Insurance ({len(insurance)} items){total_str}[/bold]")

        # Group by sheet if available
        by_sheet_ins: dict[str, tuple[list[Any], float]] = {}
        for ins in insurance:
            sheet = ins.get("sheetName", "Other")
            value = ins.get("value", {})
            amount = value.get("amount", 0) or 0

            if sheet not in by_sheet_ins:
                by_sheet_ins[sheet] = ([], 0)
            items, total = by_sheet_ins[sheet]
            items.append(ins)
            by_sheet_ins[sheet] = (items, total + amount)

        if len(by_sheet_ins) > 1:  # Only show sheets if there's more than one
            ins_sheet_table = Table(show_header=True, show_lines=False)
            ins_sheet_table.add_column("Sheet", style="cyan")
            ins_sheet_table.add_column("Items", justify="right")
            ins_sheet_table.add_column("Total Value", style="blue", justify="right")

            for sheet_name, (items, total) in by_sheet_ins.items():
                currency = items[0].get("value", {}).get("currency", "USD") if items else "USD"
                ins_sheet_table.add_row(
                    sheet_name,
                    str(len(items)),
                    format_currency(total, currency)
                )

            console.print(ins_sheet_table)

    # Documents - API uses 'document' not 'documents'
    documents = portfolio.get("document", portfolio.get("documents", []))
    if documents:
        console.print(f"\n[bold]Documents:[/bold] {len(documents)} documents")

    console.print()


def print_asset_tree(portfolio: dict[str, Any]) -> None:
    """Print asset allocation as a tree view.

    Args:
        portfolio: Portfolio dictionary
    """
    console = Console()

    # Header with net worth
    net_worth_amount = portfolio.get("netWorth")
    net_worth_str = ""
    if net_worth_amount is not None:
        net_worth_str = f" - Net Worth: {format_currency(net_worth_amount, 'USD')}"

    tree = Tree(f"[bold]{portfolio.get('name', 'Portfolio')}{net_worth_str}[/bold]")

    # Assets - API uses 'asset' not 'assets'
    assets = portfolio.get("asset", portfolio.get("assets", []))
    if assets:
        asset_total = portfolio.get("assetTotal")
        total_str = ""
        if asset_total is not None:
            total_str = f" - Total: {format_currency(asset_total, 'USD')}"

        asset_branch = tree.add(f"[cyan]Assets ({len(assets)}){total_str}[/cyan]")

        # Group by sheet/type for better organization
        by_sheet: dict[str, list[Any]] = {}
        for asset in assets:
            sheet = asset.get("sheetName", "Other")
            if sheet not in by_sheet:
                by_sheet[sheet] = []
            by_sheet[sheet].append(asset)

        for sheet_name, sheet_assets in list(by_sheet.items())[:5]:  # Show first 5 sheets
            sheet_branch = asset_branch.add(f"[yellow]{sheet_name}[/yellow]")
            for asset in sheet_assets[:10]:  # Show first 10 per sheet
                value = asset.get("value", {})
                name = asset.get("name", "Unknown")
                amount = format_currency(value.get("amount"), value.get("currency", "USD"))
                sheet_branch.add(f"{name}: {amount}")
            if len(sheet_assets) > 10:
                sheet_branch.add(f"[dim]... {len(sheet_assets) - 10} more[/dim]")

        if len(by_sheet) > 5:
            asset_branch.add(f"[dim]... {len(by_sheet) - 5} more categories[/dim]")

    # Debts - API uses 'debt' not 'debts'
    debts = portfolio.get("debt", portfolio.get("debts", []))
    if debts:
        debt_total = portfolio.get("debtTotal")
        total_str = ""
        if debt_total is not None:
            total_str = f" - Total: {format_currency(debt_total, 'USD')}"

        debt_branch = tree.add(f"[red]Debts ({len(debts)}){total_str}[/red]")
        for debt in debts[:10]:
            value = debt.get("value", {})
            name = debt.get("name", "Unknown")
            amount = format_currency(value.get("amount"), value.get("currency", "USD"))
            debt_branch.add(f"{name}: {amount}")
        if len(debts) > 10:
            debt_branch.add(f"[dim]... {len(debts) - 10} more[/dim]")

    # Insurance
    insurance = portfolio.get("insurance", [])
    if insurance:
        ins_branch = tree.add(f"[blue]Insurance ({len(insurance)})[/blue]")
        for ins in insurance[:10]:
            value = ins.get("value", {})
            name = ins.get("name", "Unknown")
            amount = format_currency(value.get("amount"), value.get("currency", "USD"))
            ins_branch.add(f"{name}: {amount}")
        if len(insurance) > 10:
            ins_branch.add(f"[dim]... {len(insurance) - 10} more[/dim]")

    console.print(tree)


def print_item(item: dict[str, Any], raw: bool = False) -> None:
    """Print item details.

    Args:
        item: Item dictionary
        raw: If True, output raw JSON
    """
    if raw:
        print(json.dumps(item, indent=2))
        return

    console = Console()

    console.print(f"\n[bold cyan]{item.get('name', 'Item')}[/bold cyan]")
    console.print(f"[dim]ID: {item.get('id', 'N/A')}[/dim]")

    if "value" in item:
        value = item["value"]
        console.print(
            f"[bold]Value:[/bold] {format_currency(value.get('amount'), value.get('currency', ''))}"
        )

    if "cost" in item and item["cost"]:
        cost = item["cost"]
        console.print(
            f"[bold]Cost:[/bold] {format_currency(cost.get('amount'), cost.get('currency', ''))}"
        )

    if "description" in item and item["description"]:
        console.print(f"[bold]Description:[/bold] {item['description']}")

    if "ticker" in item and item["ticker"]:
        console.print(f"[bold]Ticker:[/bold] {item['ticker']}")

    if "quantity" in item and item["quantity"]:
        console.print(f"[bold]Quantity:[/bold] {item['quantity']}")

    console.print()


def print_success(message: str) -> None:
    """Print a success message.

    Args:
        message: Success message
    """
    console = Console()
    console.print(f"[green]✓[/green] {message}")


def print_sheet_detail(
    items: list[dict[str, Any]], sheet_name: str, category: str, portfolio_name: str, raw: bool = False
) -> None:
    """Print detailed information for items in a sheet.

    Shows individual items with value, cost basis, and gains, grouped by sections.

    Args:
        items: List of item dictionaries from a specific sheet
        sheet_name: Name of the sheet
        category: Category name (asset, debt, insurance)
        portfolio_name: Name of the portfolio
        raw: If True, output raw JSON
    """
    if raw:
        print(json.dumps(items, indent=2))
        return

    console = Console()

    # Header
    console.print(f"\n[bold cyan]{portfolio_name}[/bold cyan]")
    console.print(f"[bold]{category.title()}: {sheet_name}[/bold]")

    # Filter out parent accounts to avoid double-counting in totals
    parent_ids = {item.get("parent", {}).get("id") for item in items if "parent" in item}
    items_for_totals = [item for item in items if item.get("id") not in parent_ids]

    # Calculate totals (excluding parent accounts)
    total_value = sum(item.get("value", {}).get("amount", 0) or 0 for item in items_for_totals)
    total_cost = sum(item.get("cost", {}).get("amount", 0) or 0 for item in items_for_totals if "cost" in item)

    # Overall gains
    if total_cost > 0:
        total_gain = total_value - total_cost
        total_gain_pct = (total_gain / total_cost) * 100
        gain_color = "green" if total_gain >= 0 else "red"
        gain_sign = "+" if total_gain >= 0 else ""
        console.print(
            f"\n[bold]Total Value:[/bold] {format_currency(total_value, 'USD')} | "
            f"[bold]Cost Basis:[/bold] {format_currency(total_cost, 'USD')} | "
            f"[bold {gain_color}]Gain:[/bold {gain_color}] {gain_sign}{format_currency(total_gain, 'USD')} "
            f"({gain_sign}{total_gain_pct:.2f}%)"
        )
    else:
        console.print(f"\n[bold]Total Value:[/bold] {format_currency(total_value, 'USD')}")

    # Group by section (excluding parent accounts)
    by_section: dict[str, list[dict[str, Any]]] = {}
    for item in items:
        if item.get("id") not in parent_ids:  # Skip parent accounts
            section = item.get("sectionName", "Other")
            if section not in by_section:
                by_section[section] = []
            by_section[section].append(item)

    console.print(f"\n[dim]Total Items: {len(items_for_totals)} across {len(by_section)} section(s)[/dim]")

    # Display each section
    for section_name, section_items in by_section.items():
        # Section header with totals (items already filtered, no parents)
        section_value = sum(item.get("value", {}).get("amount", 0) or 0 for item in section_items)
        section_cost = sum(item.get("cost", {}).get("amount", 0) or 0 for item in section_items if "cost" in item)

        console.print(f"\n[bold yellow]{section_name}[/bold yellow] ({len(section_items)} items)")

        if section_cost > 0:
            section_gain = section_value - section_cost
            section_gain_pct = (section_gain / section_cost) * 100
            gain_color = "green" if section_gain >= 0 else "red"
            gain_sign = "+" if section_gain >= 0 else ""
            console.print(
                f"[dim]Value: {format_currency(section_value, 'USD')} | "
                f"Cost: {format_currency(section_cost, 'USD')} | "
                f"[{gain_color}]Gain: {gain_sign}{format_currency(section_gain, 'USD')} "
                f"({gain_sign}{section_gain_pct:.2f}%)[/{gain_color}][/dim]"
            )
        else:
            console.print(f"[dim]Value: {format_currency(section_value, 'USD')}[/dim]")

        # Detect which columns have data in this section
        has_ticker = any(item.get("ticker") for item in section_items)
        has_quantity = any(item.get("quantity") for item in section_items)
        has_cost = any("cost" in item and item.get("cost", {}).get("amount") for item in section_items)

        # Create table for this section with only relevant columns
        table = Table(show_header=True, show_lines=False, box=None)
        table.add_column("Name", style="cyan")
        table.add_column("Value", style="green", justify="right")
        if has_ticker:
            table.add_column("Ticker", style="yellow")
        if has_quantity:
            table.add_column("Quantity", justify="right")
        if has_cost:
            table.add_column("Cost Basis", justify="right")
            table.add_column("Gain/Loss", justify="right")
            table.add_column("Gain %", justify="right")

        # section_items are already filtered (no parent accounts)
        for item in section_items:
            name = item.get("name", "N/A")
            value = item.get("value", {})
            value_amount = value.get("amount", 0) or 0
            currency = value.get("currency", "USD")
            ticker = item.get("ticker", "")
            quantity = item.get("quantity", "")

            # Build row dynamically based on which columns are present
            row = [name, format_currency(value_amount, currency)]

            if has_ticker:
                row.append(ticker)

            if has_quantity:
                qty_str = format_number(quantity) if quantity else ""
                row.append(qty_str)

            if has_cost:
                # Cost basis and gains
                cost_str = ""
                gain_str = ""
                gain_pct_str = ""

                if "cost" in item:
                    cost = item["cost"]
                    cost_amount = cost.get("amount", 0) or 0
                    cost_str = format_currency(cost_amount, currency)

                    if cost_amount > 0:
                        gain = value_amount - cost_amount
                        gain_pct = (gain / cost_amount) * 100
                        gain_color = "green" if gain >= 0 else "red"
                        gain_sign = "+" if gain >= 0 else ""

                        gain_str = f"[{gain_color}]{gain_sign}{format_currency(gain, currency)}[/{gain_color}]"
                        gain_pct_str = f"[{gain_color}]{gain_sign}{gain_pct:.2f}%[/{gain_color}]"

                row.extend([cost_str, gain_str, gain_pct_str])

            table.add_row(*row)

        console.print(table)

    console.print()


def print_error(message: str) -> None:
    """Print an error message.

    Args:
        message: Error message
    """
    console = Console()
    console.print(f"[red]✗[/red] {message}", style="red")
