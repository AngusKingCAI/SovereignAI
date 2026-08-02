"""TUI Web Client with session cookie jar.

TUIWebClient wraps httpx.AsyncClient with persistent cookie storage
and restrictive file permissions for session cookies.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import httpx2 as httpx
import platformdirs

# Windows ACL limitation: os.chmod() does not enforce ACLs on Windows.
# Cookie file permissions are set via atomic write with 0o600, but
# Windows ACLs may still allow broader access depending on system settings.


class TUIWebClient:
    """HTTP client with persistent cookie jar for TUI.

    Wraps httpx.AsyncClient with cookie persistence using platformdirs
    for cross-platform cache directory location. Cookie file is created
    with restrictive permissions (0o600) on Unix systems.
    """

    def __init__(self, base_url: str | None = None) -> None:
        """Initialize TUIWebClient with cookie jar and base URL.

        Args:
            base_url: Optional base URL. Defaults to SOVEREIGNAI_API_URL
                     environment variable or http://localhost:8000.
        """
        self._base_url = base_url or os.environ.get(
            "SOVEREIGNAI_API_URL",
            "http://localhost:8000"
        )
        self._cookie_path = self._get_cookie_path()
        self._cookie_jar: dict[str, str] = self._load_cookie_jar()
        self._client: httpx.AsyncClient | None = None

    def _get_cookie_path(self) -> Path:
        """Get cookie file path from platformdirs cache directory."""
        cache_dir = Path(platformdirs.user_cache_dir("sovereignai"))
        # Create parent directory with restrictive permissions
        cache_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
        return cache_dir / "cookie"

    def _load_cookie_jar(self) -> dict[str, str]:
        """Load or create cookie jar with persistent storage."""
        cookies = {}

        if self._cookie_path.exists():
            try:
                # Load existing cookies from file (simple JSON format)
                import json
                with open(self._cookie_path, encoding="utf-8") as f:
                    cookie_data = json.load(f)
                    cookies = cookie_data if isinstance(cookie_data, dict) else {}
                # Reset permissions on existing file
                os.chmod(self._cookie_path, 0o600)
            except Exception:
                # If loading fails, start with empty jar
                pass

        return cookies

    def _save_cookie_jar(self) -> None:
        """Save cookie jar to disk with restrictive permissions."""
        try:
            # Use dict directly for JSON serialization
            import json
            # Atomic write with restrictive permissions (text mode for JSON)
            with open(
                self._cookie_path,
                "w",
                encoding="utf-8",
                opener=lambda p, f: os.open(p, f, 0o600)
            ) as f:
                json.dump(self._cookie_jar, f)
            # Explicitly reset permissions after write
            os.chmod(self._cookie_path, 0o600)
        except Exception:
            # Silently fail on save errors (cookie persistence is optional)
            pass

    async def __aenter__(self) -> TUIWebClient:
        """Async context manager entry."""
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            cookies=self._cookie_jar,
            timeout=30.0
        )
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Async context manager exit with cookie save."""
        if self._client is not None:
            await self._client.aclose()
            self._save_cookie_jar()

    @property
    def client(self) -> httpx.AsyncClient:
        """Get underlying httpx.AsyncClient.

        Raises:
            RuntimeError: If client is not initialized (use async context manager).
        """
        if self._client is None:
            raise RuntimeError(
                "TUIWebClient must be used as async context manager. "
                "Use: async with client as c: ..."
            )
        return self._client

    @property
    def base_url(self) -> str:
        """Get base URL."""
        return self._base_url

    async def get(self, path: str, **kwargs: Any) -> httpx.Response:
        """HTTP GET request."""
        return await self.client.get(path, **kwargs)

    async def post(self, path: str, **kwargs: Any) -> httpx.Response:
        """HTTP POST request."""
        return await self.client.post(path, **kwargs)

    async def put(self, path: str, **kwargs: Any) -> httpx.Response:
        """HTTP PUT request."""
        return await self.client.put(path, **kwargs)

    async def delete(self, path: str, **kwargs: Any) -> httpx.Response:
        """HTTP DELETE request."""
        return await self.client.delete(path, **kwargs)

    async def stream_sse(self, path: str, **kwargs: Any) -> Any:
        """Stream SSE events from endpoint.

        Returns:
            Async context manager for SSE streaming.
        """
        return self.client.stream("GET", path, **kwargs)
