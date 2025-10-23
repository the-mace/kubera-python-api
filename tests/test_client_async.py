"""Tests for Kubera client async API methods."""

from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

from kubera import KuberaClient
from kubera.exceptions import (
    KuberaAPIError,
    KuberaAuthenticationError,
)
from tests.fixtures import (
    ERROR_RESPONSE_401,
    PORTFOLIO_DETAIL_RESPONSE,
    PORTFOLIOS_LIST_RESPONSE,
    UPDATE_ITEM_RESPONSE,
    wrap_api_response,
)


@pytest.fixture
def client():
    """Create a test client."""
    return KuberaClient(api_key="test_key", secret="test_secret")


@pytest.fixture
def mock_async_response():
    """Create a mock async HTTP response."""

    def _mock_response(status_code=200, json_data=None):
        response = Mock(spec=httpx.Response)
        response.status_code = status_code
        response.json.return_value = json_data or {}
        response.text = str(json_data) if json_data else ""
        return response

    return _mock_response


@pytest.mark.asyncio
class TestAsyncGetPortfolios:
    """Tests for aget_portfolios() async method."""

    async def test_aget_portfolios_success(self, client, mock_async_response):
        """Test async portfolio list retrieval."""
        response = mock_async_response(200, wrap_api_response(PORTFOLIOS_LIST_RESPONSE))

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.get.return_value = response

        with patch.object(client, "_get_async_client", return_value=mock_client):
            portfolios = await client.aget_portfolios()

        assert len(portfolios) == 3
        assert portfolios[0]["id"] == "portfolio_001"
        assert portfolios[0]["name"] == "Test Portfolio 1"

    async def test_aget_portfolios_empty(self, client, mock_async_response):
        """Test async portfolio list when empty."""
        response = mock_async_response(200, wrap_api_response([]))

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.get.return_value = response

        with patch.object(client, "_get_async_client", return_value=mock_client):
            portfolios = await client.aget_portfolios()

        assert portfolios == []

    async def test_aget_portfolios_auth_error(self, client, mock_async_response):
        """Test async portfolio list with auth error."""
        response = mock_async_response(401, ERROR_RESPONSE_401)

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.get.return_value = response

        with patch.object(client, "_get_async_client", return_value=mock_client):
            with pytest.raises(KuberaAuthenticationError):
                await client.aget_portfolios()


@pytest.mark.asyncio
class TestAsyncGetPortfolio:
    """Tests for aget_portfolio() async method."""

    async def test_aget_portfolio_success(self, client, mock_async_response):
        """Test async portfolio detail retrieval."""
        response = mock_async_response(200, wrap_api_response(PORTFOLIO_DETAIL_RESPONSE))

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.get.return_value = response

        with patch.object(client, "_get_async_client", return_value=mock_client):
            portfolio = await client.aget_portfolio("portfolio_001")

        assert "asset" in portfolio
        assert len(portfolio["asset"]) == 3
        assert portfolio["asset"][0]["type"] == "bank"

    async def test_aget_portfolio_not_found(self, client, mock_async_response):
        """Test async portfolio detail with non-existent ID."""
        error_response = {"errorCode": 404, "message": "Portfolio not found"}
        response = mock_async_response(404, error_response)

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.get.return_value = response

        with patch.object(client, "_get_async_client", return_value=mock_client):
            with pytest.raises(KuberaAPIError) as exc_info:
                await client.aget_portfolio("nonexistent")

        assert exc_info.value.status_code == 404


@pytest.mark.asyncio
class TestAsyncUpdateItem:
    """Tests for aupdate_item() async method."""

    async def test_aupdate_item_success(self, client, mock_async_response):
        """Test async item update."""
        response = mock_async_response(200, wrap_api_response(UPDATE_ITEM_RESPONSE))
        updates = {"value": 5500.00}

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.post.return_value = response

        with patch.object(client, "_get_async_client", return_value=mock_client):
            result = await client.aupdate_item("asset_001", updates)

        assert result["id"] == "asset_001"
        assert result["value"]["amount"] == 5500.00


@pytest.mark.asyncio
class TestAsyncContextManager:
    """Tests for async context manager."""

    async def test_async_context_manager(self):
        """Test client as async context manager."""
        async with KuberaClient(api_key="test_key", secret="test_secret") as client:
            assert isinstance(client, KuberaClient)
            assert client.api_key == "test_key"

    async def test_async_close(self):
        """Test async client cleanup."""
        client = KuberaClient(api_key="test_key", secret="test_secret")

        # Create async client
        _ = client._get_async_client()
        assert client._async_client is not None

        # Close should clean up
        await client.aclose()
        # Note: We can't easily verify the client was closed without more mocking
