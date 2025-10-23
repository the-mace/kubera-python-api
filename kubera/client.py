"""Kubera API client implementation."""

import os
import re
from typing import Any

import httpx
from dotenv import load_dotenv

from kubera.auth import create_auth_headers
from kubera.exceptions import (
    KuberaAPIError,
    KuberaAuthenticationError,
    KuberaRateLimitError,
    KuberaValidationError,
)
from kubera.types import PortfolioData, PortfolioSummary, UpdateItemRequest


def _load_env_with_export_support(env_path: str) -> None:
    """Load .env file that may contain 'export' statements.

    Python-dotenv doesn't handle 'export KEY=value' format, so we parse it manually
    if the standard load fails to find the variables.

    Args:
        env_path: Path to the .env file
    """
    if not os.path.exists(env_path):
        return

    # Try standard dotenv loading first
    load_dotenv(env_path)

    # If variables still not found, parse manually to handle 'export' format
    if not os.getenv("KUBERA_API_KEY") or not os.getenv("KUBERA_SECRET"):
        try:
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if not line or line.startswith("#"):
                        continue

                    # Match: export KEY=value or KEY=value
                    # Handle quoted and unquoted values
                    match = re.match(
                        r'^\s*(?:export\s+)?([A-Z_][A-Z0-9_]*)\s*=\s*["\']?([^"\'\n]*)["\']?\s*$',
                        line,
                    )
                    if match:
                        key, value = match.groups()
                        # Only set if not already in environment
                        if key in ("KUBERA_API_KEY", "KUBERA_SECRET") and not os.getenv(key):
                            os.environ[key] = value
        except Exception:
            # If manual parsing fails, just continue - standard dotenv may have worked
            pass


class KuberaClient:
    """Modern async/sync client for Kubera Data API v3.

    This client provides both synchronous and asynchronous methods for
    interacting with the Kubera API.

    Example:
        >>> client = KuberaClient()
        >>> portfolios = client.get_portfolios()
        >>> portfolio = client.get_portfolio(portfolios[0]['id'])
    """

    BASE_URL = "https://api.kubera.com"
    API_VERSION = "v3"

    def __init__(
        self,
        api_key: str | None = None,
        secret: str | None = None,
        base_url: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        """Initialize the Kubera client.

        Args:
            api_key: Kubera API key (defaults to KUBERA_API_KEY env var)
            secret: Kubera API secret (defaults to KUBERA_SECRET env var)
            base_url: Base URL for API (defaults to https://api.kubera.com)
            timeout: Request timeout in seconds

        Raises:
            KuberaAuthenticationError: If credentials are not provided
        """
        # First check if already set in environment (e.g., from sourced shell)
        self.api_key = api_key or os.getenv("KUBERA_API_KEY")
        self.secret = secret or os.getenv("KUBERA_SECRET")

        # If not found in environment, try loading from ~/.env file
        # This handles both standard format (KEY=value) and shell format (export KEY=value)
        if not self.api_key or not self.secret:
            _load_env_with_export_support(os.path.expanduser("~/.env"))
            self.api_key = self.api_key or os.getenv("KUBERA_API_KEY")
            self.secret = self.secret or os.getenv("KUBERA_SECRET")

        if not self.api_key or not self.secret:
            raise KuberaAuthenticationError(
                "API credentials not found. Please provide api_key and secret, "
                "or set KUBERA_API_KEY and KUBERA_SECRET environment variables."
            )

        self.base_url = base_url or self.BASE_URL
        self.timeout = timeout
        self._client = httpx.Client(timeout=timeout)
        self._async_client: httpx.AsyncClient | None = None

    def __enter__(self) -> "KuberaClient":
        """Context manager entry."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.close()

    async def __aenter__(self) -> "KuberaClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Async context manager exit."""
        await self.aclose()

    def close(self) -> None:
        """Close the synchronous HTTP client."""
        self._client.close()

    async def aclose(self) -> None:
        """Close the asynchronous HTTP client."""
        if self._async_client:
            await self._async_client.aclose()

    def _get_async_client(self) -> httpx.AsyncClient:
        """Get or create async client."""
        if self._async_client is None:
            self._async_client = httpx.AsyncClient(timeout=self.timeout)
        return self._async_client

    def _build_url(self, path: str) -> str:
        """Build full URL from path."""
        return f"{self.base_url}{path}"

    def _create_headers(
        self, method: str, path: str, body: dict[str, Any] | None = None
    ) -> dict[str, str]:
        """Create request headers with authentication."""
        # Type assertion safe because __init__ validates these are not None
        assert self.api_key is not None and self.secret is not None
        headers = create_auth_headers(self.api_key, self.secret, method, path, body)
        headers["Content-Type"] = "application/json"
        return headers

    def _handle_response(self, response: httpx.Response) -> Any:
        """Handle API response and raise appropriate exceptions."""
        if response.status_code == 200:
            data = response.json()
            # Kubera API wraps responses in {"data": ..., "errorCode": 0}
            # Extract the data field if present
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            return data

        # Handle error responses
        try:
            error_data = response.json()
            error_message = error_data.get("message", response.text)
        except Exception:
            error_message = response.text

        if response.status_code == 401:
            hint = (
                " Check: 1) Credentials are correct, "
                "2) IP address is allowed (some API keys have IP restrictions)"
            )
            raise KuberaAuthenticationError(
                f"Authentication failed: {error_message}.{hint}", response.status_code
            )
        elif response.status_code == 403:
            hint = (
                " Note: Update operations require an API key with update permissions enabled. "
                "Read-only API keys cannot modify data."
            )
            raise KuberaAPIError(
                f"Permission denied: {error_message}.{hint}", response.status_code
            )
        elif response.status_code == 429:
            raise KuberaRateLimitError(
                f"Rate limit exceeded: {error_message}. "
                "Limits: 30 req/min, 100/day (Essential) or 1000/day (Black)",
                response.status_code,
            )
        elif response.status_code == 400:
            raise KuberaValidationError(
                f"Validation error: {error_message}", response.status_code
            )
        else:
            raise KuberaAPIError(
                f"API error ({response.status_code}): {error_message}", response.status_code
            )

    # Synchronous methods

    def get_portfolios(self) -> list[PortfolioSummary]:
        """Get list of all portfolios.

        Returns:
            List of portfolio summaries with id, name, and currency

        Raises:
            KuberaAPIError: If the API request fails
        """
        path = f"/api/{self.API_VERSION}/data/portfolio"
        headers = self._create_headers("GET", path)

        response = self._client.get(self._build_url(path), headers=headers)
        return self._handle_response(response)

    def get_portfolio(self, portfolio_id: str) -> PortfolioData:
        """Get comprehensive data for a specific portfolio.

        Args:
            portfolio_id: The portfolio ID

        Returns:
            Complete portfolio data including assets, debts, and insurance

        Raises:
            KuberaAPIError: If the API request fails
        """
        path = f"/api/{self.API_VERSION}/data/portfolio/{portfolio_id}"
        headers = self._create_headers("GET", path)

        response = self._client.get(self._build_url(path), headers=headers)
        return self._handle_response(response)

    def update_item(self, item_id: str, updates: UpdateItemRequest) -> dict[str, Any]:
        """Update an asset or debt item.

        Args:
            item_id: The asset or debt ID
            updates: Dictionary with fields to update (name, description, value, cost)

        Returns:
            Updated item data

        Raises:
            KuberaAPIError: If the API request fails
            KuberaValidationError: If the update data is invalid
        """
        path = f"/api/{self.API_VERSION}/data/item/{item_id}"
        # Cast UpdateItemRequest to dict for headers
        body_dict: dict[str, Any] = dict(updates)
        headers = self._create_headers("POST", path, body_dict)

        response = self._client.post(self._build_url(path), headers=headers, json=updates)
        return self._handle_response(response)

    # Asynchronous methods

    async def aget_portfolios(self) -> list[PortfolioSummary]:
        """Async: Get list of all portfolios.

        Returns:
            List of portfolio summaries with id, name, and currency

        Raises:
            KuberaAPIError: If the API request fails
        """
        path = f"/api/{self.API_VERSION}/data/portfolio"
        headers = self._create_headers("GET", path)

        client = self._get_async_client()
        response = await client.get(self._build_url(path), headers=headers)
        return self._handle_response(response)

    async def aget_portfolio(self, portfolio_id: str) -> PortfolioData:
        """Async: Get comprehensive data for a specific portfolio.

        Args:
            portfolio_id: The portfolio ID

        Returns:
            Complete portfolio data including assets, debts, and insurance

        Raises:
            KuberaAPIError: If the API request fails
        """
        path = f"/api/{self.API_VERSION}/data/portfolio/{portfolio_id}"
        headers = self._create_headers("GET", path)

        client = self._get_async_client()
        response = await client.get(self._build_url(path), headers=headers)
        return self._handle_response(response)

    async def aupdate_item(self, item_id: str, updates: UpdateItemRequest) -> dict[str, Any]:
        """Async: Update an asset or debt item.

        Args:
            item_id: The asset or debt ID
            updates: Dictionary with fields to update (name, description, value, cost)

        Returns:
            Updated item data

        Raises:
            KuberaAPIError: If the API request fails
            KuberaValidationError: If the update data is invalid
        """
        path = f"/api/{self.API_VERSION}/data/item/{item_id}"
        # Cast UpdateItemRequest to dict for headers
        body_dict: dict[str, Any] = dict(updates)
        headers = self._create_headers("POST", path, body_dict)

        client = self._get_async_client()
        response = await client.post(self._build_url(path), headers=headers, json=updates)
        return self._handle_response(response)
