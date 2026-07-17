from __future__ import annotations

from textual.app import App, ComposeResult
from textual.widgets import Static


class SimpleTestApp(App):
    def compose(self) -> ComposeResult:
        yield Static("Hello World - TUI is working!")


if __name__ == "__main__":
    app = SimpleTestApp()
    app.run()
