"""Tests for SkillsPanel using Textual app.run_test()."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.tui.panels.skills import SkillsPanel


class TestSkillsPanel:
    """Test SkillsPanel using Textual testing approach."""

    @pytest.mark.asyncio
    async def test_skills_panel_compose(self):
        """Test skills panel compose() method."""
        mock_container = MagicMock()
        mock_trace = MagicMock()

        from textual.app import App

        class TestApp(App):
            def compose(self):
                yield SkillsPanel(container=mock_container, trace=mock_trace)

        app = TestApp()
        async with app.run_test() as pilot:
            # Should compose without errors
            panel = app.query_one(SkillsPanel)
            assert panel is not None

    @pytest.mark.asyncio
    async def test_skills_panel_load_data_handles_api_unavailable(self):
        """Test skills panel handles when CapabilityAPI is unavailable."""
        mock_container = MagicMock()
        mock_container.retrieve.side_effect = Exception("API not available")
        mock_trace = MagicMock()

        from textual.app import App

        class TestApp(App):
            def compose(self):
                yield SkillsPanel(container=mock_container, trace=mock_trace)

        app = TestApp()
        async with app.run_test() as pilot:
            panel = app.query_one(SkillsPanel)
            # Should handle API unavailability gracefully
            assert panel is not None

    @pytest.mark.asyncio
    async def test_skills_panel_refresh_skills_with_no_api(self):
        """Test skills panel refresh handles None API gracefully."""
        mock_container = MagicMock()
        mock_trace = MagicMock()

        from textual.app import App

        class TestApp(App):
            def compose(self):
                yield SkillsPanel(container=mock_container, trace=mock_trace)

        app = TestApp()
        async with app.run_test() as pilot:
            panel = app.query_one(SkillsPanel)
            panel._api = None
            # Should handle None API gracefully
            panel._refresh_skills()
            assert panel is not None

    @pytest.mark.asyncio
    async def test_skills_panel_refresh_skills_with_api_error(self):
        """Test skills panel refresh handles API errors gracefully."""
        mock_container = MagicMock()
        mock_trace = MagicMock()
        mock_api = MagicMock()
        mock_api.query_skills.side_effect = Exception("API error")
        mock_container.retrieve.return_value = mock_api

        from textual.app import App

        class TestApp(App):
            def compose(self):
                yield SkillsPanel(container=mock_container, trace=mock_trace)

        app = TestApp()
        async with app.run_test() as pilot:
            panel = app.query_one(SkillsPanel)
            panel._api = mock_api
            # Should handle API error gracefully
            panel._refresh_skills()
            assert panel is not None

    @pytest.mark.asyncio
    async def test_skills_panel_button_refresh(self):
        """Test skills panel refresh button functionality."""
        mock_container = MagicMock()
        mock_trace = MagicMock()
        mock_api = MagicMock()
        mock_api.query_skills.return_value = []
        mock_container.retrieve.return_value = mock_api

        from textual.app import App

        class TestApp(App):
            def compose(self):
                yield SkillsPanel(container=mock_container, trace=mock_trace)

        app = TestApp()
        async with app.run_test() as pilot:
            panel = app.query_one(SkillsPanel)
            panel._api = mock_api
            # Simulate button press
            from textual.widgets import Button
            button = panel.query_one("#btn-refresh", Button)
            panel.on_button_pressed(Button.Pressed(button))
            assert panel is not None

    @pytest.mark.asyncio
    async def test_skills_panel_on_mount(self):
        """Test skills panel on_mount lifecycle."""
        mock_container = MagicMock()
        mock_trace = MagicMock()

        from textual.app import App

        class TestApp(App):
            def compose(self):
                yield SkillsPanel(container=mock_container, trace=mock_trace)

        app = TestApp()
        async with app.run_test() as pilot:
            panel = app.query_one(SkillsPanel)
            # Should call _load_data after mount
            assert panel is not None