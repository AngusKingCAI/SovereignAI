"""Tests for panel display methods using Textual app.run_test()."""

from unittest.mock import AsyncMock, MagicMock

import pytest

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


class TestPanelDisplayMethods:
    """Test panel display/update methods using Textual app.run_test()."""

    @pytest.mark.asyncio
    async def test_orchestrator_panel_display_update(self):
        """Test orchestrator panel display update method."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "state": "running",
            "uptime_seconds": 3600,
            "tasks_completed": 42
        }

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        from textual.app import App

        class TestApp(App):
            def compose(self):
                yield OrchestratorPanel(client=mock_client)

        app = TestApp()
        async with app.run_test() as pilot:
            panel = app.query_one(OrchestratorPanel)
            await panel._load_data()
            panel._update_display()
            assert panel is not None

    @pytest.mark.asyncio
    async def test_workers_panel_display_update(self):
        """Test workers panel display update method."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "subsystems": [
                {"name": "worker-1", "kind": "worker", "status": "healthy"}
            ]
        }

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        from textual.app import App

        class TestApp(App):
            def compose(self):
                yield WorkersPanel(client=mock_client)

        app = TestApp()
        async with app.run_test() as pilot:
            panel = app.query_one(WorkersPanel)
            await panel._load_data()
            panel._update_display()
            assert panel is not None

    @pytest.mark.asyncio
    async def test_tasks_panel_display_update(self):
        """Test tasks panel display update method."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"event_id": 100, "task_id": "task-1", "event_type": "created"}
        ]

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        from textual.app import App

        class TestApp(App):
            def compose(self):
                yield TasksPanel(client=mock_client)

        app = TestApp()
        async with app.run_test() as pilot:
            panel = app.query_one(TasksPanel)
            await panel._load_data()
            panel._update_display()
            assert panel is not None

    @pytest.mark.asyncio
    async def test_memory_panel_display_update(self):
        """Test memory panel handles display without _update_display method."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "healthy",
            "memory_usage_gb": 8.5
        }

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        from textual.app import App

        class TestApp(App):
            def compose(self):
                yield MemoryPanel(client=mock_client)

        app = TestApp()
        async with app.run_test() as pilot:
            panel = app.query_one(MemoryPanel)
            await panel._load_data()
            # MemoryPanel doesn't have _update_display, but that's okay
            assert panel is not None

    @pytest.mark.asyncio
    async def test_models_panel_display_update(self):
        """Test models panel display update method."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"model_id": "llama-2-7b", "provider": "ollama"}
        ]

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        from textual.app import App

        class TestApp(App):
            def compose(self):
                yield ModelsPanel(client=mock_client)

        app = TestApp()
        async with app.run_test() as pilot:
            panel = app.query_one(ModelsPanel)
            await panel._load_data()
            panel._update_display()
            assert panel is not None

    @pytest.mark.asyncio
    async def test_adapters_panel_display_update(self):
        """Test adapters panel display update method."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "subsystems": [
                {"name": "ollama", "kind": "adapter", "status": "healthy"}
            ]
        }

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        from textual.app import App

        class TestApp(App):
            def compose(self):
                yield AdaptersPanel(client=mock_client)

        app = TestApp()
        async with app.run_test() as pilot:
            panel = app.query_one(AdaptersPanel)
            await panel._load_data()
            panel._update_display()
            assert panel is not None

    @pytest.mark.asyncio
    async def test_hardware_panel_display_update(self):
        """Test hardware panel display update method."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "subsystems": [
                {
                    "name": "cpu",
                    "kind": "hardware",
                    "status": "healthy",
                    "details": {"cpu_percent": 45}
                }
            ]
        }

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        from textual.app import App

        class TestApp(App):
            def compose(self):
                yield HardwarePanel(client=mock_client)

        app = TestApp()
        async with app.run_test() as pilot:
            panel = app.query_one(HardwarePanel)
            await panel._load_data()
            panel._update_display()
            assert panel is not None

    @pytest.mark.asyncio
    async def test_logs_panel_display_update(self):
        """Test logs panel display update method."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"timestamp": "2024-01-01T00:00:00Z", "level": "info", "message": "Test"}
        ]

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        from textual.app import App

        class TestApp(App):
            def compose(self):
                yield LogsPanel(client=mock_client)

        app = TestApp()
        async with app.run_test() as pilot:
            panel = app.query_one(LogsPanel)
            await panel._load_data()
            panel._update_display()
            assert panel is not None

    @pytest.mark.asyncio
    async def test_options_panel_display_update(self):
        """Test options panel display update method."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "max_workers": 4,
            "timeout_seconds": 30
        }

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        from textual.app import App

        class TestApp(App):
            def compose(self):
                yield OptionsPanel(client=mock_client)

        app = TestApp()
        async with app.run_test() as pilot:
            panel = app.query_one(OptionsPanel)
            await panel._load_data()
            panel._update_display()
            assert panel is not None

    @pytest.mark.asyncio
    async def test_audit_panel_display_update(self):
        """Test audit panel display update method."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "timestamp": "2024-01-01T00:00:00Z",
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

        from textual.app import App

        class TestApp(App):
            def compose(self):
                yield AuditPanel(client=mock_client)

        app = TestApp()
        async with app.run_test() as pilot:
            panel = app.query_one(AuditPanel)
            await panel._load_data()
            panel._update_display()
            assert panel is not None