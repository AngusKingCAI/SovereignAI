from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, DataTable, Static

from app.tui.client import TUIWebClient


class OptionsPanel(Vertical):
    """Options panel showing system options from /api/options/*.

    Extracts OptionsUpdate fields and displays option key-value pairs in editable list.
    Uses REST polling (SSE disabled per DEBT-7).
    """

    def __init__(
        self,
        client: TUIWebClient,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._client = client
        self._options_data: dict[str, Any] = {}

    def compose(self) -> ComposeResult:
        yield Static("System Options", id="options-title")
        yield Button("Refresh", id="btn-refresh")
        yield DataTable(id="options-table")

    def on_mount(self) -> None:
        self.call_after_refresh(self._load_data)

    async def _load_data(self) -> None:
        """Load options from /api/options/*."""
        try:
            async with self._client as client:
                # Try to get options list
                response = await client.get("/api/options")
                if response.status_code == 200:
                    self._options_data = response.json()
                    self._update_display()
                else:
                    self._update_error(f"HTTP {response.status_code}")
        except Exception as e:
            self._update_error(str(e))

    def _update_display(self) -> None:
        """Update display with option key-value pairs."""
        try:
            table = self.query_one("#options-table", DataTable)
            table.clear(columns=True)
            table.add_column("Option Key")
            table.add_column("Value")
            table.add_column("Type")
            table.add_column("Actions")

            if not self._options_data:
                table.add_row("--", "--", "--", "--")
                return

            # Display options as key-value pairs
            for key, value in self._options_data.items():
                value_str = str(value)
                value_type = type(value).__name__

                # Truncate long values
                if len(value_str) > 50:
                    value_str = value_str[:47] + "..."

                table.add_row(key, value_str, value_type, "[Edit]")
        except Exception:
            # Widget tree not mounted (e.g., during testing)
            pass

    def _update_error(self, error_msg: str) -> None:
        """Update display with error message."""
        try:
            table = self.query_one("#options-table", DataTable)
            table.clear(columns=True)
            table.add_column("Option Key")
            table.add_column("Value")
            table.add_column("Type")
            table.add_column("Actions")
            table.add_row(f"Error: {error_msg}", "--", "--", "--")
        except Exception:
            # Widget tree not mounted (e.g., during testing)
            pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-refresh":
            self.call_after_refresh(self._load_data)
