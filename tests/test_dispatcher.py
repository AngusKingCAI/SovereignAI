"""Tests for MessageDispatcher."""
from __future__ import annotations

from unittest.mock import Mock, patch
from uuid import uuid4

import pytest

from sovereignai.orchestrator.dispatcher import MessageDispatcher
from sovereignai.shared.capability_api import CapabilityAPI
from sovereignai.shared.capability_graph import CapabilityGraph
from sovereignai.shared.task_state_machine import ITaskStateQuery, Task, TaskState
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import (
    CapabilityCategory,
    CapabilityDeclaration,
    ComponentId,
    ComponentManifest,
)


@pytest.fixture
def trace() -> TraceEmitter:
    """Create a trace emitter for testing."""
    return TraceEmitter()


@pytest.fixture
def capability_graph(trace: TraceEmitter) -> CapabilityGraph:
    """Create a capability graph with test manifests."""
    graph = CapabilityGraph(trace=trace)

    # Register websearch skill
    websearch_manifest = ComponentManifest(
        component_id=ComponentId("websearch_skill"),
        version="0.1.0",
        author="user",
        content_hash="sha256:test",
        provides=(
            CapabilityDeclaration(
                category=CapabilityCategory.TOOL,
                name="web_search",
                version="1.0.0",
                priority=100,
            ),
        ),
        requires=(),
    )
    graph.register(websearch_manifest)

    # Register ollama adapter
    ollama_manifest = ComponentManifest(
        component_id=ComponentId("ollama_adapter"),
        version="0.1.0",
        author="user",
        content_hash="sha256:test",
        provides=(
            CapabilityDeclaration(
                category=CapabilityCategory.MODEL_INFERENCE,
                name="chat_completion",
                version="1.0.0",
                priority=100,
            ),
        ),
        requires=(),
    )
    graph.register(ollama_manifest)

    return graph


@pytest.fixture
def capability_api() -> CapabilityAPI:
    """Create a mock capability API."""
    api = Mock(spec=CapabilityAPI)
    api.submit_task = Mock(return_value=uuid4())
    return api


@pytest.fixture
def task_state_machine() -> ITaskStateQuery:
    """Create a mock task state machine."""
    machine = Mock(spec=ITaskStateQuery)
    machine.list_tasks = Mock(return_value=[])
    machine.get_state = Mock(return_value=TaskState.RECEIVED)
    return machine


@pytest.fixture
def dispatcher(
    capability_api: CapabilityAPI,
    capability_graph: CapabilityGraph,
    task_state_machine: ITaskStateQuery,
    trace: TraceEmitter,
) -> MessageDispatcher:
    """Create a message dispatcher for testing."""
    return MessageDispatcher(
        capability_api=capability_api,
        capability_graph=capability_graph,
        task_state_machine=task_state_machine,
        trace=trace,
    )


@pytest.mark.asyncio
async def test_dispatch_to_websearch_skill(
    dispatcher: MessageDispatcher,
    capability_api: CapabilityAPI,
    task_state_machine: ITaskStateQuery,
) -> None:
    """Test dispatch to websearch skill when message contains 'search' keyword."""
    # Mock the manifest file reading
    with patch("sovereignai.orchestrator.dispatcher.Path") as mock_path:
        mock_path.return_value.exists.return_value = True
        mock_path.return_value.open.return_value.__enter__.return_value.read.return_value = b"""
[component]
component_id = "websearch_skill"
intent_keywords = ["search", "find"]
"""

        task_id = uuid4()
        capability_api.submit_task = Mock(return_value=task_id)  # type: ignore[method-assign]

        task = Task(
            task_id=task_id,
            capability=CapabilityDeclaration(
                category=CapabilityCategory.TOOL,
                name="web_search",
                version="1.0.0",
            ),
            payload="search for python",
            submitted_at=Mock(),
        )
        task_state_machine.list_tasks = Mock(return_value=[task])  # type: ignore[method-assign]

        result = await dispatcher.dispatch("search for python", token="test-token")

        assert result.task_id == task_id
        capability_api.submit_task.assert_called_once()


@pytest.mark.asyncio
async def test_dispatch_to_ollama_adapter(
    dispatcher: MessageDispatcher,
    capability_api: CapabilityAPI,
    task_state_machine: ITaskStateQuery,
) -> None:
    """Test dispatch to ollama adapter when message contains 'chat' keyword."""
    with patch("sovereignai.orchestrator.dispatcher.Path") as mock_path:
        mock_path.return_value.exists.return_value = True
        mock_path.return_value.open.return_value.__enter__.return_value.read.return_value = b"""
[component]
component_id = "ollama_adapter"
intent_keywords = ["chat", "talk"]
"""

        task_id = uuid4()
        capability_api.submit_task = Mock(return_value=task_id)  # type: ignore[method-assign]

        task = Task(
            task_id=task_id,
            capability=CapabilityDeclaration(
                category=CapabilityCategory.MODEL_INFERENCE,
                name="chat_completion",
                version="1.0.0",
            ),
            payload="chat with me",
            submitted_at=Mock(),
        )
        task_state_machine.list_tasks = Mock(return_value=[task])  # type: ignore[method-assign]

        result = await dispatcher.dispatch("chat with me", token="test-token")

        assert result.task_id == task_id


@pytest.mark.asyncio
async def test_dispatch_no_match_fallback_to_ollama(
    dispatcher: MessageDispatcher,
    capability_api: CapabilityAPI,
    task_state_machine: ITaskStateQuery,
) -> None:
    """Test dispatch fallback to ollama when no skill matches."""
    with patch("sovereignai.orchestrator.dispatcher.Path") as mock_path:
        mock_path.return_value.exists.return_value = True
        # No intent_keywords in manifests

        task_id = uuid4()
        capability_api.submit_task = Mock(return_value=task_id)  # type: ignore[method-assign]

        task = Task(
            task_id=task_id,
            capability=CapabilityDeclaration(
                category=CapabilityCategory.MODEL_INFERENCE,
                name="chat_completion",
                version="1.0.0",
            ),
            payload="random message",
            submitted_at=Mock(),
        )
        task_state_machine.list_tasks = Mock(return_value=[task])  # type: ignore[method-assign]

        result = await dispatcher.dispatch("random message", token="test-token")

        assert result.task_id == task_id
        # Should route to ollama_adapter
        call_args = capability_api.submit_task.call_args
        assert call_args[1]["capability_name"] == "chat_completion"


@pytest.mark.asyncio
async def test_dispatch_trace_emission(
    dispatcher: MessageDispatcher,
    trace: TraceEmitter,
    task_state_machine: ITaskStateQuery,
) -> None:
    """Test that dispatch emits trace events."""
    with patch("sovereignai.orchestrator.dispatcher.Path") as mock_path:
        mock_path.return_value.exists.return_value = True
        mock_path.return_value.open.return_value.__enter__.return_value.read.return_value = b"""
[component]
component_id = "websearch_skill"
intent_keywords = ["search"]
"""

        task_id = uuid4()
        dispatcher._api.submit_task = Mock(return_value=task_id)  # type: ignore[method-assign]

        task = Task(
            task_id=task_id,
            capability=CapabilityDeclaration(
                category=CapabilityCategory.TOOL,
                name="web_search",
                version="1.0.0",
            ),
            payload="search test",
            submitted_at=Mock(),
        )
        task_state_machine.list_tasks = Mock(return_value=[task])  # type: ignore[method-assign]

        await dispatcher.dispatch("search test", token="test-token")

        events = trace.get_events()
        assert len(events) > 0
        assert any("Received message" in event.message for event in events)


@pytest.mark.asyncio
async def test_dispatch_async_return_no_blocking(
    dispatcher: MessageDispatcher,
    task_state_machine: ITaskStateQuery,
) -> None:
    """Test that dispatch returns immediately without blocking."""
    with patch("sovereignai.orchestrator.dispatcher.Path") as mock_path:
        mock_path.return_value.exists.return_value = True
        mock_path.return_value.open.return_value.__enter__.return_value.read.return_value = b"""
[component]
component_id = "websearch_skill"
intent_keywords = ["search"]
"""

        task_id = uuid4()
        dispatcher._api.submit_task = Mock(return_value=task_id)  # type: ignore[method-assign]

        task = Task(
            task_id=task_id,
            capability=CapabilityDeclaration(
                category=CapabilityCategory.TOOL,
                name="web_search",
                version="1.0.0",
            ),
            payload="search test",
            submitted_at=Mock(),
        )
        task_state_machine.list_tasks = Mock(return_value=[task])  # type: ignore[method-assign]

        # Dispatch should return immediately, not wait for task completion
        import asyncio
        start = asyncio.get_event_loop().time()
        await dispatcher.dispatch("search test", token="test-token")
        end = asyncio.get_event_loop().time()

        # Should complete very quickly (< 1 second)
        assert (end - start) < 1.0
