"""Final tests to reach 90% coverage target."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.tui.panels.adapters import AdaptersPanel
from app.tui.panels.audit import AuditPanel
from app.tui.panels.hardware import HardwarePanel
from app.tui.panels.logs import LogsPanel
from app.tui.panels.memory import MemoryPanel
from app.tui.panels.models import ModelsPanel
from app.tui.panels.options import OptionsPanel
from app.tui.main import LifecycleState, SovereignTUI


class TestFinalCoverageTo90Percent:
    """Final tests to reach 90% coverage target."""

    @pytest.mark.asyncio
    async def test_adapters_panel_http_403_handling(self):
        """Test adapters panel handles 403 forbidden."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.json.return_value = {"error": "forbidden"}

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = AdaptersPanel(client=mock_client)
        await panel._load_data()
        # Should handle 403 gracefully
        assert panel._health_data.get("subsystems", []) == []

    @pytest.mark.asyncio
    async def test_audit_panel_http_401_handling(self):
        """Test audit panel handles 401 unauthorized."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": "unauthorized"}

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = AuditPanel(client=mock_client)
        await panel._load_data()
        # Should handle 401 gracefully
        assert panel._audit_data.get("items", []) == []

    @pytest.mark.asyncio
    async def test_hardware_panel_http_503_handling(self):
        """Test hardware panel handles 503 service unavailable."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 503
        mock_response.json.return_value = {"error": "service unavailable"}

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = HardwarePanel(client=mock_client)
        await panel._load_data()
        # Should handle 503 gracefully
        assert panel._health_data.get("subsystems", []) == []

    @pytest.mark.asyncio
    async def test_logs_panel_http_500_handling(self):
        """Test logs panel handles 500 internal server error."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"error": "internal server error"}

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = LogsPanel(client=mock_client)
        await panel._load_data()
        # Should handle 500 gracefully
        assert panel._logs_data == []

    @pytest.mark.asyncio
    async def test_memory_panel_http_503_memory_not_ready(self):
        """Test memory panel handles 503 with memory_not_ready."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 503
        mock_response.json.return_value = {
            "error_code": "memory_not_ready",
            "message": "Memory not ready"
        }

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = MemoryPanel(client=mock_client)
        await panel._load_data()
        # Should handle 503 gracefully (may show loading or pending state)
        assert panel._memory_status in ["Loading…", "LOADING", "PENDING", "Error", "ERROR"]

    @pytest.mark.asyncio
    async def test_models_panel_http_503_handling(self):
        """Test models panel handles 503 service unavailable."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 503
        mock_response.json.return_value = {"error": "service unavailable"}

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = ModelsPanel(client=mock_client)
        await panel._load_data()
        # Should handle 503 gracefully
        if isinstance(panel._models_data, dict):
            assert panel._models_data.get("models", []) == []
        else:
            assert panel._models_data == []

    @pytest.mark.asyncio
    async def test_options_panel_http_403_handling(self):
        """Test options panel handles 403 forbidden."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.json.return_value = {"error": "forbidden"}

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = OptionsPanel(client=mock_client)
        await panel._load_data()
        # Should handle 403 gracefully
        assert panel._options_data == {}

    @pytest.mark.asyncio
    async def test_main_lifecycle_http_429_rate_limit(self):
        """Test main lifecycle handles 429 rate limiting."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.json.return_value = {"error": "rate limited", "retry_after": 60}

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        tui = SovereignTUI()
        tui._client = mock_client
        tui._lifecycle_state = LifecycleState.LIFECYCLE_READY
        tui._lifecycle_baseline_pid = 12345
        tui._lifecycle_baseline_uuid = "test-uuid"

        # Should handle 429 gracefully
        await tui._check_lifecycle_status()
        assert tui._lifecycle_state == LifecycleState.LIFECYCLE_SHUTDOWN_DETECTED

    @pytest.mark.asyncio
    async def test_main_lifecycle_http_401_unauthorized(self):
        """Test main lifecycle handles 401 unauthorized."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": "unauthorized"}

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        tui = SovereignTUI()
        tui._client = mock_client
        tui._lifecycle_state = LifecycleState.LIFECYCLE_READY
        tui._lifecycle_baseline_pid = 12345
        tui._lifecycle_baseline_uuid = "test-uuid"

        # Should handle 401 gracefully
        await tui._check_lifecycle_status()
        assert tui._lifecycle_state == LifecycleState.LIFECYCLE_SHUTDOWN_DETECTED

    @pytest.mark.asyncio
    async def test_main_lifecycle_http_403_forbidden(self):
        """Test main lifecycle handles 403 forbidden."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.json.return_value = {"error": "forbidden"}

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        tui = SovereignTUI()
        tui._client = mock_client
        tui._lifecycle_state = LifecycleState.LIFECYCLE_READY
        tui._lifecycle_baseline_pid = 12345
        tui._lifecycle_baseline_uuid = "test-uuid"

        # Should handle 403 gracefully
        await tui._check_lifecycle_status()
        assert tui._lifecycle_state == LifecycleState.LIFECYCLE_SHUTDOWN_DETECTED