from __future__ import annotations

from datetime import UTC
from typing import Any

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, DataTable, Static

from sovereignai.shared.task_state_machine import ITaskStateQuery, TaskState


class TasksPanel(Vertical):
    def __init__(self, container: Any, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._container = container
        self._task_state_query = container.retrieve(ITaskStateQuery)

    def compose(self) -> ComposeResult:
        yield Static("Tasks", id="tasks-title")
        yield Button("Create Task", id="btn-create-task")
        yield DataTable(id="tasks-table")

    def on_mount(self) -> None:
        self._refresh_tasks()

    def _refresh_tasks(self) -> None:
        table = self.query_one("#tasks-table", DataTable)
        table.clear(columns=True)
        table.add_column("ID")
        table.add_column("Department")
        table.add_column("State")
        table.add_column("Age")
        table.add_column("Actions")

        tasks = self._task_state_query.list_tasks()

        from datetime import datetime
        now = datetime.now(UTC)

        for task in tasks:
            state = self._task_state_query.get_state(task.task_id)
            if state:
                age_seconds = (
                    (now - task.created_at).total_seconds()
                    if hasattr(task, "created_at")
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
                color = color_map.get(state, "")

                table.add_row(
                    f"{color}{str(task.task_id)[:8]}...[/]",
                    "General",
                    f"{color}{state.value}[/]",
                    f"{age_minutes}m",
                    "[Cancel]"
                )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-refresh":
            self._refresh_tasks()
