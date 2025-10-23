"""Type definitions for Kubera API models."""

from typing import Any, TypedDict


class ValueDict(TypedDict, total=False):
    """Represents a monetary value with currency."""

    amount: float
    currency: str


class ConnectionDict(TypedDict, total=False):
    """Represents account connection details."""

    aggregator: str
    provider: str
    last_updated: str
    account_id: str


class PortfolioSummary(TypedDict):
    """Represents a portfolio summary from the list endpoint."""

    id: str
    name: str
    currency: str


class ItemData(TypedDict, total=False):
    """Represents an asset, debt, or insurance item."""

    id: str
    name: str
    description: str | None
    value: ValueDict
    cost: ValueDict | None
    ticker: str | None
    quantity: float | None
    taxability: str | None
    connection: ConnectionDict | None
    parent_account: str | None


class UpdateItemRequest(TypedDict, total=False):
    """Request body for updating an item."""

    name: str
    description: str
    value: float
    cost: float


class PortfolioData(TypedDict, total=False):
    """Represents comprehensive portfolio data."""

    id: str
    name: str
    currency: str
    net_worth: ValueDict
    assets: list[ItemData]
    debts: list[ItemData]
    insurance: list[ItemData]
    documents: list[dict[str, Any]]
    allocation: dict[str, Any]
