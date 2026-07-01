from uuid import UUID

from sovereignai.shared.capability_api import CapabilityAPI
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import (
    CapabilityCategory,
    TraceLevel,
    bind_correlation_id,
    current_correlation_id,
    new_correlation_id,
    reset_correlation_id,
)


def test_emit_picks_up_contextvar():
    trace = TraceEmitter()
    cid = new_correlation_id()
    token = bind_correlation_id(cid)
    
    trace.emit(component="Test", level=TraceLevel.INFO, message="test")
    events = trace.get_events()
    
    reset_correlation_id(token)
    assert len(events) == 1
    assert events[0].correlation_id == cid


def test_emit_generates_fresh_when_no_context():
    trace = TraceEmitter()
    
    assert current_correlation_id() is None
    trace.emit(component="Test", level=TraceLevel.INFO, message="test")
    events = trace.get_events()
    
    assert len(events) == 1
    assert events[0].correlation_id is not None


def test_submit_task_binds_fresh_when_none():
    trace = TraceEmitter()
    
    class MockAuth:
        def validate(self, token: str) -> None:
            pass
    
    class MockIndex:
        def find_providers(self, category, name):
            return [("test_provider", type("Decl", (), {"version": "1.0.0"})())]
    
    class MockQuery:
        def get_state(self, task_id: UUID) -> None:
            return None
    
    class MockStateMachine:
        def submit(self, task) -> None:
            pass
    
    api = CapabilityAPI(
        auth=MockAuth(),
        capability_index=MockIndex(),
        task_state_query=MockQuery(),
        state_machine=MockStateMachine(),
        trace=trace,
    )
    
    task_id = api.submit_task("token", CapabilityCategory.MODEL_INFERENCE, "test", "payload")
    events = trace.get_events()
    
    assert len(events) == 1
    assert events[0].correlation_id is not None
    assert current_correlation_id() is None


def test_submit_task_inherits_when_present():
    trace = TraceEmitter()
    cid = new_correlation_id()
    token = bind_correlation_id(cid)
    
    class MockAuth:
        def validate(self, token: str) -> None:
            pass
    
    class MockIndex:
        def find_providers(self, category, name):
            return [("test_provider", type("Decl", (), {"version": "1.0.0"})())]
    
    class MockQuery:
        def get_state(self, task_id: UUID) -> None:
            return None
    
    class MockStateMachine:
        def submit(self, task) -> None:
            pass
    
    api = CapabilityAPI(
        auth=MockAuth(),
        capability_index=MockIndex(),
        task_state_query=MockQuery(),
        state_machine=MockStateMachine(),
        trace=trace,
    )
    
    task_id = api.submit_task("token", CapabilityCategory.MODEL_INFERENCE, "test", "payload")
    events = trace.get_events()
    
    reset_correlation_id(token)
    assert len(events) == 1
    assert events[0].correlation_id == cid


def test_nested_submit_task_inherits_parent_id():
    trace = TraceEmitter()
    cid = new_correlation_id()
    token = bind_correlation_id(cid)
    
    class MockAuth:
        def validate(self, token: str) -> None:
            pass
    
    class MockIndex:
        def find_providers(self, category, name):
            return [("test_provider", type("Decl", (), {"version": "1.0.0"})())]
    
    class MockQuery:
        def get_state(self, task_id: UUID) -> None:
            return None
    
    class MockStateMachine:
        def submit(self, task) -> None:
            pass
    
    api = CapabilityAPI(
        auth=MockAuth(),
        capability_index=MockIndex(),
        task_state_query=MockQuery(),
        state_machine=MockStateMachine(),
        trace=trace,
    )
    
    api.submit_task("token", CapabilityCategory.MODEL_INFERENCE, "test1", "payload1")
    api.submit_task("token", CapabilityCategory.MODEL_INFERENCE, "test2", "payload2")
    events = trace.get_events()
    
    reset_correlation_id(token)
    assert len(events) == 2
    assert all(e.correlation_id == cid for e in events)


def test_recent_events_returns_last_500():
    trace = TraceEmitter()
    
    for i in range(600):
        trace.emit(component="Test", level=TraceLevel.INFO, message=f"test {i}")
    
    recent = trace.recent_events()
    assert len(recent) == 500
    assert recent[0].message == "test 100"
    assert recent[-1].message == "test 599"


def test_subscribe_callback_receives_live_events():
    trace = TraceEmitter()
    received = []
    
    def callback(event):
        received.append(event)
    
    unsubscribe = trace.subscribe_callback(callback)
    
    trace.emit(component="Test", level=TraceLevel.INFO, message="test1")
    trace.emit(component="Test", level=TraceLevel.INFO, message="test2")
    
    assert len(received) == 2
    assert received[0].message == "test1"
    assert received[1].message == "test2"
    
    unsubscribe()
    trace.emit(component="Test", level=TraceLevel.INFO, message="test3")
    
    assert len(received) == 2


def test_faulty_callback_does_not_block_emit():
    trace = TraceEmitter()
    received = []
    
    def faulty_callback(event):
        raise Exception("test error")
    
    def good_callback(event):
        received.append(event)
    
    trace.subscribe_callback(faulty_callback)
    trace.subscribe_callback(good_callback)
    
    trace.emit(component="Test", level=TraceLevel.INFO, message="test")
    
    assert len(received) == 1
    assert received[0].message == "test"
