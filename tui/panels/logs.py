from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, RichLog, Static

from sovereignai.shared.trace_emitter import TraceEmitter


class LogsPanel(Vertical):
    def __init__(self, container: Any, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._container = container
        self._trace = container.retrieve(TraceEmitter)

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
        self._load_all_events()

    def _load_all_events(self) -> None:
        log = self.query_one("#trace-log", RichLog)
        log.clear()

        for event in self._trace.get_events():
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
        log = self.query_one("#trace-log", RichLog)
        log.clear()

        filter_level = event.button.id
        if filter_level:
            filter_level = filter_level.replace("btn-", "")

        for trace_event in self._trace.get_events():
            level = (
                trace_event.level.value
                if hasattr(trace_event.level, "value")
                else str(trace_event.level)
            )

            if filter_level == "all" or level == filter_level:
                self._append_event(trace_event)
