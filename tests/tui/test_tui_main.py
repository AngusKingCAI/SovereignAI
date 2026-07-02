from __future__ import annotations

from textual.app import App
from textual.widgets import Button, ContentSwitcher, Header, Footer, Static

from tui.main import SovereignTUI


def test_tui_app_initialization():
    app = SovereignTUI()
    assert app.title == "SovereignTUI"


def test_tui_compose_structure():
    app = SovereignTUI()
    async def check_compose():
        async with app.run_test() as pilot:
            # Check Header exists
            header = app.query_one(Header)
            assert header is not None

            # Check Footer exists
            footer = app.query_one(Footer)
            assert footer is not None

            # Check sidebar exists
            sidebar = app.query_one("#sidebar")
            assert sidebar is not None

            # Check main-content ContentSwitcher exists
            content_switcher = app.query_one("#main-content", ContentSwitcher)
            assert content_switcher is not None

            # Check location bar exists
            location_bar = app.query_one("#location-bar", Static)
            assert location_bar is not None

            # Check all panel buttons exist
            from tui.panels import PANEL_NAMES
            for panel_name in PANEL_NAMES:
                button = app.query_one(f"#btn-{panel_name}", Button)
                assert button is not None
                assert button.label == panel_name.title()

    import asyncio
    asyncio.run(check_compose())


def test_tui_panel_buttons_exist():
    app = SovereignTUI()
    async def check_buttons():
        async with app.run_test() as pilot:
            from tui.panels import PANEL_NAMES
            for panel_name in PANEL_NAMES:
                button = app.query_one(f"#btn-{panel_name}", Button)
                assert button is not None

    import asyncio
    asyncio.run(check_buttons())


def test_tui_q_key_quits():
    app = SovereignTUI()
    async def check_quit():
        async with app.run_test() as pilot:
            await pilot.press("q")
            assert app.is_running is False

    import asyncio
    asyncio.run(check_quit())


def test_tui_lazy_panel_loading():
    app = SovereignTUI()
    async def check_lazy_loading():
        async with app.run_test() as pilot:
            from tui.panels import PANEL_NAMES

            # Initially, panels should be placeholder Static widgets
            for panel_name in PANEL_NAMES:
                placeholder = app.query_one(f"#placeholder-{panel_name}", Static)
                assert placeholder is not None

            # Click a button to load the actual panel
            first_panel_name = PANEL_NAMES[0]
            button = app.query_one(f"#btn-{first_panel_name}", Button)
            await pilot.click(button)

            # The panel should now be replaced with the actual panel class
            panel = app.query_one(f"#panel-{first_panel_name}")
            assert panel is not None
            # It should no longer be a Static placeholder
            assert not isinstance(panel, Static)

    import asyncio
    asyncio.run(check_lazy_loading())
