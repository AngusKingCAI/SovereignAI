from __future__ import annotations

import asyncio

import pytest
from sovereignai.shared.auth import AuthMiddleware
from sovereignai.shared.capability_api import CapabilityAPI
from sovereignai.shared.capability_graph import CapabilityGraph
from sovereignai.shared.event_bus import EventBus
from sovereignai.shared.hardware_probe import HardwareProbe
from sovereignai.shared.task_state_machine import TaskStateMachine
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import HardwareSnapshot


def test_sample_hardware_returns_snapshot() -> None:
    trace = TraceEmitter()
    auth = AuthMiddleware(trace=trace)
    graph = CapabilityGraph(trace=trace, dev_mode=True)
    bus = EventBus(trace=trace)
    state_machine = TaskStateMachine(bus=bus, trace=trace)
    hardware_probe = HardwareProbe()

    api = CapabilityAPI(
        auth=auth,
        capability_index=graph,
        task_state_query=state_machine,
        state_machine=state_machine,
        trace=trace,
        hardware_probe=hardware_probe,
    )

    snapshot = api.sample_hardware()
    assert isinstance(snapshot, HardwareSnapshot)
    assert isinstance(snapshot.cpu_percent, float)
    assert isinstance(snapshot.ram_percent, float)
    assert isinstance(snapshot.disks, list)
    assert isinstance(snapshot.gpus, list)


@pytest.mark.asyncio
async def test_stream_hardware_yields_at_1hz() -> None:
    trace = TraceEmitter()
    auth = AuthMiddleware(trace=trace)
    graph = CapabilityGraph(trace=trace, dev_mode=True)
    bus = EventBus(trace=trace)
    state_machine = TaskStateMachine(bus=bus, trace=trace)
    hardware_probe = HardwareProbe()

    api = CapabilityAPI(
        auth=auth,
        capability_index=graph,
        task_state_query=state_machine,
        state_machine=state_machine,
        trace=trace,
        hardware_probe=hardware_probe,
    )

    count = 0
    start_time = asyncio.get_event_loop().time()

    async for snapshot in api.stream_hardware():
        assert isinstance(snapshot, HardwareSnapshot)
        count += 1
        if count >= 3:
            break

    elapsed = asyncio.get_event_loop().time() - start_time
    assert count == 3
    assert 2.0 < elapsed < 4.0
