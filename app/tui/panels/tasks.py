from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, DataTable, RichLog, Static

from app.tui.client import TUIWebClient


class TasksPanel(Vertical):
    """Tasks panel showing task events from /api/events/tasks.

    Uses REST polling fallback (5s interval) since SSE disabled per DEBT-7.
    Extracts TaskEventDTO fields: event_id, task_id, event_type, timestamp, details.
    Renders as scrollable event list grouped by task_id.
    """

    def __init__(
        self,
        client: TUIWebClient,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._client = client
        self._events_data: list[dict[str, Any]] = []
        self._last_event_id: int | None = None

    def compose(self) -> ComposeResult:
        yield Static("Task Events", id="tasks-title")
        yield Button("Refresh", id="btn-refresh")
        yield DataTable(id="tasks-table")
        yield Static("Event Details", id="event-details-title")
        yield RichLog(id="event-details-log", markup=True)

    def on_mount(self) -> None:
        self.call_after_refresh(self._load_data)

    async def _load_data(self) -> None:
        """Load task events from /api/events/tasks with since_event_id cursor."""
        try:
            params = {}
            if self._last_event_id is not None:
                params["since_event_id"] = self._last_event_id

            async with self._client as client:
                response = await client.get("/api/events/tasks", params=params)
                if response.status_code == 200:
                    new_events = response.json()
                    if new_events:
                        self._events_data.extend(new_events)
                        # Update cursor to latest event_id
                        self._last_event_id = max(
                            e.get("event_id", 0) for e in new_events
                        )
                    self._update_display()
                else:
                    self._update_error(f"HTTP {response.status_code}")
        except Exception as e:
            self._update_error(str(e))

    def _update_display(self) -> None:
        """Update display with task events grouped by task_id."""
        try:
            table = self.query_one("#tasks-table", DataTable)
            table.clear(columns=True)
            table.add_column("Event ID")
            table.add_column("Task ID")
            table.add_column("Event Type")
            table.add_column("Timestamp")

            if not self._events_data:
                table.add_row("--", "--", "--", "--")
                return

            # Group events by task_id
            from collections import defaultdict
            events_by_task = defaultdict(list)
            for event in self._events_data:
                task_id = event.get("task_id", "unknown")
                events_by_task[task_id].append(event)

            # Display latest event for each task
            for task_id, events in events_by_task.items():
                latest_event = max(events, key=lambda e: e.get("event_id", 0))
                event_id = str(latest_event.get("event_id", ""))[:8]
                event_type = latest_event.get("event_type", "unknown")
                timestamp = latest_event.get("timestamp", "")

                table.add_row(event_id, str(task_id)[:8], event_type, timestamp)
        except Exception:
            # Widget tree not mounted (e.g., during testing)
            pass

    def _update_error(self, error_msg: str) -> None:
        """Update display with error message."""
        try:
            table = self.query_one("#tasks-table", DataTable)
            table.clear(columns=True)
            table.add_column("Event ID")
            table.add_column("Task ID")
            table.add_column("Event Type")
            table.add_column("Timestamp")
            table.add_row(f"Error: {error_msg}", "--", "--", "--")
        except Exception:
            # Widget tree not mounted (e.g., during testing)
            pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-refresh":
            self.call_after_refresh(self._load_data)
