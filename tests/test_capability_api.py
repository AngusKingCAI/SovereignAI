"""Tests for CapabilityAPI — public contract for UI processes."""
from __future__ import annotations

from uuid import UUID, uuid4

import pytest

from sovereignai.shared.auth import AuthMiddleware
from sovereignai.shared.capability_api import CapabilityAPI
from sovereignai.shared.capability_graph import (
    CapabilityGraph,
    ICapabilityIndex,
)
from sovereignai.shared.event_bus import EventBus
from sovereignai.shared.task_state_machine import (
    TaskStateMachine,
)
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import (
    AuthError,
    CapabilityCategory,
    CapabilityDeclaration,
    ComponentId,
    ComponentManifest,
    NoActiveProviderError,
    TaskState,
)


@pytest.fixture
def trace() -> TraceEmitter:
    """Create a TraceEmitter instance for testing."""
    return TraceEmitter()


@pytest.fixture
def auth(trace: TraceEmitter) -> AuthMiddleware:
    """Create an AuthMiddleware instance for testing."""
    return AuthMiddleware(trace=trace)


@pytest.fixture
def bus(trace: TraceEmitter) -> EventBus:
    """Create an EventBus instance for testing."""
    return EventBus(trace=trace)


@pytest.fixture
def capability_index(trace: TraceEmitter) -> ICapabilityIndex:
    """Create a CapabilityGraph instance for testing."""
    return CapabilityGraph(trace=trace)


@pytest.fixture
def task_state_machine(bus: EventBus, trace: TraceEmitter) -> TaskStateMachine:
    """Create a TaskStateMachine instance for testing."""
    return TaskStateMachine(bus=bus, trace=trace)


@pytest.fixture
def api(
    auth: AuthMiddleware,
    capability_index: ICapabilityIndex,
    task_state_machine: TaskStateMachine,
    trace: TraceEmitter,
) -> CapabilityAPI:
    """Create a CapabilityAPI instance wired to test fixtures."""
    return CapabilityAPI(
        auth=auth,
        capability_index=capability_index,
        task_state_query=task_state_machine,
        state_machine=task_state_machine,
        trace=trace,
    )


def test_query_capabilities_valid_token_returns_providers(
    api: CapabilityAPI, auth: AuthMiddleware, capability_index: ICapabilityIndex
) -> None:
    """Verify that query_capabilities with a valid token returns providers."""
    # Register a user and get a token
    auth.register_user("testuser", "password")
    token = auth.login("testuser", "password").token

    # Register a provider via manifest
    capability_index.register(
        ComponentManifest(
            component_id=ComponentId("TestProvider"),
            version="1.0.0",
            provides=(
                CapabilityDeclaration(
                    category=CapabilityCategory.TOOL,
                    name="websearch",
                    version="1.0.0",
                    priority=0,
                ),
            ),
            requires=(),
            author="test",
            content_hash="abc123",
        )
    )

    # Query capabilities
    from sovereignai.shared.types import CapabilityQuery

    response = api.query_capabilities(
        token, CapabilityQuery(category=CapabilityCategory.TOOL, name="websearch")
    )
    assert response.providers == (ComponentId("TestProvider"),)


def test_query_capabilities_invalid_token_raises(api: CapabilityAPI) -> None:
    """Verify that query_capabilities with an invalid token raises AuthError."""
    from sovereignai.shared.types import CapabilityQuery

    with pytest.raises(AuthError):
        api.query_capabilities(
            "invalid_token",
            CapabilityQuery(category=CapabilityCategory.TOOL, name="websearch"),
        )


def test_submit_task_valid_token_returns_uuid(
    api: CapabilityAPI,
    auth: AuthMiddleware,
    capability_index: ICapabilityIndex,
) -> None:
    """Verify that submit_task with a valid token returns a UUID."""
    # Register a user and get a token
    auth.register_user("testuser", "password")
    token = auth.login("testuser", "password").token

    # Register a provider via manifest
    capability_index.register(
        ComponentManifest(
            component_id=ComponentId("TestProvider"),
            version="1.0.0",
            provides=(
                CapabilityDeclaration(
                    category=CapabilityCategory.TOOL,
                    name="websearch",
                    version="1.0.0",
                    priority=0,
                ),
            ),
            requires=(),
            author="test",
            content_hash="abc123",
        )
    )

    # Submit a task
    task_id = api.submit_task(
        token, CapabilityCategory.TOOL, "websearch", '{"query": "test"}'
    )
    assert isinstance(task_id, UUID)


def test_submit_task_invalid_token_raises(api: CapabilityAPI) -> None:
    """Verify that submit_task with an invalid token raises AuthError."""
    with pytest.raises(AuthError):
        api.submit_task(
            "invalid_token", CapabilityCategory.TOOL, "websearch", "{}"
        )


def test_get_task_state_valid_token_returns_none_for_unknown(
    api: CapabilityAPI, auth: AuthMiddleware
) -> None:
    """Verify that get_task_state returns None for an unknown UUID (per Rev3 Finding 2)."""
    # Register a user and get a token
    auth.register_user("testuser", "password")
    token = auth.login("testuser", "password").token

    # Query state for a task that was never submitted
    state = api.get_task_state(token, uuid4())
    assert state is None


def test_get_task_state_invalid_token_raises(api: CapabilityAPI) -> None:
    """Verify that get_task_state with an invalid token raises AuthError."""
    with pytest.raises(AuthError):
        api.get_task_state("invalid_token", uuid4())


def test_submit_task_no_provider_raises(
    api: CapabilityAPI, auth: AuthMiddleware
) -> None:
    """Verify that submit_task for a capability with no provider raises NoActiveProviderError."""
    # Register a user and get a token
    auth.register_user("testuser", "password")
    token = auth.login("testuser", "password").token

    # Try to submit a task for a capability with no registered provider
    with pytest.raises(NoActiveProviderError):
        api.submit_task(
            token, CapabilityCategory.TOOL, "nonexistent_capability", "{}"
        )


def test_submit_task_with_category_param(
    api: CapabilityAPI,
    auth: AuthMiddleware,
    capability_index: ICapabilityIndex,
) -> None:
    """Verify that submit_task accepts a category parameter (per Rev3 Finding 2)."""
    # Register a user and get a token
    auth.register_user("testuser", "password")
    token = auth.login("testuser", "password").token

    # Register a MODEL_INFERENCE provider via manifest
    capability_index.register(
        ComponentManifest(
            component_id=ComponentId("ModelProvider"),
            version="1.0.0",
            provides=(
                CapabilityDeclaration(
                    category=CapabilityCategory.MODEL_INFERENCE,
                    name="text_generation",
                    version="1.0.0",
                    priority=0,
                ),
            ),
            requires=(),
            author="test",
            content_hash="abc123",
        )
    )

    # Submit a task with MODEL_INFERENCE category
    task_id = api.submit_task(
        token,
        CapabilityCategory.MODEL_INFERENCE,
        "text_generation",
        '{"prompt": "hello"}',
    )
    assert isinstance(task_id, UUID)


def test_submit_task_then_get_state_returns_received(
    api: CapabilityAPI,
    auth: AuthMiddleware,
    capability_index: ICapabilityIndex,
    task_state_machine: TaskStateMachine,
) -> None:
    """Verify that submit_task actually submits to the state machine (per Rev2 Finding 1)."""
    # Register a user and get a token
    auth.register_user("testuser", "password")
    token = auth.login("testuser", "password").token

    # Register a provider via manifest
    capability_index.register(
        ComponentManifest(
            component_id=ComponentId("TestProvider"),
            version="1.0.0",
            provides=(
                CapabilityDeclaration(
                    category=CapabilityCategory.TOOL,
                    name="websearch",
                    version="1.0.0",
                    priority=0,
                ),
            ),
            requires=(),
            author="test",
            content_hash="abc123",
        )
    )

    # Submit a task
    task_id = api.submit_task(
        token, CapabilityCategory.TOOL, "websearch", '{"query": "test"}'
    )

    # Verify the task is in RECEIVED state via the state machine
    state = task_state_machine.get_state(task_id)
    assert state == TaskState.RECEIVED
