from __future__ import annotations

from uuid import UUID, uuid4

import pytest
from sovereignai.shared.auth import AuthMiddleware
from sovereignai.shared.capability_api import CapabilityAPI
from sovereignai.shared.capability_graph import CapabilityGraph, ICapabilityIndex
from sovereignai.shared.event_bus import EventBus
from sovereignai.shared.event_registry import EventRegistry
from sovereignai.shared.hardware_probe import HardwareProbe
from sovereignai.shared.task_state_machine import TaskStateMachine
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
    return TraceEmitter()

@pytest.fixture
def auth(trace: TraceEmitter) -> AuthMiddleware:
    return AuthMiddleware(trace=trace)

@pytest.fixture
def bus(trace: TraceEmitter) -> EventBus:
    registry = EventRegistry()
    return EventBus(trace=trace, registry=registry)

@pytest.fixture
def capability_index(trace: TraceEmitter) -> CapabilityGraph:
    return CapabilityGraph(trace=trace)

@pytest.fixture
def task_state_machine(bus: EventBus, trace: TraceEmitter) -> TaskStateMachine:
    return TaskStateMachine(bus=bus, trace=trace)

@pytest.fixture
def hardware_probe() -> HardwareProbe:
    return HardwareProbe()

@pytest.fixture
def api(  # noqa: E501
    auth: AuthMiddleware,
    capability_index: ICapabilityIndex,
    task_state_machine: TaskStateMachine,
    trace: TraceEmitter,
    hardware_probe: HardwareProbe
) -> CapabilityAPI:
    return CapabilityAPI(  # noqa: E501
        auth=auth,
        capability_index=capability_index,
        task_state_query=task_state_machine,
        state_machine=task_state_machine,
        trace=trace,
        hardware_probe=hardware_probe
    )

def test_query_capabilities_valid_token_returns_providers(  # noqa: E501
    api: CapabilityAPI,
    auth: AuthMiddleware,
    capability_index: CapabilityGraph
) -> None:
    auth.register_user('testuser', 'password')
    token = auth.login('testuser', 'password').token
    capability_index.register(  # noqa: E501
        ComponentManifest(
            component_id=ComponentId('TestProvider'),
            version='1.0.0',
            provides=(
                CapabilityDeclaration(
                    category=CapabilityCategory.TOOL,
                    name='websearch',
                    version='1.0.0',
                    priority=0
                ),
            ),
            requires=(),
            author='test',
            content_hash='abc123'
        )
    )
    from sovereignai.shared.types import CapabilityQuery
    response = api.query_capabilities(  # noqa: E501
        token,
        CapabilityQuery(category=CapabilityCategory.TOOL, name='websearch')
    )
    assert response.providers == (ComponentId('TestProvider'),)

def test_query_capabilities_invalid_token_raises(api: CapabilityAPI) -> None:
    from sovereignai.shared.types import CapabilityQuery
    with pytest.raises(AuthError):
        api.query_capabilities(  # noqa: E501
            'invalid_token',
            CapabilityQuery(category=CapabilityCategory.TOOL, name='websearch')
        )

def test_submit_task_valid_token_returns_uuid(  # noqa: E501
    api: CapabilityAPI,
    auth: AuthMiddleware,
    capability_index: CapabilityGraph
) -> None:
    auth.register_user('testuser', 'password')
    token = auth.login('testuser', 'password').token
    capability_index.register(  # noqa: E501
        ComponentManifest(
            component_id=ComponentId('TestProvider'),
            version='1.0.0',
            provides=(
                CapabilityDeclaration(
                    category=CapabilityCategory.TOOL,
                    name='websearch',
                    version='1.0.0',
                    priority=0
                ),
            ),
            requires=(),
            author='test',
            content_hash='abc123'
        )
    )
    task_id = api.submit_task(token, CapabilityCategory.TOOL, 'websearch', '{"query": "test"}')
    assert isinstance(task_id, UUID)

def test_submit_task_invalid_token_raises(api: CapabilityAPI) -> None:
    with pytest.raises(AuthError):
        api.submit_task('invalid_token', CapabilityCategory.TOOL, 'websearch', '{}')

def test_get_task_state_valid_token_returns_none_for_unknown(  # noqa: E501
    api: CapabilityAPI,
    auth: AuthMiddleware
) -> None:
    auth.register_user('testuser', 'password')
    token = auth.login('testuser', 'password').token
    state = api.get_task_state(token, uuid4())
    assert state is None

def test_get_task_state_invalid_token_raises(api: CapabilityAPI) -> None:
    with pytest.raises(AuthError):
        api.get_task_state('invalid_token', uuid4())

def test_submit_task_no_provider_raises(api: CapabilityAPI, auth: AuthMiddleware) -> None:
    auth.register_user('testuser', 'password')
    token = auth.login('testuser', 'password').token
    with pytest.raises(NoActiveProviderError):
        api.submit_task(token, CapabilityCategory.TOOL, 'nonexistent_capability', '{}')

def test_submit_task_with_category_param(  # noqa: E501
    api: CapabilityAPI,
    auth: AuthMiddleware,
    capability_index: CapabilityGraph
) -> None:
    auth.register_user('testuser', 'password')
    token = auth.login('testuser', 'password').token
    capability_index.register(  # noqa: E501
        ComponentManifest(
            component_id=ComponentId('ModelProvider'),
            version='1.0.0',
            provides=(
                CapabilityDeclaration(
                    category=CapabilityCategory.MODEL_INFERENCE,
                    name='text_generation',
                    version='1.0.0',
                    priority=0
                ),
            ),
            requires=(),
            author='test',
            content_hash='abc123'
        )
    )
    task_id = api.submit_task(  # noqa: E501
        token,
        CapabilityCategory.MODEL_INFERENCE,
        'text_generation',
        '{"prompt": "hello"}'
    )
    assert isinstance(task_id, UUID)

def test_submit_task_then_get_state_returns_received(  # noqa: E501
    api: CapabilityAPI,
    auth: AuthMiddleware,
    capability_index: CapabilityGraph,
    task_state_machine: TaskStateMachine
) -> None:
    auth.register_user('testuser', 'password')
    token = auth.login('testuser', 'password').token
    capability_index.register(  # noqa: E501
        ComponentManifest(
            component_id=ComponentId('TestProvider'),
            version='1.0.0',
            provides=(
                CapabilityDeclaration(
                    category=CapabilityCategory.TOOL,
                    name='websearch',
                    version='1.0.0',
                    priority=0
                ),
            ),
            requires=(),
            author='test',
            content_hash='abc123'
        )
    )
    task_id = api.submit_task(token, CapabilityCategory.TOOL, 'websearch', '{"query": "test"}')
    state = task_state_machine.get_state(task_id)
    assert state == TaskState.RECEIVED
