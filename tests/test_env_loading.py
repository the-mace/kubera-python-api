"""Tests for environment variable loading with export support."""

import os
import tempfile
from pathlib import Path

from kubera.client import _load_env_with_export_support


def test_load_env_standard_format() -> None:
    """Test loading .env file in standard format (KEY=value)."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write("KUBERA_API_KEY=test_key\n")
        f.write("KUBERA_SECRET=test_secret\n")
        temp_path = f.name

    try:
        # Clear any existing values
        os.environ.pop("KUBERA_API_KEY", None)
        os.environ.pop("KUBERA_SECRET", None)

        _load_env_with_export_support(temp_path)

        assert os.getenv("KUBERA_API_KEY") == "test_key"
        assert os.getenv("KUBERA_SECRET") == "test_secret"
    finally:
        Path(temp_path).unlink()
        os.environ.pop("KUBERA_API_KEY", None)
        os.environ.pop("KUBERA_SECRET", None)


def test_load_env_export_format() -> None:
    """Test loading .env file with export statements."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write("export KUBERA_API_KEY=test_key_export\n")
        f.write("export KUBERA_SECRET=test_secret_export\n")
        temp_path = f.name

    try:
        # Clear any existing values
        os.environ.pop("KUBERA_API_KEY", None)
        os.environ.pop("KUBERA_SECRET", None)

        _load_env_with_export_support(temp_path)

        assert os.getenv("KUBERA_API_KEY") == "test_key_export"
        assert os.getenv("KUBERA_SECRET") == "test_secret_export"
    finally:
        Path(temp_path).unlink()
        os.environ.pop("KUBERA_API_KEY", None)
        os.environ.pop("KUBERA_SECRET", None)


def test_load_env_mixed_format() -> None:
    """Test loading .env file with both formats and comments."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write("# This is a comment\n")
        f.write("export KUBERA_API_KEY=test_key_mixed\n")
        f.write("\n")
        f.write("KUBERA_SECRET=test_secret_mixed\n")
        f.write("# Another comment\n")
        temp_path = f.name

    try:
        # Clear any existing values
        os.environ.pop("KUBERA_API_KEY", None)
        os.environ.pop("KUBERA_SECRET", None)

        _load_env_with_export_support(temp_path)

        assert os.getenv("KUBERA_API_KEY") == "test_key_mixed"
        assert os.getenv("KUBERA_SECRET") == "test_secret_mixed"
    finally:
        Path(temp_path).unlink()
        os.environ.pop("KUBERA_API_KEY", None)
        os.environ.pop("KUBERA_SECRET", None)


def test_load_env_quoted_values() -> None:
    """Test loading .env file with quoted values."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write('export KUBERA_API_KEY="test_key_quoted"\n')
        f.write("KUBERA_SECRET='test_secret_quoted'\n")
        temp_path = f.name

    try:
        # Clear any existing values
        os.environ.pop("KUBERA_API_KEY", None)
        os.environ.pop("KUBERA_SECRET", None)

        _load_env_with_export_support(temp_path)

        assert os.getenv("KUBERA_API_KEY") == "test_key_quoted"
        assert os.getenv("KUBERA_SECRET") == "test_secret_quoted"
    finally:
        Path(temp_path).unlink()
        os.environ.pop("KUBERA_API_KEY", None)
        os.environ.pop("KUBERA_SECRET", None)


def test_load_env_respects_existing_env_vars() -> None:
    """Test that existing environment variables take precedence."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write("export KUBERA_API_KEY=file_key\n")
        f.write("export KUBERA_SECRET=file_secret\n")
        temp_path = f.name

    try:
        # Set environment variables before loading
        os.environ["KUBERA_API_KEY"] = "env_key"
        os.environ["KUBERA_SECRET"] = "env_secret"

        _load_env_with_export_support(temp_path)

        # Environment variables should not be overwritten
        assert os.getenv("KUBERA_API_KEY") == "env_key"
        assert os.getenv("KUBERA_SECRET") == "env_secret"
    finally:
        Path(temp_path).unlink()
        os.environ.pop("KUBERA_API_KEY", None)
        os.environ.pop("KUBERA_SECRET", None)


def test_load_env_nonexistent_file() -> None:
    """Test that loading nonexistent file doesn't raise error."""
    _load_env_with_export_support("/nonexistent/path/.env")
    # Should not raise any error
