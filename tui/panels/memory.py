from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, DataTable, RichLog, Static

from sovereignai.memory.episodic_backend import EpisodicMemoryBackend
from sovereignai.memory.procedural_backend import ProceduralMemoryBackend
from sovereignai.memory.trace_backend import TraceMemoryBackend
from sovereignai.memory.working_backend import WorkingMemoryBackend


class MemoryPanel(Vertical):
    def __init__(self, container: Any, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._container = container
        self._episodic = container.retrieve(EpisodicMemoryBackend)
        self._procedural = container.retrieve(ProceduralMemoryBackend)
        self._working = container.retrieve(WorkingMemoryBackend)
        self._trace = container.retrieve(TraceMemoryBackend)

    def compose(self) -> ComposeResult:
        yield Static("Memory Backends", id="memory-title")
        yield DataTable(id="memory-table")
        yield Button("Refresh", id="btn-refresh")
        yield Button("Test Write", id="btn-test-write")
        yield RichLog(id="trace-log")

    def on_mount(self) -> None:
        self._refresh_memory_table()

    def _refresh_memory_table(self) -> None:
        table = self.query_one("#memory-table", DataTable)
        table.clear(columns=True)
        table.add_column("Backend")
        table.add_column("Records")
        table.add_column("Last Write")

        backends = [
            ("Episodic", self._episodic),
            ("Procedural", self._procedural),
            ("Working", self._working),
            ("Trace", self._trace),
        ]

        for name, backend in backends:
            try:
                records = self._get_record_count(backend)
                last_write = self._get_last_write(backend)
                table.add_row(name, str(records), last_write or "N/A")
            except Exception as e:
                table.add_row(name, "Error", str(e))

    def _get_record_count(self, backend: Any) -> int:
        if isinstance(backend, WorkingMemoryBackend):
            return sum(len(records) for records in backend._store.values())
        elif hasattr(backend, "_conn") and backend._conn:
            cursor = backend._conn.cursor()
            if isinstance(backend, TraceMemoryBackend):
                cursor.execute("SELECT COUNT(*) FROM traces")
            else:
                cursor.execute("SELECT COUNT(*) FROM episodes")
            result = cursor.fetchone()[0]
            return int(result) if result is not None else 0
        return 0

    def _get_last_write(self, backend: Any) -> str | None:
        if hasattr(backend, "_conn") and backend._conn:
            cursor = backend._conn.cursor()
            if isinstance(backend, TraceMemoryBackend):
                cursor.execute("SELECT MAX(timestamp) FROM traces")
            else:
                cursor.execute("SELECT MAX(timestamp) FROM episodes")
            result = cursor.fetchone()[0]
            if result:
                from datetime import datetime
                return datetime.fromtimestamp(result).strftime("%Y-%m-%d %H:%M:%S")
        return None

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-refresh":
            self._refresh_memory_table()
        elif event.button.id == "btn-test-write":
            self._test_write()

    def _test_write(self) -> None:
        log = self.query_one("#trace-log", RichLog)
        log.write("Testing write to WorkingMemory...")

        try:
            test_data = {
                "task_id": "test-task-123",
                "key": "test_key",
                "value": "test_value"
            }
            record_id = self._working.store(test_data)
            log.write(f"[green]Success: Stored record {record_id}[/green]")

            retrieved = self._working.query({"task_id": "test-task-123"})
            log.write(f"[green]Success: Retrieved {len(retrieved)} records[/green]")

            self._refresh_memory_table()
        except Exception as e:
            log.write(f"[red]Error: {e}[/red]")
