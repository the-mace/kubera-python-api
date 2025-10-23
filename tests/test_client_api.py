"""Tests for Kubera client API methods using real response fixtures."""

import pytest
import httpx
from unittest.mock import Mock, patch

from kubera import KuberaClient
from kubera.exceptions import (
    KuberaAPIError,
    KuberaAuthenticationError,
    KuberaRateLimitError,
    KuberaValidationError,
)
from tests.fixtures import (
    PORTFOLIOS_LIST_RESPONSE,
    PORTFOLIO_DETAIL_RESPONSE,
    UPDATE_ITEM_RESPONSE,
    ERROR_RESPONSE_401,
    ERROR_RESPONSE_403,
    ERROR_RESPONSE_429,
    ERROR_RESPONSE_400,
    wrap_api_response,
)


@pytest.fixture
def client():
    """Create a test client."""
    return KuberaClient(api_key="test_key", secret="test_secret")


@pytest.fixture
def mock_response():
    """Create a mock HTTP response."""
    def _mock_response(status_code=200, json_data=None):
        response = Mock(spec=httpx.Response)
        response.status_code = status_code
        response.json.return_value = json_data or {}
        response.text = str(json_data) if json_data else ""
        return response
    return _mock_response


class TestGetPortfolios:
    """Tests for get_portfolios() method."""

    def test_get_portfolios_success(self, client, mock_response):
        """Test successful portfolio list retrieval."""
        response = mock_response(200, wrap_api_response(PORTFOLIOS_LIST_RESPONSE))

        with patch.object(client._client, 'get', return_value=response):
            portfolios = client.get_portfolios()

        assert len(portfolios) == 3
        assert portfolios[0]["id"] == "portfolio_001"
        assert portfolios[0]["name"] == "Test Portfolio 1"
        assert portfolios[0]["currency"] == "USD"
        assert portfolios[1]["currency"] == "EUR"
        assert portfolios[2]["currency"] == "GBP"

    def test_get_portfolios_empty(self, client, mock_response):
        """Test portfolio list when no portfolios exist."""
        response = mock_response(200, wrap_api_response([]))

        with patch.object(client._client, 'get', return_value=response):
            portfolios = client.get_portfolios()

        assert portfolios == []

    def test_get_portfolios_authentication_error(self, client, mock_response):
        """Test portfolio list with authentication error."""
        response = mock_response(401, ERROR_RESPONSE_401)

        with patch.object(client._client, 'get', return_value=response):
            with pytest.raises(KuberaAuthenticationError) as exc_info:
                client.get_portfolios()

        assert "Authentication failed" in str(exc_info.value)
        assert "IP address" in str(exc_info.value)


class TestGetPortfolio:
    """Tests for get_portfolio() method."""

    def test_get_portfolio_success(self, client, mock_response):
        """Test successful portfolio detail retrieval."""
        response = mock_response(200, wrap_api_response(PORTFOLIO_DETAIL_RESPONSE))

        with patch.object(client._client, 'get', return_value=response):
            portfolio = client.get_portfolio("portfolio_001")

        # Check structure
        assert "asset" in portfolio
        assert "debt" in portfolio
        assert "insurance" in portfolio
        assert "netWorth" in portfolio

        # Check assets
        assert len(portfolio["asset"]) == 3
        bank_account = portfolio["asset"][0]
        assert bank_account["type"] == "bank"
        assert bank_account["subType"] == "cash"
        assert bank_account["value"]["amount"] == 5000.00
        assert "connection" in bank_account

        # Check stock with parent
        stock = portfolio["asset"][1]
        assert stock["ticker"] == "AAPL"
        assert stock["subType"] == "stock"
        assert "parent" in stock
        assert stock["parent"]["name"] == "Brokerage Account - 5678"
        assert "isin" in stock
        assert "rate" in stock

        # Check mutual fund with tax info
        fund = portfolio["asset"][2]
        assert fund["subType"] == "mutual fund"
        assert "cost" in fund
        assert "costBasisForTax" in fund
        assert "taxRate" in fund
        assert fund["taxRate"] == 30
        assert "taxOnUnrealizedGain" in fund
        assert "irr" in fund

        # Check debts
        assert len(portfolio["debt"]) == 1
        mortgage = portfolio["debt"][0]
        assert mortgage["subType"] == "mortgage"
        assert mortgage["value"]["amount"] == 250000.00

        # Check insurance
        assert len(portfolio["insurance"]) == 1
        insurance = portfolio["insurance"][0]
        assert insurance["subType"] == "life"
        assert insurance["value"]["amount"] == 500000.00

    def test_get_portfolio_not_found(self, client, mock_response):
        """Test portfolio detail with non-existent ID."""
        error_response = {"errorCode": 404, "message": "Portfolio not found"}
        response = mock_response(404, error_response)

        with patch.object(client._client, 'get', return_value=response):
            with pytest.raises(KuberaAPIError) as exc_info:
                client.get_portfolio("nonexistent")

        assert exc_info.value.status_code == 404


class TestUpdateItem:
    """Tests for update_item() method."""

    def test_update_item_success(self, client, mock_response):
        """Test successful item update."""
        response = mock_response(200, wrap_api_response(UPDATE_ITEM_RESPONSE))
        updates = {"value": 5500.00, "description": "Updated description"}

        with patch.object(client._client, 'post', return_value=response):
            result = client.update_item("asset_001", updates)

        assert result["id"] == "asset_001"
        assert result["name"] == "Updated Item Name"
        assert result["value"]["amount"] == 5500.00
        assert result["description"] == "Updated description"

    def test_update_item_partial(self, client, mock_response):
        """Test item update with only some fields."""
        response = mock_response(200, wrap_api_response(UPDATE_ITEM_RESPONSE))
        updates = {"value": 5500.00}

        with patch.object(client._client, 'post', return_value=response):
            result = client.update_item("asset_001", updates)

        assert result is not None

    def test_update_item_permission_denied(self, client, mock_response):
        """Test item update without proper permissions."""
        response = mock_response(403, ERROR_RESPONSE_403)
        updates = {"value": 5500.00}

        with patch.object(client._client, 'post', return_value=response):
            with pytest.raises(KuberaAPIError) as exc_info:
                client.update_item("asset_001", updates)

        assert exc_info.value.status_code == 403
        assert "Permission denied" in str(exc_info.value)
        assert "update permissions" in str(exc_info.value)

    def test_update_item_validation_error(self, client, mock_response):
        """Test item update with invalid data."""
        response = mock_response(400, ERROR_RESPONSE_400)
        updates = {"value": "invalid"}

        with patch.object(client._client, 'post', return_value=response):
            with pytest.raises(KuberaValidationError) as exc_info:
                client.update_item("asset_001", updates)

        assert exc_info.value.status_code == 400
        assert "Validation error" in str(exc_info.value)


class TestErrorHandling:
    """Tests for API error handling."""

    def test_rate_limit_error(self, client, mock_response):
        """Test rate limit exceeded error."""
        response = mock_response(429, ERROR_RESPONSE_429)

        with patch.object(client._client, 'get', return_value=response):
            with pytest.raises(KuberaRateLimitError) as exc_info:
                client.get_portfolios()

        assert exc_info.value.status_code == 429
        assert "Rate limit exceeded" in str(exc_info.value)
        assert "30 req/min" in str(exc_info.value)

    def test_generic_api_error(self, client, mock_response):
        """Test generic API error."""
        error_response = {"errorCode": 500, "message": "Internal server error"}
        response = mock_response(500, error_response)

        with patch.object(client._client, 'get', return_value=response):
            with pytest.raises(KuberaAPIError) as exc_info:
                client.get_portfolios()

        assert exc_info.value.status_code == 500
        assert "500" in str(exc_info.value)

    def test_error_without_json(self, client):
        """Test error response that doesn't contain valid JSON."""
        response = Mock(spec=httpx.Response)
        response.status_code = 500
        response.text = "Internal Server Error"
        response.json.side_effect = Exception("Not JSON")

        with patch.object(client._client, 'get', return_value=response):
            with pytest.raises(KuberaAPIError) as exc_info:
                client.get_portfolios()

        assert "Internal Server Error" in str(exc_info.value)


class TestResponseHandling:
    """Tests for response handling and data extraction."""

    def test_wrapped_response(self, client, mock_response):
        """Test extraction of data from wrapped response."""
        wrapped = wrap_api_response(PORTFOLIOS_LIST_RESPONSE)
        response = mock_response(200, wrapped)

        with patch.object(client._client, 'get', return_value=response):
            portfolios = client.get_portfolios()

        # Should extract the "data" field
        assert portfolios == PORTFOLIOS_LIST_RESPONSE

    def test_unwrapped_response(self, client, mock_response):
        """Test handling of response without data wrapper."""
        response = mock_response(200, PORTFOLIOS_LIST_RESPONSE)

        with patch.object(client._client, 'get', return_value=response):
            portfolios = client.get_portfolios()

        # Should work even without wrapper
        assert portfolios == PORTFOLIOS_LIST_RESPONSE
