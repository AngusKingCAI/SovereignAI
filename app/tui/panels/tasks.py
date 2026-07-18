from __future__ import annotations

from datetime import UTC
from typing import Any

from sovereignai.shared.capability_api import CapabilityAPI
from sovereignai.shared.types import TaskState
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, DataTable, Static, RichLog


class TasksPanel(Vertical):
    def __init__(self, container: Any, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._container = container
        self._api = None

    def compose(self) -> ComposeResult:
        yield Static("Tasks", id="tasks-title")
        yield Button("Refresh", id="btn-refresh")
        yield Button("Create Task", id="btn-create-task")
        yield DataTable(id="tasks-table")
        yield Static("Agent Reasoning Trace", id="trace-title")
        yield RichLog(id="agent-trace-log", markup=True)

    def on_mount(self) -> None:
        self.call_after_refresh(self._load_data)

    def _load_data(self) -> None:
        try:
            self._api = self._container.retrieve(CapabilityAPI)
            self.call_after_refresh(self._refresh_tasks)
        except Exception as e:
            import traceback
            print(f"TasksPanel load error: {e}")
            traceback.print_exc()

    def _refresh_tasks(self) -> None:
        if self._api is None:
            return
        table = self.query_one("#tasks-table", DataTable)
        table.clear(columns=True)
        table.add_column("ID")
        table.add_column("Department")
        table.add_column("State")
        table.add_column("Age")
        table.add_column("Actions")

        from textual import work

        @work(thread=True)
        def fetch_tasks():
            from sovereignai.shared.auth import AuthError
            try:
                return self._api.query_task_states("dummy_token")
            except AuthError:
                return []

        tasks = fetch_tasks()

        from datetime import datetime
        now = datetime.now(UTC)

        for task in tasks:
            age_seconds = (
                (now - task.submitted_at).total_seconds()
                if hasattr(task, "submitted_at")
                else 0
            )
            age_minutes = int(age_seconds / 60) if age_seconds else 0

            color_map = {
                TaskState.RECEIVED: "[dim]",
                TaskState.QUEUED: "[yellow]",
                TaskState.EXECUTING: "[blue]",
                TaskState.COMPLETE: "[green]",
                TaskState.FAILED: "[red]",
            }
            color = color_map.get(task.state, "")

            table.add_row(
                f"{color}{str(task.task_id)[:8]}...[/]",
                "General",
                f"{color}{task.state.value}[/]",
                f"{age_minutes}m",
                "[Cancel]"
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-refresh":
            self._refresh_tasks()
        elif event.button.id == "btn-create-task":
            self._create_agent_task()

    def _create_agent_task(self) -> None:
        """Create and submit an agent task (placeholder for Plan 23 S8)."""
        # TODO: Implement agent task creation UI
        # For now, this is a placeholder per P23-F cookie auth requirement
        # TUI tasks panel should include session cookie in SSE request headers
        # If textual cannot attach cookie, defer stream consumption + DEBT.md entry
        self._log_trace("Agent task creation not yet implemented")

    def _log_trace(self, message: str) -> None:
        """Log message to agent reasoning trace display."""
        try:
            trace_log = self.query_one("#agent-trace-log", RichLog)
            trace_log.write(message)
        except Exception:
            pass

    def _update_agent_indicator(self, active: bool) -> None:
        """Update agent task indicator in the panel."""
        try:
            title = self.query_one("#tasks-title", Static)
            if active:
                title.update("Tasks [green]● Agent Active[/]")
            else:
                title.update("Tasks")
        except Exception:
            pass
