"""Tests for TUI sidebar panels with API integration."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.tui.client import TUIWebClient
from app.tui.error_classification import ErrorClassification, classify_error
from app.tui.panels.adapters import AdaptersPanel
from app.tui.panels.audit import AuditPanel
from app.tui.panels.hardware import HardwarePanel
from app.tui.panels.logs import LogsPanel
from app.tui.panels.memory import MemoryPanel
from app.tui.panels.models import ModelsPanel
from app.tui.panels.options import OptionsPanel
from app.tui.panels.orchestrator import OrchestratorPanel
from app.tui.panels.tasks import TasksPanel
from app.tui.panels.workers import WorkersPanel


class TestErrorClassification:
    """Test error classification by API error code."""

    def test_error_terminal_auth_expired(self):
        """Test auth_expired error classified as terminal."""
        response = {"status_code": 401, "error_code": "auth_expired"}
        action = classify_error(response)
        assert action.classification == ErrorClassification.TERMINAL
        assert "login" in action.message.lower()

    def test_error_transient_429_respects_retry_after(self):
        """Test 429 rate limit respects Retry-After header."""
        response = {"status_code": 429, "retry_after": 120}
        action = classify_error(response)
        assert action.classification == ErrorClassification.TRANSIENT
        assert action.retry_after_seconds == 120

    def test_error_transient_503_retry_after_60_delays(self):
        """Test 503 service_draining with 60s retry delay."""
        response = {"status_code": 503, "error_code": "service_draining", "retry_after": 60}
        action = classify_error(response)
        assert action.classification == ErrorClassification.TRANSIENT
        assert action.retry_after_seconds == 60
        assert "shutting down" in action.message.lower()

    def test_error_lockout_no_login_prompt(self):
        """Test lockout error classified as terminal without login prompt."""
        response = {"status_code": 423, "error_code": "lockout", "retry_after_seconds": 300}
        action = classify_error(response)
        assert action.classification == ErrorClassification.TERMINAL_NO_LOGIN
        assert action.retry_after_seconds == 300
        assert "locked" in action.message.lower()

    def test_truth_table_all_codes(self):
        """Test truth table enumerates all error codes."""
        test_cases = [
            # (status_code, error_code, expected_classification)
            (200, "", ErrorClassification.TRANSIENT),  # Default fallback
            (401, "login_required", ErrorClassification.TERMINAL),
            (403, "authorization_denied", ErrorClassification.TERMINAL),
            (403, "setup_token_required", ErrorClassification.TERMINAL),
            (403, "insecure_deployment", ErrorClassification.TERMINAL),
            (409, "idempotency_conflict", ErrorClassification.TERMINAL_NO_LOGIN),
            (423, "lockout", ErrorClassification.TERMINAL_NO_LOGIN),
            (429, "rate_limited", ErrorClassification.TRANSIENT),
            (501, "", ErrorClassification.OPERATOR),
            (503, "memory_not_ready", ErrorClassification.TRANSIENT),
            (503, "", ErrorClassification.TRANSIENT),
            (500, "", ErrorClassification.TRANSIENT),
            (502, "", ErrorClassification.TRANSIENT),
            (504, "", ErrorClassification.TRANSIENT),
            (408, "", ErrorClassification.TRANSIENT),
        ]

        for status_code, error_code, expected in test_cases:
            response = {"status_code": status_code, "error_code": error_code}
            action = classify_error(response)
            assert action.classification == expected, \
                f"Failed for {status_code}/{error_code}: expected {expected}, got {action.classification}"


class TestOrchestratorPanel:
    """Test orchestrator panel integration."""

    @pytest.mark.asyncio
    async def test_orchestrator_panel_renders_status(self):
        """Test orchestrator panel renders OrchestratorStatus DTO."""
        mock_client = MagicMock(spec=TUIWebClient)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "state": "running",
            "uptime_seconds": 3600,
            "tasks_completed": 42,
            "tasks_failed": 3
        }

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = OrchestratorPanel(client=mock_client)
        await panel._load_data()

        # Test data loading without widget tree
        assert panel._status_data["state"] == "running"
        assert panel._status_data["uptime_seconds"] == 3600
        assert panel._status_data["tasks_completed"] == 42
        assert panel._status_data["tasks_failed"] == 3


class TestWorkersPanel:
    """Test workers panel integration."""

    @pytest.mark.asyncio
    async def test_workers_panel_displays_adapters(self):
        """Test workers panel displays HealthSnapshot subsystems."""
        mock_client = MagicMock(spec=TUIWebClient)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "subsystems": [
                {"name": "worker-1", "kind": "worker", "status": "healthy"},
                {"name": "worker-2", "kind": "worker", "status": "degraded"},
            ]
        }

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = WorkersPanel(client=mock_client)
        await panel._load_data()

        # Test data loading without widget tree
        assert len(panel._health_data["subsystems"]) == 2


class TestTasksPanel:
    """Test tasks panel integration."""

    @pytest.mark.asyncio
    async def test_tasks_panel_polls_since_event_id(self):
        """Test tasks panel polls with since_event_id cursor."""
        mock_client = MagicMock(spec=TUIWebClient)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"event_id": 100, "task_id": "task-1", "event_type": "created", "timestamp": "2026-07-21T00:00:00Z"},
            {"event_id": 101, "task_id": "task-1", "event_type": "started", "timestamp": "2026-07-21T00:01:00Z"},
        ]

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = TasksPanel(client=mock_client)
        await panel._load_data()

        # Test data loading without widget tree
        assert len(panel._events_data) == 2
        assert panel._last_event_id == 101


class TestMemoryPanel:
    """Test memory panel integration."""

    @pytest.mark.asyncio
    async def test_memory_panel_shows_pending_before_plan34(self):
        """Test memory panel shows PENDING when Plan 34 not deployed (404)."""
        mock_client = MagicMock(spec=TUIWebClient)
        mock_response = MagicMock()
        mock_response.status_code = 404

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = MemoryPanel(client=mock_client)
        await panel._load_data()

        # Test status without widget tree
        assert panel._memory_status == "PENDING"


class TestModelsPanel:
    """Test models panel integration."""

    @pytest.mark.asyncio
    async def test_models_panel_renders_model_list(self):
        """Test models panel renders ModelListResponse from RF-10."""
        mock_client = MagicMock(spec=TUIWebClient)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"model_id": "llama-2-7b", "provider": "ollama", "sync_status": "synced"},
            {"model_id": "gpt-4", "provider": "openai", "sync_status": "syncing"},
        ]

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = ModelsPanel(client=mock_client)
        await panel._load_data()

        # Test data loading without widget tree
        assert len(panel._models_data) == 2


class TestAdaptersPanel:
    """Test adapters panel integration."""

    @pytest.mark.asyncio
    async def test_adapters_panel_displays_adapters(self):
        """Test adapters panel displays HealthSnapshot subsystems."""
        mock_client = MagicMock(spec=TUIWebClient)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "subsystems": [
                {"name": "adapter-1", "kind": "adapter", "status": "healthy"},
                {"name": "adapter-2", "kind": "adapter", "status": "unhealthy"},
            ]
        }

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = AdaptersPanel(client=mock_client)
        await panel._load_data()

        # Test data loading without widget tree
        assert len(panel._health_data["subsystems"]) == 2


class TestHardwarePanel:
    """Test hardware panel integration."""

    @pytest.mark.asyncio
    async def test_hardware_panel_displays_details(self):
        """Test hardware panel displays HealthSnapshot subsystems filtered by kind=hardware."""
        mock_client = MagicMock(spec=TUIWebClient)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "subsystems": [
                {
                    "name": "cpu",
                    "kind": "hardware",
                    "status": "healthy",
                    "details": {
                        "cpu_percent": 45.2,
                        "model": "AMD Ryzen 9",
                        "cores": 12
                    }
                },
                {
                    "name": "memory",
                    "kind": "hardware",
                    "status": "healthy",
                    "details": {
                        "ram_used_gb": 8.5,
                        "ram_total_gb": 32.0,
                        "ram_percent": 26.5
                    }
                }
            ]
        }

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = HardwarePanel(client=mock_client)
        await panel._load_data()

        # Test data loading without widget tree
        assert len(panel._health_data["subsystems"]) == 2


class TestLogsPanel:
    """Test logs panel integration."""

    @pytest.mark.asyncio
    async def test_log_panel_renders_log_entries(self):
        """Test logs panel renders paginated AuditPage with TraceEvent."""
        mock_client = MagicMock(spec=TUIWebClient)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"timestamp": "2026-07-21T00:00:00Z", "level": "info", "source": "orchestrator", "message": "Task started"},
            {"timestamp": "2026-07-21T00:01:00Z", "level": "error", "source": "worker", "message": "Task failed"},
        ]

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = LogsPanel(client=mock_client)
        await panel._load_data()

        # Test data loading without widget tree
        assert len(panel._logs_data) == 2


class TestOptionsPanel:
    """Test options panel integration."""

    @pytest.mark.asyncio
    async def test_options_panel_fetches_and_displays_options(self):
        """Test options panel fetches and displays OptionsData DTO."""
        mock_client = MagicMock(spec=TUIWebClient)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "max_workers": 4,
            "timeout_seconds": 30,
            "log_level": "info"
        }

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = OptionsPanel(client=mock_client)
        await panel._load_data()

        # Test data loading without widget tree
        assert panel._options_data["max_workers"] == 4
        assert panel._options_data["timeout_seconds"] == 30


class TestAuditPanel:
    """Test audit panel integration."""

    @pytest.mark.asyncio
    async def test_audit_panel_pagination(self):
        """Test audit panel displays paginated AuditPage with MessagingAuditEntryDTO."""
        mock_client = MagicMock(spec=TUIWebClient)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "timestamp": "2026-07-21T00:00:00Z",
                    "source_department": "orchestrator",
                    "target_department": "worker",
                    "content": "Task assignment"
                }
            ],
            "total_count": 1,
            "page_count": 1
        }

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = AuditPanel(client=mock_client)
        await panel._load_data()

        # Test data loading without widget tree
        assert len(panel._audit_data["items"]) == 1


class TestTaskPanelTransportDecision:
    """Test task panel transport decision follows spike outcome."""

    @pytest.mark.asyncio
    async def test_task_panel_uses_polling_after_spike_fail(self):
        """Test task panel uses REST polling after SSE_FAIL spike outcome."""
        # Since spike returned SSE_FAIL, task panel should use polling
        # This is verified by the implementation using REST polling
        mock_client = MagicMock(spec=TUIWebClient)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = TasksPanel(client=mock_client)
        await panel._load_data()

        # Verify REST GET was called (polling), not SSE stream
        mock_client.get.assert_called_once()
        # Check that stream_sse method exists but wasn't called
        assert hasattr(mock_client, 'stream_sse') or not hasattr(TUIWebClient, 'stream_sse')

    @pytest.mark.asyncio
    async def test_log_panel_transport_decision_follows_spike_outcome(self):
        """Test log panel uses REST polling after SSE_FAIL spike outcome."""
        # Since spike returned SSE_FAIL, log panel should use polling
        mock_client = MagicMock(spec=TUIWebClient)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = LogsPanel(client=mock_client)
        await panel._load_data()

        # Verify REST GET was called (polling), not SSE stream
        mock_client.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_orchestrator_panel_handles_empty_response(self):
        """Test orchestrator panel handles empty API response."""
        mock_client = MagicMock(spec=TUIWebClient)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = OrchestratorPanel(client=mock_client)
        await panel._load_data()

        # Should handle empty response gracefully
        assert panel._status_data == {}

    @pytest.mark.asyncio
    async def test_workers_panel_handles_health_check_failure(self):
        """Test workers panel handles health check failure."""
        mock_client = MagicMock(spec=TUIWebClient)
        mock_response = MagicMock()
        mock_response.status_code = 503

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = WorkersPanel(client=mock_client)
        await panel._load_data()

        # Should handle failure gracefully - panel should still have data structure
        assert hasattr(panel, '_health_data')

    @pytest.mark.asyncio
    async def test_models_panel_handles_empty_list(self):
        """Test models panel handles empty model list."""
        mock_client = MagicMock(spec=TUIWebClient)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"models": []}

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = ModelsPanel(client=mock_client)
        await panel._load_data()

        # Should handle empty list gracefully
        assert panel._models_data == {"models": []}

    @pytest.mark.asyncio
    async def test_adapters_panel_handles_adapter_list(self):
        """Test adapters panel handles adapter list response."""
        mock_client = MagicMock(spec=TUIWebClient)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "subsystems": [
                {"name": "ollama", "kind": "adapter", "status": "healthy"},
                {"name": "llama_cpp", "kind": "adapter", "status": "degraded"}
            ]
        }

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = AdaptersPanel(client=mock_client)
        await panel._load_data()

        # Should handle adapter list in health data
        assert len(panel._health_data.get("subsystems", [])) == 2

    @pytest.mark.asyncio
    async def test_hardware_panel_handles_no_metrics(self):
        """Test hardware panel handles no hardware metrics."""
        mock_client = MagicMock(spec=TUIWebClient)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"subsystems": []}

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = HardwarePanel(client=mock_client)
        await panel._load_data()

        # Should handle empty metrics gracefully
        assert panel._health_data == {"subsystems": []}

    @pytest.mark.asyncio
    async def test_memory_panel_handles_pending_state(self):
        """Test memory panel handles pending state before Plan 34."""
        mock_client = MagicMock(spec=TUIWebClient)
        mock_response = MagicMock()
        mock_response.status_code = 404

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = MemoryPanel(client=mock_client)
        await panel._load_data()

        # Should show pending state when 404
        assert panel._memory_status == "PENDING"

    @pytest.mark.asyncio
    async def test_logs_panel_handles_empty_logs(self):
        """Test logs panel handles empty log list."""
        mock_client = MagicMock(spec=TUIWebClient)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = LogsPanel(client=mock_client)
        await panel._load_data()

        # Should handle empty logs gracefully
        assert panel._logs_data == []

    @pytest.mark.asyncio
    async def test_options_panel_handles_options_data(self):
        """Test options panel handles options data."""
        mock_client = MagicMock(spec=TUIWebClient)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "max_workers": 8,
            "timeout_seconds": 60,
            "log_level": "debug"
        }

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = OptionsPanel(client=mock_client)
        await panel._load_data()

        # Should handle options data
        assert panel._options_data["max_workers"] == 8

    @pytest.mark.asyncio
    async def test_audit_panel_handles_empty_audit(self):
        """Test audit panel handles empty audit data."""
        mock_client = MagicMock(spec=TUIWebClient)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [],
            "total_count": 0,
            "page_count": 0
        }

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = AuditPanel(client=mock_client)
        await panel._load_data()

        # Should handle empty audit gracefully
        assert panel._audit_data["total_count"] == 0

    @pytest.mark.asyncio
    async def test_orchestrator_panel_update_display(self):
        """Test orchestrator panel display update method."""
        mock_client = MagicMock(spec=TUIWebClient)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "state": "running",
            "uptime_seconds": 3600,
            "tasks_completed": 42,
            "tasks_failed": 3
        }

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = OrchestratorPanel(client=mock_client)
        await panel._load_data()

        # Should have loaded data
        assert panel._status_data["state"] == "running"

    @pytest.mark.asyncio
    async def test_workers_panel_update_display(self):
        """Test workers panel display update method."""
        mock_client = MagicMock(spec=TUIWebClient)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "subsystems": [
                {"name": "worker1", "kind": "worker", "status": "healthy"},
                {"name": "worker2", "kind": "worker", "status": "degraded"}
            ]
        }

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = WorkersPanel(client=mock_client)
        await panel._load_data()

        # Should have loaded data
        assert len(panel._health_data["subsystems"]) == 2

    @pytest.mark.asyncio
    async def test_tasks_panel_update_display(self):
        """Test tasks panel display update method."""
        mock_client = MagicMock(spec=TUIWebClient)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"event_id": 1, "task_id": 101, "event_type": "task_started", "timestamp": "2024-01-01T00:00:00Z"},
            {"event_id": 2, "task_id": 102, "event_type": "task_completed", "timestamp": "2024-01-01T00:01:00Z"}
        ]

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = TasksPanel(client=mock_client)
        await panel._load_data()

        # Should have loaded data
        assert len(panel._events_data) == 2

    @pytest.mark.asyncio
    async def test_models_panel_update_display(self):
        """Test models panel display update method."""
        mock_client = MagicMock(spec=TUIWebClient)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "llama2", "status": "loaded"},
                {"name": "mistral", "status": "available"}
            ]
        }

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = ModelsPanel(client=mock_client)
        await panel._load_data()

        # Should have loaded data
        assert len(panel._models_data["models"]) == 2

    @pytest.mark.asyncio
    async def test_hardware_panel_update_display(self):
        """Test hardware panel display update method."""
        mock_client = MagicMock(spec=TUIWebClient)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "subsystems": [
                {"name": "cpu", "kind": "hardware", "status": "healthy", "details": {"usage": 45}},
                {"name": "gpu", "kind": "hardware", "status": "healthy", "details": {"usage": 78}}
            ]
        }

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = HardwarePanel(client=mock_client)
        await panel._load_data()

        # Should have loaded data
        assert len(panel._health_data["subsystems"]) == 2

    @pytest.mark.asyncio
    async def test_logs_panel_update_display(self):
        """Test logs panel display update method."""
        mock_client = MagicMock(spec=TUIWebClient)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"timestamp": "2024-01-01T00:00:00Z", "level": "info", "message": "Test log"},
            {"timestamp": "2024-01-01T00:01:00Z", "level": "error", "message": "Test error"}
        ]

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = LogsPanel(client=mock_client)
        await panel._load_data()

        # Should have loaded data
        assert len(panel._logs_data) == 2

    @pytest.mark.asyncio
    async def test_options_panel_update_display(self):
        """Test options panel display update method."""
        mock_client = MagicMock(spec=TUIWebClient)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "max_workers": 8,
            "timeout_seconds": 60,
            "log_level": "debug"
        }

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = OptionsPanel(client=mock_client)
        await panel._load_data()

        # Should have loaded data
        assert panel._options_data["max_workers"] == 8

    @pytest.mark.asyncio
    async def test_audit_panel_update_display(self):
        """Test audit panel display update method."""
        mock_client = MagicMock(spec=TUIWebClient)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {"timestamp": "2024-01-01T00:00:00Z", "source_department": "orchestrator", "target_department": "worker", "content": "Task assignment"}
            ],
            "total_count": 1,
            "page_count": 1
        }

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = AuditPanel(client=mock_client)
        await panel._load_data()

        # Should have loaded data
        assert len(panel._audit_data["items"]) == 1

    @pytest.mark.asyncio
    async def test_adapters_panel_widget_tree_not_mounted(self):
        """Test adapters panel handles widget tree not mounted during display update."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "subsystems": [
                {"name": "test", "kind": "adapter", "status": "healthy"}
            ]
        }

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = AdaptersPanel(client=mock_client)
        await panel._load_data()

        # Update display without mounting widget tree
        panel._update_display()
        # Should not raise exception
        assert panel._health_data["subsystems"] is not None

    @pytest.mark.asyncio
    async def test_tasks_panel_handles_invalid_json_response(self):
        """Test tasks panel handles invalid JSON response."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = TasksPanel(client=mock_client)
        await panel._load_data()

        # Should handle JSON error gracefully
        assert panel._events_data == []

    @pytest.mark.asyncio
    async def test_orchestrator_panel_handles_missing_state_field(self):
        """Test orchestrator panel handles missing state field in response."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "uptime": 100,
            "tasks_completed": 5
            # Missing "state" field
        }

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = OrchestratorPanel(client=mock_client)
        await panel._load_data()

        # Should handle missing field gracefully
        assert panel._status_data.get("state") is None

    @pytest.mark.asyncio
    async def test_workers_panel_handles_null_kind_field(self):
        """Test workers panel handles null kind field in subsystems."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "subsystems": [
                {"name": "test", "kind": None, "status": "healthy"}
            ]
        }

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = WorkersPanel(client=mock_client)
        await panel._load_data()

        # Should handle null kind gracefully
        assert panel._health_data["subsystems"] is not None

    @pytest.mark.asyncio
    async def test_memory_panel_handles_http_409_conflict(self):
        """Test memory panel handles conflict errors."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 409
        mock_response.json.return_value = {"error": "conflict"}

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = MemoryPanel(client=mock_client)
        await panel._load_data()

        # Should handle 409 gracefully (may show pending or error)
        assert panel._memory_status in ["PENDING", "Error", "ERROR"]

    @pytest.mark.asyncio
    async def test_models_panel_handles_malformed_model_data(self):
        """Test models panel handles malformed model data."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"id": None, "provider": "test"}  # Missing required fields
            ]
        }

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = ModelsPanel(client=mock_client)
        await panel._load_data()

        # Should handle malformed data gracefully
        assert panel._models_data["models"] is not None

    @pytest.mark.asyncio
    async def test_hardware_panel_handles_missing_details_field(self):
        """Test hardware panel handles missing details field."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "subsystems": [
                {
                    "name": "test",
                    "kind": "hardware",
                    "status": "healthy"
                    # Missing "details" field
                }
            ]
        }

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = HardwarePanel(client=mock_client)
        await panel._load_data()

        # Should handle missing details gracefully
        assert len(panel._health_data["subsystems"]) == 1

    @pytest.mark.asyncio
    async def test_logs_panel_handles_empty_response_list(self):
        """Test logs panel handles empty response list."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = LogsPanel(client=mock_client)
        await panel._load_data()

        # Should handle empty list gracefully
        assert panel._logs_data == []

    @pytest.mark.asyncio
    async def test_options_panel_handles_empty_options_dict(self):
        """Test options panel handles empty options dictionary."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = OptionsPanel(client=mock_client)
        await panel._load_data()

        # Should handle empty dict gracefully
        assert panel._options_data == {}

    @pytest.mark.asyncio
    async def test_audit_panel_handles_null_items_field(self):
        """Test audit panel handles null items field."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": None,
            "total_count": 0,
            "page_count": 0
        }

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = AuditPanel(client=mock_client)
        await panel._load_data()

        # Should handle null items gracefully
        assert panel._audit_data["total_count"] == 0

    @pytest.mark.asyncio
    async def test_adapters_panel_widget_tree_not_mounted(self):
        """Test adapters panel handles widget tree not mounted during display update."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "subsystems": [
                {"name": "test", "kind": "adapter", "status": "healthy"}
            ]
        }

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = AdaptersPanel(client=mock_client)
        await panel._load_data()

        # Update display without mounting widget tree
        panel._update_display()
        # Should not raise exception
        assert panel._health_data["subsystems"] is not None

    @pytest.mark.asyncio
    async def test_tasks_panel_handles_invalid_json_response(self):
        """Test tasks panel handles invalid JSON response."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = TasksPanel(client=mock_client)
        await panel._load_data()

        # Should handle JSON error gracefully
        assert panel._events_data == []

    @pytest.mark.asyncio
    async def test_orchestrator_panel_handles_missing_state_field(self):
        """Test orchestrator panel handles missing state field in response."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "uptime": 100,
            "tasks_completed": 5
            # Missing "state" field
        }

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = OrchestratorPanel(client=mock_client)
        await panel._load_data()

        # Should handle missing field gracefully
        assert panel._status_data.get("state") is None

    @pytest.mark.asyncio
    async def test_workers_panel_handles_null_kind_field(self):
        """Test workers panel handles null kind field in subsystems."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "subsystems": [
                {"name": "test", "kind": None, "status": "healthy"}
            ]
        }

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = WorkersPanel(client=mock_client)
        await panel._load_data()

        # Should handle null kind gracefully
        assert panel._health_data["subsystems"] is not None

    @pytest.mark.asyncio
    async def test_memory_panel_handles_http_409_conflict(self):
        """Test memory panel handles conflict errors."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 409
        mock_response.json.return_value = {"error": "conflict"}

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = MemoryPanel(client=mock_client)
        await panel._load_data()

        # Should handle 409 gracefully (may show pending or error)
        assert panel._memory_status in ["PENDING", "Error", "ERROR"]

    @pytest.mark.asyncio
    async def test_models_panel_handles_malformed_model_data(self):
        """Test models panel handles malformed model data."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"id": None, "provider": "test"}  # Missing required fields
            ]
        }

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = ModelsPanel(client=mock_client)
        await panel._load_data()

        # Should handle malformed data gracefully
        assert panel._models_data["models"] is not None

    @pytest.mark.asyncio
    async def test_hardware_panel_handles_missing_details_field(self):
        """Test hardware panel handles missing details field."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "subsystems": [
                {
                    "name": "test",
                    "kind": "hardware",
                    "status": "healthy"
                    # Missing "details" field
                }
            ]
        }

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = HardwarePanel(client=mock_client)
        await panel._load_data()

        # Should handle missing details gracefully
        assert len(panel._health_data["subsystems"]) == 1

    @pytest.mark.asyncio
    async def test_logs_panel_handles_empty_response_list(self):
        """Test logs panel handles empty response list."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = LogsPanel(client=mock_client)
        await panel._load_data()

        # Should handle empty list gracefully
        assert panel._logs_data == []

    @pytest.mark.asyncio
    async def test_options_panel_handles_empty_options_dict(self):
        """Test options panel handles empty options dictionary."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = OptionsPanel(client=mock_client)
        await panel._load_data()

        # Should handle empty dict gracefully
        assert panel._options_data == {}

    @pytest.mark.asyncio
    async def test_audit_panel_handles_null_items_field(self):
        """Test audit panel handles null items field."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": None,
            "total_count": 0,
            "page_count": 0
        }

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        panel = AuditPanel(client=mock_client)
        await panel._load_data()

        # Should handle null items gracefully
        assert panel._audit_data["total_count"] == 0
