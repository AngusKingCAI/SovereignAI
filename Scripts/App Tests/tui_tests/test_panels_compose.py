"""Tests for panel compose() methods using Textual app.run_test()."""

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


class TestPanelComposeMethods:
    """Test panel compose() methods using Textual app.run_test()."""

    @pytest.mark.asyncio
    async def test_orchestrator_panel_compose(self):
        """Test orchestrator panel compose() method."""
        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        from textual.app import App

        class TestApp(App):
            def compose(self):
                yield OrchestratorPanel(client=mock_client)

        app = TestApp()
        async with app.run_test() as pilot:
            # Should compose without errors
            panel = app.query_one(OrchestratorPanel)
            assert panel is not None

    @pytest.mark.asyncio
    async def test_workers_panel_compose(self):
        """Test workers panel compose() method."""
        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        from textual.app import App

        class TestApp(App):
            def compose(self):
                yield WorkersPanel(client=mock_client)

        app = TestApp()
        async with app.run_test() as pilot:
            panel = app.query_one(WorkersPanel)
            assert panel is not None

    @pytest.mark.asyncio
    async def test_tasks_panel_compose(self):
        """Test tasks panel compose() method."""
        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        from textual.app import App

        class TestApp(App):
            def compose(self):
                yield TasksPanel(client=mock_client)

        app = TestApp()
        async with app.run_test() as pilot:
            panel = app.query_one(TasksPanel)
            assert panel is not None

    @pytest.mark.asyncio
    async def test_memory_panel_compose(self):
        """Test memory panel compose() method."""
        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        from textual.app import App

        class TestApp(App):
            def compose(self):
                yield MemoryPanel(client=mock_client)

        app = TestApp()
        async with app.run_test() as pilot:
            panel = app.query_one(MemoryPanel)
            assert panel is not None

    @pytest.mark.asyncio
    async def test_models_panel_compose(self):
        """Test models panel compose() method."""
        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        from textual.app import App

        class TestApp(App):
            def compose(self):
                yield ModelsPanel(client=mock_client)

        app = TestApp()
        async with app.run_test() as pilot:
            panel = app.query_one(ModelsPanel)
            assert panel is not None

    @pytest.mark.asyncio
    async def test_adapters_panel_compose(self):
        """Test adapters panel compose() method."""
        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        from textual.app import App

        class TestApp(App):
            def compose(self):
                yield AdaptersPanel(client=mock_client)

        app = TestApp()
        async with app.run_test() as pilot:
            panel = app.query_one(AdaptersPanel)
            assert panel is not None

    @pytest.mark.asyncio
    async def test_hardware_panel_compose(self):
        """Test hardware panel compose() method."""
        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        from textual.app import App

        class TestApp(App):
            def compose(self):
                yield HardwarePanel(client=mock_client)

        app = TestApp()
        async with app.run_test() as pilot:
            panel = app.query_one(HardwarePanel)
            assert panel is not None

    @pytest.mark.asyncio
    async def test_logs_panel_compose(self):
        """Test logs panel compose() method."""
        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        from textual.app import App

        class TestApp(App):
            def compose(self):
                yield LogsPanel(client=mock_client)

        app = TestApp()
        async with app.run_test() as pilot:
            panel = app.query_one(LogsPanel)
            assert panel is not None

    @pytest.mark.asyncio
    async def test_options_panel_compose(self):
        """Test options panel compose() method."""
        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        from textual.app import App

        class TestApp(App):
            def compose(self):
                yield OptionsPanel(client=mock_client)

        app = TestApp()
        async with app.run_test() as pilot:
            panel = app.query_one(OptionsPanel)
            assert panel is not None

    @pytest.mark.asyncio
    async def test_audit_panel_compose(self):
        """Test audit panel compose() method."""
        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        from textual.app import App

        class TestApp(App):
            def compose(self):
                yield AuditPanel(client=mock_client)

        app = TestApp()
        async with app.run_test() as pilot:
            panel = app.query_one(AuditPanel)
            assert panel is not None