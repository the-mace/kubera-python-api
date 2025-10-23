"""Cache management for portfolio ID mapping."""

import json
from pathlib import Path
from typing import Any


def get_cache_file() -> Path:
    """Get the cache file path.

    Returns:
        Path to the cache file
    """
    cache_dir = Path.home() / ".kubera"
    cache_dir.mkdir(exist_ok=True)
    return cache_dir / "portfolio_cache.json"


def save_portfolio_cache(portfolios: list[dict[str, Any]]) -> None:
    """Save portfolio list to cache for index-based lookups.

    Args:
        portfolios: List of portfolio dictionaries
    """
    cache_file = get_cache_file()
    cache_data = {
        "portfolios": [
            {
                "id": p.get("id"),
                "name": p.get("name"),
                "currency": p.get("currency"),
            }
            for p in portfolios
        ]
    }
    with open(cache_file, "w") as f:
        json.dump(cache_data, f, indent=2)


def load_portfolio_cache() -> list[dict[str, Any]]:
    """Load portfolio list from cache.

    Returns:
        List of cached portfolios, or empty list if cache doesn't exist
    """
    cache_file = get_cache_file()
    if not cache_file.exists():
        return []

    try:
        with open(cache_file, "r") as f:
            cache_data = json.load(f)
            return cache_data.get("portfolios", [])
    except (json.JSONDecodeError, IOError):
        return []


def resolve_portfolio_id(id_or_index: str) -> str | None:
    """Resolve a portfolio index or ID to an ID.

    Args:
        id_or_index: Either a numeric index (1, 2, 3...) or a portfolio ID (GUID)

    Returns:
        Portfolio ID if found, None otherwise
    """
    # Check if it looks like a GUID (contains hyphens and is 36 chars)
    if "-" in id_or_index and len(id_or_index) == 36:
        return id_or_index

    # Try to parse as an index
    try:
        index = int(id_or_index)
        portfolios = load_portfolio_cache()
        if 1 <= index <= len(portfolios):
            return portfolios[index - 1]["id"]
    except (ValueError, IndexError, KeyError):
        pass

    return None
