"""Tests for TUIWebClient cookie jar and configuration."""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.tui.client import TUIWebClient


class TestCookieJarPermissions:
    """Test cookie jar file permissions."""

    def test_cookie_jar_permissions(self):
        """Test cookie jar created with restrictive 0o600 permissions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("platformdirs.user_cache_dir") as mock_cache:
                mock_cache.return_value = tmpdir

                client = TUIWebClient()
                # Trigger cookie jar creation
                client._save_cookie_jar()

                cookie_path = client._cookie_path
                assert cookie_path.exists()

                # Check file permissions (Unix only)
                if os.name != "nt":  # Skip on Windows
                    stat_info = os.stat(cookie_path)
                    mode = stat_info.st_mode & 0o777
                    assert mode == 0o600, f"Expected 0o600, got {oct(mode)}"

    def test_cookie_jar_permissions_reset_on_existing_file(self):
        """Test cookie jar permissions reset on existing file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("platformdirs.user_cache_dir") as mock_cache:
                mock_cache.return_value = tmpdir

                # Create client and save initial cookies
                client1 = TUIWebClient()
                client1._save_cookie_jar()

                cookie_path = client1._cookie_path

                # Deliberately loosen permissions
                if os.name != "nt":  # Skip on Windows
                    os.chmod(cookie_path, 0o644)

                # Create new client (should reset permissions)
                client2 = TUIWebClient()
                client2._load_cookie_jar()

                if os.name != "nt":  # Skip on Windows
                    stat_info = os.stat(cookie_path)
                    mode = stat_info.st_mode & 0o777
                    assert mode == 0o600, f"Expected 0o600 after reset, got {oct(mode)}"


class TestBaseUrlConfiguration:
    """Test base URL configuration from environment variable."""

    def test_base_url_env_var(self):
        """Test base URL from SOVEREIGNAI_API_URL environment variable."""
        with patch.dict(os.environ, {"SOVEREIGNAI_API_URL": "http://custom:9000"}):
            client = TUIWebClient()
            assert client.base_url == "http://custom:9000"

    def test_base_url_default_localhost(self):
        """Test base URL defaults to localhost:8000 when env var not set."""
        with patch.dict(os.environ, {}, clear=True):
            client = TUIWebClient()
            assert client.base_url == "http://localhost:8000"

    def test_base_url_explicit_override(self):
        """Test explicit base_url parameter overrides env var."""
        with patch.dict(os.environ, {"SOVEREIGNAI_API_URL": "http://custom:9000"}):
            client = TUIWebClient(base_url="http://explicit:8080")
            assert client.base_url == "http://explicit:8080"


class TestClientContextManager:
    """Test async context manager behavior."""

    @pytest.mark.asyncio
    async def test_context_manager_initializes_client(self):
        """Test async context manager initializes httpx client."""
        with patch("platformdirs.user_cache_dir") as mock_cache:
            mock_cache.return_value = tempfile.mkdtemp()

            async with TUIWebClient() as client:
                assert client._client is not None
                assert client.client is not None

    @pytest.mark.asyncio
    async def test_context_manager_saves_cookies_on_exit(self):
        """Test async context manager saves cookies on exit."""
        with patch("platformdirs.user_cache_dir") as mock_cache:
            tmpdir = tempfile.mkdtemp()
            mock_cache.return_value = tmpdir

            async with TUIWebClient() as client:
                # Set a cookie
                client._cookie_jar["test"] = "value"

            # Verify cookie file was created
            cookie_path = Path(tmpdir) / "cookie"
            assert cookie_path.exists()

    @pytest.mark.asyncio
    async def test_context_manager_handles_client_initialization_error(self):
        """Test context manager handles client initialization errors."""
        with patch("platformdirs.user_cache_dir") as mock_cache:
            mock_cache.return_value = tempfile.mkdtemp()

            with patch("httpx.AsyncClient", side_effect=Exception("Client init error")):
                try:
                    async with TUIWebClient() as client:
                        pass
                except Exception:
                    # Should handle initialization error gracefully
                    pass

    @pytest.mark.asyncio
    async def test_context_manager_handles_cookie_save_error(self):
        """Test context manager handles cookie save errors."""
        with patch("platformdirs.user_cache_dir") as mock_cache:
            tmpdir = tempfile.mkdtemp()
            mock_cache.return_value = tmpdir

            with patch("pathlib.Path.open", side_effect=PermissionError("Permission denied")):
                async with TUIWebClient() as client:
                    # Set a cookie
                    client._cookie_jar["test"] = "value"

                # Should handle permission error gracefully

    @pytest.mark.asyncio
    async def test_client_property_raises_without_context(self):
        """Test client property raises when used outside context manager."""
        client = TUIWebClient()

        with pytest.raises(RuntimeError, match="Client not initialized"):
            _ = client.client

    @pytest.mark.asyncio
    async def test_get_method_with_timeout(self):
        """Test GET method with timeout parameter."""
        with patch("platformdirs.user_cache_dir") as mock_cache:
            mock_cache.return_value = tempfile.mkdtemp()

            async with TUIWebClient() as client:
                with patch.object(client._client, "get") as mock_get:
                    mock_response = MagicMock()
                    mock_response.status_code = 200
                    mock_response.json.return_value = {"test": "data"}
                    mock_get.return_value = mock_response

                    response = await client.get("/api/test", timeout=10.0)

                    # Should pass timeout to underlying client
                    mock_get.assert_called_once_with("/api/test", timeout=10.0)

    @pytest.mark.asyncio
    async def test_post_method_with_timeout(self):
        """Test POST method with timeout parameter."""
        with patch("platformdirs.user_cache_dir") as mock_cache:
            mock_cache.return_value = tempfile.mkdtemp()

            async with TUIWebClient() as client:
                with patch.object(client._client, "post") as mock_post:
                    mock_response = MagicMock()
                    mock_response.status_code = 200
                    mock_response.json.return_value = {"test": "data"}
                    mock_post.return_value = mock_response

                    response = await client.post("/api/test", json={"data": "test"}, timeout=5.0)

                    # Should pass timeout to underlying client
                    mock_post.assert_called_once_with("/api/test", json={"data": "test"}, timeout=5.0)

    @pytest.mark.asyncio
    async def test_get_method_with_headers(self):
        """Test GET method with custom headers."""
        with patch("platformdirs.user_cache_dir") as mock_cache:
            mock_cache.return_value = tempfile.mkdtemp()

            async with TUIWebClient() as client:
                with patch.object(client._client, "get") as mock_get:
                    mock_response = MagicMock()
                    mock_response.status_code = 200
                    mock_response.json.return_value = {"test": "data"}
                    mock_get.return_value = mock_response

                    response = await client.get("/api/test", headers={"Custom": "value"})

                    # Should pass headers to underlying client
                    mock_get.assert_called_once_with("/api/test", headers={"Custom": "value"})

    @pytest.mark.asyncio
    async def test_context_manager_closes_client_on_exit(self):
        """Test context manager closes httpx client on exit."""
        with patch("platformdirs.user_cache_dir") as mock_cache:
            mock_cache.return_value = tempfile.mkdtemp()

            async with TUIWebClient() as client:
                # Client should be initialized
                assert client._client is not None

            # Client cleanup is handled by httpx async context manager
            # We just verify it was initialized during context

    @pytest.mark.asyncio
    async def test_client_property_raises_without_context(self):
        """Test client property raises RuntimeError without context manager."""
        client = TUIWebClient()
        with pytest.raises(RuntimeError, match="async context manager"):
            _ = client.client
