"""Authentication utilities for Kubera API."""

import hashlib
import hmac
import json
import time
from typing import Any


def generate_signature(
    api_key: str,
    secret: str,
    http_method: str,
    request_path: str,
    body: dict[str, Any] | None = None,
    timestamp: str | None = None,
) -> tuple[str, str]:
    """Generate HMAC-SHA256 signature for Kubera API authentication.

    Args:
        api_key: Your Kubera API key
        secret: Your Kubera API secret
        http_method: HTTP method (GET, POST, etc.)
        request_path: API endpoint path (e.g., /api/v3/data/portfolio)
        body: Request body dictionary (for POST requests)
        timestamp: Unix timestamp in seconds (auto-generated if None)

    Returns:
        Tuple of (signature, timestamp)
    """
    if timestamp is None:
        timestamp = str(int(time.time()))

    # Prepare body data (compact JSON with no spaces)
    body_data = ""
    if body is not None:
        body_data = json.dumps(body, separators=(",", ":"))

    # Create signature data string
    data = f"{api_key}{timestamp}{http_method}{request_path}{body_data}"

    # Generate HMAC-SHA256 signature
    signature = hmac.new(
        secret.encode("utf-8"), data.encode("utf-8"), hashlib.sha256
    ).hexdigest()

    return signature, timestamp


def create_auth_headers(
    api_key: str,
    secret: str,
    http_method: str,
    request_path: str,
    body: dict[str, Any] | None = None,
) -> dict[str, str]:
    """Create authentication headers for Kubera API request.

    Args:
        api_key: Your Kubera API key
        secret: Your Kubera API secret
        http_method: HTTP method (GET, POST, etc.)
        request_path: API endpoint path
        body: Request body dictionary (for POST requests)

    Returns:
        Dictionary of authentication headers
    """
    signature, timestamp = generate_signature(api_key, secret, http_method, request_path, body)

    return {
        "x-api-token": api_key,
        "x-timestamp": timestamp,
        "x-signature": signature,
    }
