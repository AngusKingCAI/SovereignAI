from unittest.mock import Mock

import pytest
from sovereignai.shared.capability_graph import ICapabilityIndex
from sovereignai.shared.lifecycle_manager import LifecycleManager
from sovereignai.shared.routing_engine import RoutingEngine
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import (
    AdapterHealth,
    AdapterUnavailableError,
    ComponentMetadata,
    NoHealthyAdapterError,
)


@pytest.fixture
def trace() -> TraceEmitter:
    return TraceEmitter()


@pytest.fixture
def lifecycle(trace: TraceEmitter) -> LifecycleManager:
    return LifecycleManager(trace=trace)


@pytest.fixture
def capability_index(trace: TraceEmitter) -> ICapabilityIndex:
    index = Mock(spec=ICapabilityIndex)
    index._trace = trace
    return index


@pytest.fixture
def router(  # noqa: E501
    capability_index: ICapabilityIndex,
    lifecycle: LifecycleManager,
    trace: TraceEmitter
) -> RoutingEngine:
    return RoutingEngine(  # noqa: E501
        capability_index=capability_index,
        lifecycle_manager=lifecycle,
        trace=trace
    )


@pytest.fixture
def mock_adapter_a():
    adapter = Mock()
    adapter.health_check.return_value = AdapterHealth(healthy=True, detail="OK")
    adapter.test_method.return_value = "result_a"
    return adapter


@pytest.fixture
def mock_adapter_b():
    adapter = Mock()
    adapter.health_check.return_value = AdapterHealth(healthy=True, detail="OK")
    adapter.test_method.return_value = "result_b"
    return adapter


def test_failover(
    router: RoutingEngine,
    capability_index: ICapabilityIndex,
    mock_adapter_a,
    mock_adapter_b,
):
    """Test failover when first adapter raises AdapterUnavailableError"""
    meta_a = ComponentMetadata(
        component_id="adapter_a",
        version="1.0.0",
        capabilities=(),
        routing_priority=10,
    )
    meta_b = ComponentMetadata(
        component_id="adapter_b",
        version="1.0.0",
        capabilities=(),
        routing_priority=20,
    )

    capability_index.adapters_by_capability.return_value = [meta_a, meta_b]
    capability_index.get_adapter.side_effect = [mock_adapter_a, mock_adapter_b]

    mock_adapter_a.test_method.side_effect = AdapterUnavailableError("Failed")

    result = router.route("model_inference", "test_method")
    assert result == "result_b"
    assert mock_adapter_b.test_method.called


def test_single_adapter(router: RoutingEngine, capability_index: ICapabilityIndex, mock_adapter_a):
    """Test single adapter returns its result"""
    meta_a = ComponentMetadata(
        component_id="adapter_a",
        version="1.0.0",
        capabilities=(),
        routing_priority=10,
    )

    capability_index.adapters_by_capability.return_value = [meta_a]
    capability_index.get_adapter.return_value = mock_adapter_a

    result = router.route("model_inference", "test_method")
    assert result == "result_a"


def test_single_adapter_raises_adapter_unavailable_error_propagates_to_no_healthy(
    router: RoutingEngine,
    capability_index: ICapabilityIndex,
    mock_adapter_a,
):
    """Test single adapter raising AdapterUnavailableError results in NoHealthyAdapterError"""
    meta_a = ComponentMetadata(
        component_id="adapter_a",
        version="1.0.0",
        capabilities=(),
        routing_priority=10,
    )

    capability_index.adapters_by_capability.return_value = [meta_a]
    capability_index.get_adapter.return_value = mock_adapter_a

    mock_adapter_a.test_method.side_effect = AdapterUnavailableError("Test error")

    with pytest.raises(NoHealthyAdapterError):
        router.route("model_inference", "test_method")


def test_all_unhealthy(
    router: RoutingEngine,
    capability_index: ICapabilityIndex,
    mock_adapter_a,
    mock_adapter_b,
):
    """Test all unhealthy adapters raise NoHealthyAdapterError"""
    meta_a = ComponentMetadata(
        component_id="adapter_a",
        version="1.0.0",
        capabilities=(),
        routing_priority=10,
    )
    meta_b = ComponentMetadata(
        component_id="adapter_b",
        version="1.0.0",
        capabilities=(),
        routing_priority=20,
    )

    capability_index.adapters_by_capability.return_value = [meta_a, meta_b]
    capability_index.get_adapter.side_effect = [mock_adapter_a, mock_adapter_b]

    mock_adapter_a.health_check.return_value = AdapterHealth(healthy=False, detail="Error")
    mock_adapter_b.health_check.return_value = AdapterHealth(healthy=False, detail="Error")

    with pytest.raises(NoHealthyAdapterError):
        router.route("model_inference", "test_method")


def test_health_check_filter_skips_unhealthy_adapter(
    router: RoutingEngine,
    capability_index: ICapabilityIndex,
    mock_adapter_a,
    mock_adapter_b,
):
    """Test health_check filter skips unhealthy adapter"""
    meta_a = ComponentMetadata(
        component_id="adapter_a",
        version="1.0.0",
        capabilities=(),
        routing_priority=10,
    )
    meta_b = ComponentMetadata(
        component_id="adapter_b",
        version="1.0.0",
        capabilities=(),
        routing_priority=20,
    )

    capability_index.adapters_by_capability.return_value = [meta_a, meta_b]
    capability_index.get_adapter.side_effect = [mock_adapter_a, mock_adapter_b]

    mock_adapter_a.health_check.return_value = AdapterHealth(healthy=False, detail="Error")
    mock_adapter_b.health_check.return_value = AdapterHealth(healthy=True, detail="OK")

    result = router.route("model_inference", "test_method")
    assert result == "result_b"
    assert not mock_adapter_a.test_method.called


def test_cpu_only_healthy(router: RoutingEngine, capability_index: ICapabilityIndex):
    """Test CPU-only llama.cpp (requested_n_gpu_layers=0) is healthy and routes successfully"""
    mock_llama = Mock()
    mock_llama.health_check.return_value = AdapterHealth(healthy=True, detail="OK")
    mock_llama.test_method.return_value = "llama_result"

    meta = ComponentMetadata(
        component_id="llama_cpp_adapter",
        version="1.0.0",
        capabilities=(),
        routing_priority=20,
    )

    capability_index.adapters_by_capability.return_value = [meta]
    capability_index.get_adapter.return_value = mock_llama

    result = router.route("model_inference", "test_method")
    assert result == "llama_result"


def test_manifest_without_routing_priority_defaults_to_1000_and_sorts_last(
    router: RoutingEngine,
    capability_index: ICapabilityIndex,
):
    """Test manifest without routing_priority defaults to 1000 and sorts last"""
    mock_adapter_a = Mock()
    mock_adapter_a.health_check.return_value = AdapterHealth(healthy=True, detail="OK")
    mock_adapter_a.test_method.return_value = "result_a"

    mock_adapter_b = Mock()
    mock_adapter_b.health_check.return_value = AdapterHealth(healthy=True, detail="OK")
    mock_adapter_b.test_method.return_value = "result_b"

    meta_a = ComponentMetadata(
        component_id="adapter_a",
        version="1.0.0",
        capabilities=(),
        routing_priority=10,
    )
    meta_b = ComponentMetadata(
        component_id="adapter_b",
        version="1.0.0",
        capabilities=(),
        routing_priority=1000,  # default
    )

    capability_index.adapters_by_capability.return_value = [meta_a, meta_b]
    capability_index.get_adapter.side_effect = [mock_adapter_a, mock_adapter_b]

    result = router.route("model_inference", "test_method")
    assert result == "result_a"  # Lower priority (10) routes first


def test_get_adapter_returns_instance(
    router: RoutingEngine,
    capability_index: ICapabilityIndex,
    mock_adapter_a,
):
    """Test get_adapter() returns instance for route() to invoke"""
    meta = ComponentMetadata(
        component_id="adapter_a",
        version="1.0.0",
        capabilities=(),
        routing_priority=10,
    )

    capability_index.adapters_by_capability.return_value = [meta]
    capability_index.get_adapter.return_value = mock_adapter_a

    result = router.route("model_inference", "test_method")
    assert result == "result_a"
    assert capability_index.get_adapter.called


def test_get_adapter_none_skip(
    router: RoutingEngine,
    capability_index: ICapabilityIndex,
):
    """Test get_adapter() returns None -> route() emits WARN trace and skips"""
    meta_a = ComponentMetadata(
        component_id="adapter_a",
        version="1.0.0",
        capabilities=(),
        routing_priority=10,
    )
    meta_b = ComponentMetadata(
        component_id="adapter_b",
        version="1.0.0",
        capabilities=(),
        routing_priority=20,
    )

    capability_index.adapters_by_capability.return_value = [meta_a, meta_b]
    capability_index.get_adapter.side_effect = [None, None]

    with pytest.raises(NoHealthyAdapterError):
        router.route("model_inference", "test_method")
