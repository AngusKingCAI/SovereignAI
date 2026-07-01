from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, DataTable, Static

from sovereignai.shared.database_registry import DatabaseRegistry
from sovereignai.shared.model_catalog import ModelCatalog
from sovereignai.shared.trace_emitter import TraceEmitter


class ModelsPanel(Vertical):
    def __init__(self, container: Any, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._container = container
        self._database_registry = container.retrieve(DatabaseRegistry)
        self._trace = container.retrieve(TraceEmitter)
        self._model_catalog = ModelCatalog(self._database_registry, self._trace)

    def compose(self) -> ComposeResult:
        yield Static("Models", id="models-title")
        yield DataTable(id="models-table")

    def on_mount(self) -> None:
        self._refresh_models()

    def _refresh_models(self) -> None:
        table = self.query_one("#models-table", DataTable)
        table.clear(columns=True)
        table.add_column("Name")
        table.add_column("Size")
        table.add_column("Quantization")
        table.add_column("Status")
        table.add_column("Actions")

        from sovereignai.shared.types import ModelFilter
        models = self._model_catalog.list_models(ModelFilter(search=""))

        for model in models[:20]:
            size_gb = model.file_size_bytes / (1024**3) if model.file_size_bytes else 0
            table.add_row(
                f"{model.org}/{model.family}",
                f"{size_gb:.1f}GB",
                model.quant,
                "Available",
                "[Pull] [Load]"
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-refresh":
            self._refresh_models()
