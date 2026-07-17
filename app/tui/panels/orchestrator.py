from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, Input, RichLog, Static

from app.sovereignai.shared.capability_api import CapabilityAPI
from app.sovereignai.shared.types import CapabilityCategory


class OrchestratorPanel(Vertical):
    def __init__(self, container: Any, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._container = container
        self._api = None

    def compose(self) -> ComposeResult:
        yield Static("Orchestrator", id="orchestrator-title")
        yield Input(placeholder="Enter your message...", id="message-input")
        yield Button("Send", id="btn-send")
        yield RichLog(id="chat-log", auto_scroll=True)

    def on_mount(self) -> None:
        self.call_after_refresh(self._load_data)

    def _load_data(self) -> None:
        try:
            self._api = self._container.retrieve(CapabilityAPI)
            self._populate_model_selector()
        except Exception as e:
            import traceback
            print(f"OrchestratorPanel load error: {e}")
            traceback.print_exc()

    def _populate_model_selector(self) -> None:
        pass

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-send":
            await self._send_message()

    async def _send_message(self) -> None:
        if self._api is None:
            return
        input_widget = self.query_one("#message-input", Input)
        message = input_widget.value
        if not message:
            return

        log = self.query_one("#chat-log", RichLog)
        log.write(f"You: {message}")
        input_widget.value = ""

        try:
            from sovereignai.shared.auth import AuthMiddleware

            auth = self._container.retrieve(AuthMiddleware)
            token = auth.generate_token("test-user")
            task_id = self._api.submit_task(
                token,
                CapabilityCategory.MODEL_INFERENCE,
                "generate",
                message
            )
            log.write(f"Assistant: Task {task_id} submitted")
        except Exception as e:
            log.write(f"[red]Error: {e}[/red]")
