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
                for name, module_path, class_name in PANEL_REGISTRY:
                    yield Static(f"Loading {name.title()}...", id=f"placeholder-{name}")
        yield Footer()

    def on_mount(self) -> None:
        self.call_after_refresh(self._load_container)

    def _load_container(self) -> None:
        from sovereignai.main import build_container

        self.container = build_container()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id is None:
            return
        panel_name = button_id.replace("btn-", "")
        self._load_panel(panel_name)
        switcher = self.query_one("#main-content", ContentSwitcher)
        switcher.current = f"panel-{panel_name}"

    def _load_panel(self, panel_name: str) -> None:
        from tui.panels import PANEL_REGISTRY

        placeholder_id = f"placeholder-{panel_name}"
        panel_id = f"panel-{panel_name}"
        placeholder = self.query_one(f"#{placeholder_id}", Static)

        if not isinstance(placeholder, Static):
            return

        for name, module_path, class_name in PANEL_REGISTRY:
            if name == panel_name:
                module = __import__(module_path, fromlist=[class_name])
                panel_class = getattr(module, class_name)
                panel = panel_class(self.container, id=panel_id)
                placeholder.remove()
                self.query_one("#main-content", ContentSwitcher).mount(panel)
                break

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
            next_name = PANEL_NAMES[next_index]
            self._load_panel(next_name)
            switcher.current = f"panel-{next_name}"
        except ValueError:
            pass


if __name__ == "__main__":
    app = SovereignTUI()
    app.run()
