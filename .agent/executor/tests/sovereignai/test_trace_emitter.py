from __future__ import annotations

import threading
from uuid import UUID

import pytest
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import TraceLevel


@pytest.fixture
def trace_emitter() -> TraceEmitter:
    return TraceEmitter()

def test_emit_records_event(trace_emitter: TraceEmitter) -> None:
    trace_emitter.emit(component='TestComponent', level=TraceLevel.INFO, message='Test message')
    events = trace_emitter.get_events()
    assert len(events) == 1
    assert events[0].component == 'TestComponent'
    assert events[0].level == TraceLevel.INFO
    assert events[0].message == 'Test message'

def test_emit_with_level_filter(trace_emitter: TraceEmitter) -> None:
    trace_emitter.emit(component='Test', level=TraceLevel.TRACE, message='trace')
    trace_emitter.emit(component='Test', level=TraceLevel.DEBUG, message='debug')
    trace_emitter.emit(component='Test', level=TraceLevel.INFO, message='info')
    trace_emitter.emit(component='Test', level=TraceLevel.WARN, message='warn')
    trace_emitter.emit(component='Test', level=TraceLevel.ERROR, message='error')
    events = trace_emitter.get_events(level=TraceLevel.WARN)
    assert len(events) == 2
    assert events[0].level == TraceLevel.WARN
    assert events[1].level == TraceLevel.ERROR

def test_emit_with_component_filter(trace_emitter: TraceEmitter) -> None:
    trace_emitter.emit(component='ComponentA', level=TraceLevel.INFO, message='a')
    trace_emitter.emit(component='ComponentB', level=TraceLevel.INFO, message='b')
    trace_emitter.emit(component='ComponentA', level=TraceLevel.INFO, message='a2')
    events = trace_emitter.get_events(component='ComponentA')
    assert len(events) == 2
    assert all(e.component == 'ComponentA' for e in events)

def test_max_events_drops_oldest(trace_emitter: TraceEmitter) -> None:
    small_emitter = TraceEmitter(max_events=5)
    for i in range(10):
        small_emitter.emit(component='Test', level=TraceLevel.INFO, message=f'message {i}')
    events = small_emitter.get_events()
    assert len(events) == 5
    assert events[0].message == 'message 5'
    assert events[-1].message == 'message 9'

def test_thread_safety(trace_emitter: TraceEmitter) -> None:
    num_threads = 10
    emits_per_thread = 100

    def emit_many() -> None:
        for i in range(emits_per_thread):
            trace_emitter.emit(  # noqa: E501
                component='ThreadTest',
                level=TraceLevel.INFO,
                message=f'message {i}'
            )
    threads = [threading.Thread(target=emit_many) for _ in range(num_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    events = trace_emitter.get_events()
    assert len(events) == num_threads * emits_per_thread

def test_correlation_id_default_generated(trace_emitter: TraceEmitter) -> None:
    trace_emitter.emit(component='Test', level=TraceLevel.INFO, message='test', correlation_id=None)
    events = trace_emitter.get_events()
    assert len(events) == 1
    assert isinstance(events[0].correlation_id, UUID)
    assert events[0].correlation_id is not None
