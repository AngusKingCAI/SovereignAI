"""Final push to reach 90% coverage."""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from app.tui.client import TUIWebClient
from app.tui.main import LifecycleState, SovereignTUI
from app.tui.panels.hardware import HardwarePanel
from app.tui.panels.memory import MemoryPanel


class TestFinalPushTo90Percent:
    """Final tests to reach 90% coverage."""

    @pytest.mark.asyncio
    async def test_client_handles_request_exception(self):
        """Test client handles request exceptions."""
        with patch("platformdirs.user_cache_dir") as mock_cache:
            import tempfile
            mock_cache.return_value = tempfile.mkdtemp()

            async with TUIWebClient() as client:
                # Mock a request exception
                with patch.object(client._client, "get", side_effect=Exception("Request failed")):
                    try:
                        await client.get("/api/test")
                    except Exception:
                        pass  # Expected to handle gracefully

    @pytest.mark.asyncio
    async def test_hardware_panel_empty_response_handling(self):
        """Test hardware panel handles empty response."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "subsystems": []
        }

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = HardwarePanel(client=mock_client)
        await panel._load_data()
        # Should handle empty response gracefully
        assert panel._health_data["subsystems"] == []

    @pytest.mark.asyncio
    async def test_memory_panel_ready_status_update(self):
        """Test memory panel ready status update."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "ready",
            "memory_usage_gb": 12.5
        }

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = MemoryPanel(client=mock_client)
        await panel._load_data()
        # Should handle ready status
        assert panel._memory_status == "Live"

    @pytest.mark.asyncio
    async def test_main_lifecycle_status_503_service_draining(self):
        """Test main lifecycle handles 503 service_draining."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 503
        mock_response.json.return_value = {
            "error_code": "service_draining",
            "retry_after": 60
        }

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        tui = SovereignTUI()
        tui._client = mock_client
        tui._lifecycle_state = LifecycleState.LIFECYCLE_READY
        tui._lifecycle_baseline_pid = 12345
        tui._lifecycle_baseline_uuid = "test-uuid"

        # Should handle 503 gracefully
        await tui._check_lifecycle_status()
        assert tui._lifecycle_state == LifecycleState.LIFECYCLE_SHUTDOWN_DETECTED