from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, ContentSwitcher, Footer, Header, Static

if TYPE_CHECKING:
    from tui.panels import PANEL_NAMES, PANEL_REGISTRY


class SovereignTUI(App):
    CSS_PATH = "sovereign.tcss"

    BINDINGS = [
        ("tab", "cycle_panel", "Cycle"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.container = None

    def compose(self) -> ComposeResult:
        from tui.panels import PANEL_NAMES, PANEL_REGISTRY

        yield Header()
        with Horizontal():
            with Vertical(id="sidebar"):
                yield Static("SovereignAI TUI", id="location-bar")
                for name in PANEL_NAMES:
                    yield Button(name.title(), id=f"btn-{name}")
            with ContentSwitcher(id="main-content"):
                for name, Cls in PANEL_REGISTRY:
                    yield Cls(self.container, id=f"panel-{name}")
        yield Footer()

    async def on_mount(self) -> None:
        from textual import work

        @work(thread=True)
        async def build_container() -> None:
            from sovereignai.main import build_container

            self.container = await self._build_container()

        await build_container()

    async def _build_container(self):
        from sovereignai.main import build_container

        return build_container()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id is None:
            return
        panel_name = button_id.replace("btn-", "")
        switcher = self.query_one("#main-content", ContentSwitcher)
        switcher.current = f"panel-{panel_name}"

    def action_cycle_panel(self) -> None:
        from tui.panels import PANEL_NAMES

        switcher = self.query_one("#main-content", ContentSwitcher)
        current = switcher.current
        if current is None:
            return
        current_name = current.replace("panel-", "")
        try:
            current_index = PANEL_NAMES.index(current_name)
            next_index = (current_index + 1) % len(PANEL_NAMES)
            switcher.current = f"panel-{PANEL_NAMES[next_index]}"
        except ValueError:
            pass


if __name__ == "__main__":
    app = SovereignTUI()
    app.run()
