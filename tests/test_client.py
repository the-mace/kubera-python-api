"""Tests for Kubera client."""

import os
from unittest.mock import patch

import pytest

from kubera import KuberaClient
from kubera.exceptions import KuberaAuthenticationError


def test_client_init_with_credentials() -> None:
    """Test client initialization with explicit credentials."""
    client = KuberaClient(api_key="test_key", secret="test_secret")

    assert client.api_key == "test_key"
    assert client.secret == "test_secret"
    assert client.base_url == "https://api.kubera.com"
    assert client.timeout == 30.0


def test_client_init_with_custom_base_url() -> None:
    """Test client initialization with custom base URL."""
    client = KuberaClient(
        api_key="test_key", secret="test_secret", base_url="https://custom.api.com"
    )

    assert client.base_url == "https://custom.api.com"


def test_client_init_with_custom_timeout() -> None:
    """Test client initialization with custom timeout."""
    client = KuberaClient(api_key="test_key", secret="test_secret", timeout=60.0)

    assert client.timeout == 60.0


def test_client_init_from_env_vars() -> None:
    """Test client initialization from environment variables."""
    with patch.dict(os.environ, {"KUBERA_API_KEY": "env_key", "KUBERA_SECRET": "env_secret"}):
        client = KuberaClient()

        assert client.api_key == "env_key"
        assert client.secret == "env_secret"


def test_client_init_missing_credentials() -> None:
    """Test that initialization fails without credentials."""
    # Clear environment and mock the file loading to ensure no credentials are found
    with patch.dict(os.environ, {}, clear=True):
        with patch("kubera.client._load_env_with_export_support"):
            with pytest.raises(KuberaAuthenticationError) as exc_info:
                KuberaClient()

            assert "API credentials not found" in str(exc_info.value)


def test_client_context_manager() -> None:
    """Test client as context manager."""
    with KuberaClient(api_key="test_key", secret="test_secret") as client:
        assert isinstance(client, KuberaClient)
        assert client.api_key == "test_key"


def test_build_url() -> None:
    """Test URL building."""
    client = KuberaClient(api_key="test_key", secret="test_secret")

    url = client._build_url("/api/v3/data/portfolio")
    assert url == "https://api.kubera.com/api/v3/data/portfolio"


def test_create_headers() -> None:
    """Test header creation."""
    client = KuberaClient(api_key="test_key", secret="test_secret")

    headers = client._create_headers("GET", "/api/v3/data/portfolio")

    assert "x-api-token" in headers
    assert "x-timestamp" in headers
    assert "x-signature" in headers
    assert "Content-Type" in headers
    assert headers["Content-Type"] == "application/json"
