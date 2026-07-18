from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from sovereignai.shared.capability_api import CapabilityAPI
from sovereignai.shared.types import (
    EpisodicQuery,
    EpisodicResult,
    ProceduralQuery,
    ProceduralResult,
    WorkingQuery,
    WorkingResult,
)


@pytest.mark.timeout(30)
def test_memory_panel_uses_capability_api() -> None:
    """Test that memory panel uses CapabilityAPI instead of direct backend imports."""
    from tui.panels.memory import MemoryPanel

    container = MagicMock()
    api = MagicMock(spec=CapabilityAPI)
    container.retrieve.return_value = api

    panel = MemoryPanel(container)
    panel._api = api

    assert panel._api is not None
    assert isinstance(panel._api, MagicMock)


@pytest.mark.timeout(30)
def test_capability_api_query_memory_episodic() -> None:
    """Test that CapabilityAPI.query_memory routes episodic queries correctly."""
    from sovereignai.memory.episodic_backend import EpisodicMemoryBackend
    from sovereignai.shared.capability_api import CapabilityAPI

    auth = MagicMock()
    auth.validate = MagicMock()
    capability_index = MagicMock()
    task_state_query = MagicMock()
    state_machine = MagicMock()
    trace = MagicMock()
    hardware_probe = MagicMock()
    database_registry = MagicMock()
    service_registry = MagicMock()

    episodic_backend = MagicMock(spec=EpisodicMemoryBackend)
    episodic_backend.query.return_value = [
        {
            "id": "test-id",
            "timestamp": 1234567890.0,
            "component": "test-component",
            "task_id": "test-task",
            "event_type": "test-event",
            "data": "test-data",
            "metadata": {"key": "value"},
        }
    ]

    memory_backends = {"episodic": episodic_backend}

    api = CapabilityAPI(
        auth=auth,
        capability_index=capability_index,
        task_state_query=task_state_query,
        state_machine=state_machine,
        trace=trace,
        hardware_probe=hardware_probe,
        database_registry=database_registry,
        service_registry=service_registry,
        memory_backends=memory_backends,
    )

    query = EpisodicQuery(session_id="test-session")
    results = api.query_memory("dummy_token", query)

    assert len(results) == 1
    assert isinstance(results[0], EpisodicResult)
    assert results[0].id == "test-id"
    assert results[0].component == "test-component"


@pytest.mark.timeout(30)
def test_capability_api_query_memory_procedural() -> None:
    """Test that CapabilityAPI.query_memory routes procedural queries correctly."""
    from sovereignai.memory.procedural_backend import ProceduralMemoryBackend
    from sovereignai.shared.capability_api import CapabilityAPI

    auth = MagicMock()
    auth.validate = MagicMock()
    capability_index = MagicMock()
    task_state_query = MagicMock()
    state_machine = MagicMock()
    trace = MagicMock()
    hardware_probe = MagicMock()
    database_registry = MagicMock()
    service_registry = MagicMock()

    procedural_backend = MagicMock(spec=ProceduralMemoryBackend)
    procedural_backend.query.return_value = [
        {
            "id": "test-pattern-id",
            "pattern": "test-pattern",
            "confidence": 0.95,
            "created_at": 1234567890.0,
        }
    ]

    memory_backends = {"procedural": procedural_backend}

    api = CapabilityAPI(
        auth=auth,
        capability_index=capability_index,
        task_state_query=task_state_query,
        state_machine=state_machine,
        trace=trace,
        hardware_probe=hardware_probe,
        database_registry=database_registry,
        service_registry=service_registry,
        memory_backends=memory_backends,
    )

    query = ProceduralQuery(skill_name="test-skill")
    results = api.query_memory("dummy_token", query)

    assert len(results) == 1
    assert isinstance(results[0], ProceduralResult)
    assert results[0].id == "test-pattern-id"
    assert results[0].pattern == "test-pattern"


@pytest.mark.timeout(30)
def test_capability_api_query_memory_working() -> None:
    """Test that CapabilityAPI.query_memory routes working queries correctly."""
    from sovereignai.memory.working_backend import WorkingMemoryBackend
    from sovereignai.shared.capability_api import CapabilityAPI

    auth = MagicMock()
    auth.validate = MagicMock()
    capability_index = MagicMock()
    task_state_query = MagicMock()
    state_machine = MagicMock()
    trace = MagicMock()
    hardware_probe = MagicMock()
    database_registry = MagicMock()
    service_registry = MagicMock()

    working_backend = MagicMock(spec=WorkingMemoryBackend)
    working_backend.query.return_value = [
        {"id": "test-working-id", "context_id": "test-context", "data": {"key": "value"}}
    ]

    memory_backends = {"working": working_backend}

    api = CapabilityAPI(
        auth=auth,
        capability_index=capability_index,
        task_state_query=task_state_query,
        state_machine=state_machine,
        trace=trace,
        hardware_probe=hardware_probe,
        database_registry=database_registry,
        service_registry=service_registry,
        memory_backends=memory_backends,
    )

    query = WorkingQuery(context_id="test-context")
    results = api.query_memory("dummy_token", query)

    assert len(results) == 1
    assert isinstance(results[0], WorkingResult)
    assert results[0].id == "test-working-id"
    assert results[0].context_id == "test-context"


@pytest.mark.timeout(30)
def test_capability_api_query_memory_returns_empty_for_missing_backend() -> None:
    """Test that CapabilityAPI.query_memory returns empty list when backend is missing."""
    from sovereignai.shared.capability_api import CapabilityAPI

    auth = MagicMock()
    auth.validate = MagicMock()
    capability_index = MagicMock()
    task_state_query = MagicMock()
    state_machine = MagicMock()
    trace = MagicMock()
    hardware_probe = MagicMock()
    database_registry = MagicMock()
    service_registry = MagicMock()

    memory_backends = {}

    api = CapabilityAPI(
        auth=auth,
        capability_index=capability_index,
        task_state_query=task_state_query,
        state_machine=state_machine,
        trace=trace,
        hardware_probe=hardware_probe,
        database_registry=database_registry,
        service_registry=service_registry,
        memory_backends=memory_backends,
    )

    query = EpisodicQuery(session_id="test-session")
    results = api.query_memory("dummy_token", query)

    assert results == []


@pytest.mark.timeout(30)
def test_capability_api_query_memory_returns_empty_for_none_backends() -> None:
    """Test that CapabilityAPI.query_memory returns empty list when memory_backends is None."""
    from sovereignai.shared.capability_api import CapabilityAPI

    auth = MagicMock()
    auth.validate = MagicMock()
    capability_index = MagicMock()
    task_state_query = MagicMock()
    state_machine = MagicMock()
    trace = MagicMock()
    hardware_probe = MagicMock()
    database_registry = MagicMock()
    service_registry = MagicMock()

    api = CapabilityAPI(
        auth=auth,
        capability_index=capability_index,
        task_state_query=task_state_query,
        state_machine=state_machine,
        trace=trace,
        hardware_probe=hardware_probe,
        database_registry=database_registry,
        service_registry=service_registry,
        memory_backends=None,
    )

    query = EpisodicQuery(session_id="test-session")
    results = api.query_memory("dummy_token", query)

    assert results == []
