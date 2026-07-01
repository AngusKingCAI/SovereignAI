from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, Input, RichLog, Static

from sovereignai.shared.capability_api import CapabilityAPI
from sovereignai.shared.types import CapabilityCategory


class OrchestratorPanel(Vertical):
    def __init__(self, container: Any, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._container = container
        self._api = container.retrieve(CapabilityAPI)

    def compose(self) -> ComposeResult:
        yield Static("Orchestrator", id="orchestrator-title")
        yield Input(placeholder="Enter your message...", id="message-input")
        yield Button("Send", id="btn-send")
        yield RichLog(id="chat-log", auto_scroll=True)

    def on_mount(self) -> None:
        self._populate_model_selector()

    def _populate_model_selector(self) -> None:
        pass

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-send":
            await self._send_message()

    async def _send_message(self) -> None:
        input_widget = self.query_one("#message-input", Input)
        message = input_widget.value
        if not message:
            return

        log = self.query_one("#chat-log", RichLog)
        log.write(f"You: {message}")
        input_widget.value = ""

        try:
            token = "test-token"
            task_id = self._api.submit_task(
                token,
                CapabilityCategory.MODEL_INFERENCE,
                "generate",
                message
            )
            log.write(f"Assistant: Task {task_id} submitted")
        except Exception as e:
            log.write(f"[red]Error: {e}[/red]")
