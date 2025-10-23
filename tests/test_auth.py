"""Tests for authentication utilities."""

import time

from kubera.auth import create_auth_headers, generate_signature


def test_generate_signature_get_request() -> None:
    """Test signature generation for GET request."""
    api_key = "test_key"
    secret = "test_secret"
    timestamp = "1234567890"

    signature, returned_timestamp = generate_signature(
        api_key=api_key,
        secret=secret,
        http_method="GET",
        request_path="/api/v3/data/portfolio",
        timestamp=timestamp,
    )

    assert isinstance(signature, str)
    assert len(signature) == 64  # SHA256 hex digest length
    assert returned_timestamp == timestamp


def test_generate_signature_post_request() -> None:
    """Test signature generation for POST request with body."""
    api_key = "test_key"
    secret = "test_secret"
    timestamp = "1234567890"
    body = {"value": 400}

    signature, returned_timestamp = generate_signature(
        api_key=api_key,
        secret=secret,
        http_method="POST",
        request_path="/api/v3/data/item/123",
        body=body,
        timestamp=timestamp,
    )

    assert isinstance(signature, str)
    assert len(signature) == 64
    assert returned_timestamp == timestamp


def test_generate_signature_auto_timestamp() -> None:
    """Test that timestamp is auto-generated when not provided."""
    before = int(time.time())

    signature, timestamp = generate_signature(
        api_key="key", secret="secret", http_method="GET", request_path="/test"
    )

    after = int(time.time())

    assert isinstance(signature, str)
    assert before <= int(timestamp) <= after


def test_create_auth_headers() -> None:
    """Test creation of authentication headers."""
    headers = create_auth_headers(
        api_key="test_key", secret="test_secret", http_method="GET", request_path="/api/v3/test"
    )

    assert "x-api-token" in headers
    assert "x-timestamp" in headers
    assert "x-signature" in headers
    assert headers["x-api-token"] == "test_key"
    assert len(headers["x-signature"]) == 64


def test_signature_consistency() -> None:
    """Test that same inputs produce same signature."""
    api_key = "test_key"
    secret = "test_secret"
    timestamp = "1234567890"
    path = "/api/v3/data/portfolio"

    sig1, _ = generate_signature(api_key, secret, "GET", path, timestamp=timestamp)
    sig2, _ = generate_signature(api_key, secret, "GET", path, timestamp=timestamp)

    assert sig1 == sig2


def test_signature_changes_with_body() -> None:
    """Test that different bodies produce different signatures."""
    api_key = "test_key"
    secret = "test_secret"
    timestamp = "1234567890"
    path = "/api/v3/data/item/123"

    sig1, _ = generate_signature(
        api_key, secret, "POST", path, body={"value": 100}, timestamp=timestamp
    )
    sig2, _ = generate_signature(
        api_key, secret, "POST", path, body={"value": 200}, timestamp=timestamp
    )

    assert sig1 != sig2
