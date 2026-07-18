from __future__ import annotations

from typing import Any

from sovereignai.shared.capability_api import CapabilityAPI
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, RichLog, Static


class LogsPanel(Vertical):
    def __init__(self, container: Any, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._container = container
        self._api = None

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

    def _load_data(self) -> None:
        try:
            self._api = self._container.retrieve(CapabilityAPI)
            self._load_logs()
        except Exception as e:
            import traceback
            print(f"LogsPanel load error: {e}")
            traceback.print_exc()

    def _load_logs(self) -> None:
        if self._api is None:
            return
        from textual import work

        @work(thread=True)
        def fetch_events():
            from sovereignai.shared.auth import AuthError
            try:
                return self._api.query_logs("dummy_token")
            except AuthError:
                return []

        events = fetch_events()
        log = self.query_one("#trace-log", RichLog)
        log.clear()

        for event in events:
            self._append_event(event)

    def _append_event(self, event: Any) -> None:
        log = self.query_one("#trace-log", RichLog)
        level = event.level.value if hasattr(event.level, 'value') else str(event.level)

        color_map = {
            "error": "[red]",
            "warn": "[yellow]",
            "info": "[green]",
            "debug": "[blue]",
            "trace": "[dim]",
        }
        color = color_map.get(level, "")

        log.write(f"{color}[{level.upper()}] {event.component}: {event.message}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if self._api is None:
            return
        log = self.query_one("#trace-log", RichLog)
        log.clear()

        filter_level = event.button.id
        if filter_level:
            filter_level = filter_level.replace("btn-", "")

        from textual import work

        @work(thread=True)
        def fetch_events():
            from sovereignai.shared.auth import AuthError
            try:
                return self._api.query_logs("dummy_token")
            except AuthError:
                return []

        events = fetch_events()
        for trace_event in events:
            level = (
                trace_event.level.value
                if hasattr(trace_event.level, "value")
                else str(trace_event.level)
            )

            if filter_level == "all" or level == filter_level:
                self._append_event(trace_event)
