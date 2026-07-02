from __future__ import annotations

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Static


class SovereignTUI(App):
    CSS = """
    #sidebar {
        width: 25;
        dock: left;
    }
    #main-content {
        width: 1fr;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with Vertical(id="sidebar"):
                yield Static("SovereignAI TUI")
                yield Button("Orchestrator", id="btn-orchestrator")
                yield Button("Workers", id="btn-workers")
                yield Button("Tasks", id="btn-tasks")
                yield Button("Skills", id="btn-skills")
                yield Button("Memory", id="btn-memory")
                yield Button("Models", id="btn-models")
                yield Button("Adapters", id="btn-adapters")
                yield Button("Hardware", id="btn-hardware")
                yield Button("Options", id="btn-options")
                yield Button("Logs", id="btn-logs")
            with Vertical(id="main-content"):
                yield Static("Select a panel from the sidebar", id="content-display")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id is None:
            return
        content = self.query_one("#content-display", Static)
        content.update(f"Selected: {button_id.replace('btn-', '').capitalize()}")


if __name__ == "__main__":
    app = SovereignTUI()
    app.run()
