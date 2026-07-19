from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sovereignai.orchestrator.classifier import (
    Department,
    IntentClassifier,
    RuleBasedClassifier,
)
from sovereignai.orchestrator.router import DepartmentRouter
from sovereignai.orchestrator.state import (
    ConversationState,
    ConversationStateManager,
    Message,
)
from sovereignai.shared.container import DIContainer
from sovereignai.shared.event_bus import EventBus
from sovereignai.shared.trace_emitter import TraceEmitter, TraceLevel
from sovereignai.shared.types import Channel, Event

if TYPE_CHECKING:
    pass


class Orchestrator:

    def __init__(
        self,
        container: DIContainer,
        classifier: IntentClassifier | None = None,
        db_path: str = "orchestrator_state.db",
    ) -> None:
        self._container = container
        self._classifier = classifier or RuleBasedClassifier()
        self._router = DepartmentRouter(container)
        self._state_manager = ConversationStateManager(db_path)
        self._event_bus = container.retrieve(EventBus)
        self._trace = container.retrieve(TraceEmitter)
        self._current_session: ConversationState | None = None
        self._subscribe_to_events()
        self._trace.emit(
            component="Orchestrator",
            level=TraceLevel.INFO,
            message="Orchestrator initialized",
        )

    async def handle_message(self, user_message: str) -> str:
        classification = await self._classifier.classify(user_message)

        if classification.department == Department.UNKNOWN:
            await self._emit_clarification_needed(user_message)
            return (
                "I'm not sure which department should handle this request. "
                "Could you provide more context?"
            )

        manager = await self._router.route(classification)
        if manager is None:
            await self._emit_clarification_needed(user_message)
            return f"The {classification.department.value} department is not yet available."

        await self._ensure_session()
        if self._current_session is None:
            return "Session initialization failed"

        self._current_session.message_history.append(
            Message(role="user", content=user_message)
        )
        self._current_session.active_department = classification.department.value

        try:
            deliverable = await manager.execute_task(user_message)
            response = self._translate_result(deliverable)
            self._current_session.message_history.append(
                Message(role="assistant", content=response)
            )
            await self._state_manager.save_state(self._current_session)
            await self._emit_response_ready(response)
            return response
        except Exception as e:
            self._trace.emit(
                component="Orchestrator",
                level=TraceLevel.ERROR,
                message=f"Task execution failed: {e}",
            )
            return f"Sorry, I encountered an error: {e}"

    async def _ensure_session(self) -> None:
        if self._current_session is None:
            self._current_session = await self._state_manager.create_session()

    def _subscribe_to_events(self) -> None:
        def on_owner_message(event: Event) -> None:
            if event.channel == Channel("owner.message.received"):
                message = event.payload.get("message", "")
                self._trace.emit(
                    component="Orchestrator",
                    level=TraceLevel.INFO,
                    message=f"Received owner message: {message[:50]}",
                )

        self._event_bus.subscribe(Channel("owner.message.received"), on_owner_message)

    def _translate_result(self, deliverable: Any) -> str:
        if deliverable.success:
            output = str(deliverable.output)
            if output and len(output) > 1000:
                output = output[:1000] + "..."
            return output
        else:
            return f"Task failed: {deliverable.output}"

    async def _emit_clarification_needed(self, user_message: str) -> None:
        event = Event(
            channel=Channel("orchestrator.clarification_needed"),
            payload={"message": user_message},
        )
        self._event_bus.publish(event)
        self._trace.emit(
            component="Orchestrator",
            level=TraceLevel.INFO,
            message="Clarification needed for user message",
        )

    async def _emit_response_ready(self, response: str) -> None:
        event = Event(
            channel=Channel("orchestrator.response.ready"),
            payload={"response": response},
        )
        self._event_bus.publish(event)
        self._trace.emit(
            component="Orchestrator",
            level=TraceLevel.INFO,
            message="Response ready for owner",
        )

    async def shutdown(self) -> None:
        await self._router.shutdown()
        self._state_manager.close()
