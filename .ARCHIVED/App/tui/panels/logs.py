from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, RichLog, Static

from app.tui.client import TUIWebClient


class LogsPanel(Vertical):
    """Logs panel showing trace events from /api/trace/logs.

    Uses REST polling fallback (5s interval) since SSE disabled per DEBT-7.
    Extracts TraceEvent fields: timestamp, level, source, message.
    Renders as color-coded log view (ERROR=red, WARN=yellow, INFO=default).
    """

    def __init__(
        self,
        client: TUIWebClient,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._client = client
        self._logs_data: list[dict[str, Any]] = []
        self._filter_level: str = "all"

    def compose(self) -> ComposeResult:
        yield Static("System Logs", id="logs-title")
        yield Horizontal(
            Button("All", id="btn-all"),
            Button("ERROR", id="btn-error"),
            Button("WARN", id="btn-warn"),
            Button("INFO", id="btn-info"),
            Button("DEBUG", id="btn-debug"),
            id="filter-buttons"
        )
        yield RichLog(id="trace-log", auto_scroll=True)

    def on_mount(self) -> None:
        self.call_after_refresh(self._load_data)

    async def _load_data(self) -> None:
        """Load trace logs from /api/trace/logs."""
        try:
            async with self._client as client:
                response = await client.get("/api/trace/logs")
                if response.status_code == 200:
                    self._logs_data = response.json()
                    self._update_display()
                else:
                    self._update_error(f"HTTP {response.status_code}")
        except Exception as e:
            self._update_error(str(e))

    def _update_display(self) -> None:
        """Update display with filtered log entries."""
        try:
            log = self.query_one("#trace-log", RichLog)
            log.clear()

            for event in self._logs_data:
                level = event.get("level", "info").lower()

                # Apply filter
                if self._filter_level != "all" and level != self._filter_level:
                    continue

                self._append_event(event)
        except Exception:
            # Widget tree not mounted (e.g., during testing)
            pass

    def _append_event(self, event: dict[str, Any]) -> None:
        """Append a single log event with color coding."""
        try:
            log = self.query_one("#trace-log", RichLog)
            level = event.get("level", "info").lower()
            source = event.get("source", "unknown")
            message = event.get("message", "")
            timestamp = event.get("timestamp", "")

            # Color code log levels (ERROR=red, WARN=yellow, INFO=default)
            color_map = {
                "error": "[red]",
                "warn": "[yellow]",
                "warning": "[yellow]",
                "info": "",
                "debug": "[blue]",
                "trace": "[dim]",
            }
            color = color_map.get(level, "")

            log.write(f"{color}[{level.upper()}] {timestamp} {source}: {message}")
        except Exception:
            # Widget tree not mounted (e.g., during testing)
            pass

    def _update_error(self, error_msg: str) -> None:
        """Update display with error message."""
        try:
            log = self.query_one("#trace-log", RichLog)
            log.clear()
            log.write(f"[red]Error loading logs: {error_msg}")
        except Exception:
            # Widget tree not mounted (e.g., during testing)
            pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id.startswith("btn-"):
            self._filter_level = event.button.id.replace("btn-", "")
            self._update_display()
