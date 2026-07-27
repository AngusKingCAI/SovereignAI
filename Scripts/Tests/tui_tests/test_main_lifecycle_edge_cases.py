"""Tests for main.py lifecycle edge cases using Textual app.run_test()."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.tui.main import LifecycleState, SovereignTUI


class TestMainLifecycleEdgeCases:
    """Test main.py lifecycle edge cases using Textual testing approach."""

    @pytest.mark.asyncio
    async def test_lifecycle_handles_503_service_draining(self):
        """Test lifecycle handles 503 service_draining error code."""
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

    @pytest.mark.asyncio
    async def test_lifecycle_handles_502_bad_gateway(self):
        """Test lifecycle handles 502 bad gateway."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 502
        mock_response.json.return_value = {"error": "bad gateway"}

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        tui = SovereignTUI()
        tui._client = mock_client
        tui._lifecycle_state = LifecycleState.LIFECYCLE_READY
        tui._lifecycle_baseline_pid = 12345
        tui._lifecycle_baseline_uuid = "test-uuid"

        # Should handle 502 gracefully
        await tui._check_lifecycle_status()
        assert tui._lifecycle_state == LifecycleState.LIFECYCLE_SHUTDOWN_DETECTED

    @pytest.mark.asyncio
    async def test_lifecycle_handles_504_gateway_timeout(self):
        """Test lifecycle handles 504 gateway timeout."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 504
        mock_response.json.return_value = {"error": "gateway timeout"}

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        tui = SovereignTUI()
        tui._client = mock_client
        tui._lifecycle_state = LifecycleState.LIFECYCLE_READY
        tui._lifecycle_baseline_pid = 12345
        tui._lifecycle_baseline_uuid = "test-uuid"

        # Should handle 504 gracefully
        await tui._check_lifecycle_status()
        assert tui._lifecycle_state == LifecycleState.LIFECYCLE_SHUTDOWN_DETECTED

    @pytest.mark.asyncio
    async def test_lifecycle_handles_408_request_timeout(self):
        """Test lifecycle handles 408 request timeout."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 408
        mock_response.json.return_value = {"error": "request timeout"}

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        tui = SovereignTUI()
        tui._client = mock_client
        tui._lifecycle_state = LifecycleState.LIFECYCLE_READY
        tui._lifecycle_baseline_pid = 12345
        tui._lifecycle_baseline_uuid = "test-uuid"

        # Should handle 408 gracefully
        await tui._check_lifecycle_status()
        assert tui._lifecycle_state == LifecycleState.LIFECYCLE_SHUTDOWN_DETECTED

    @pytest.mark.asyncio
    async def test_lifecycle_handles_500_internal_server_error(self):
        """Test lifecycle handles 500 internal server error."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"error": "internal server error"}

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        tui = SovereignTUI()
        tui._client = mock_client
        tui._lifecycle_state = LifecycleState.LIFECYCLE_READY
        tui._lifecycle_baseline_pid = 12345
        tui._lifecycle_baseline_uuid = "test-uuid"

        # Should handle 500 gracefully
        await tui._check_lifecycle_status()
        assert tui._lifecycle_state == LifecycleState.LIFECYCLE_SHUTDOWN_DETECTED

    @pytest.mark.asyncio
    async def test_lifecycle_handles_missing_uuid_field(self):
        """Test lifecycle handles missing instance_uuid field."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "ready": True,
            "pid": 12345
            # Missing instance_uuid
        }

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        tui = SovereignTUI()
        tui._client = mock_client
        tui._lifecycle_state = LifecycleState.LIFECYCLE_INIT

        # Should handle missing field gracefully (transitions to READY with None baseline)
        await tui._check_lifecycle_status()
        assert tui._lifecycle_state == LifecycleState.LIFECYCLE_READY
        assert tui._lifecycle_baseline_uuid is None

    @pytest.mark.asyncio
    async def test_lifecycle_handles_missing_pid_field(self):
        """Test lifecycle handles missing pid field."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "ready": True,
            "instance_uuid": "test-uuid"
            # Missing pid
        }

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        tui = SovereignTUI()
        tui._client = mock_client
        tui._lifecycle_state = LifecycleState.LIFECYCLE_INIT

        # Should handle missing field gracefully (transitions to READY with None baseline)
        await tui._check_lifecycle_status()
        assert tui._lifecycle_state == LifecycleState.LIFECYCLE_READY
        assert tui._lifecycle_baseline_pid is None

    @pytest.mark.asyncio
    async def test_lifecycle_handles_null_ready_field(self):
        """Test lifecycle handles null ready field."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "ready": None,
            "pid": 12345,
            "instance_uuid": "test-uuid"
        }

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        tui = SovereignTUI()
        tui._client = mock_client
        tui._lifecycle_state = LifecycleState.LIFECYCLE_INIT

        # Should handle null ready gracefully
        await tui._check_lifecycle_status()
        assert tui._lifecycle_state == LifecycleState.LIFECYCLE_INIT

    @pytest.mark.asyncio
    async def test_lifecycle_handles_malformed_json_response(self):
        """Test lifecycle handles malformed JSON response."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        tui = SovereignTUI()
        tui._client = mock_client
        tui._lifecycle_state = LifecycleState.LIFECYCLE_READY
        tui._lifecycle_baseline_pid = 12345
        tui._lifecycle_baseline_uuid = "test-uuid"

        # Should handle JSON error gracefully
        await tui._check_lifecycle_status()
        assert tui._lifecycle_state == LifecycleState.LIFECYCLE_SHUTDOWN_DETECTED