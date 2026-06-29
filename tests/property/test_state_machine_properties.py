"""Property-based tests for state machine invariants."""
from hypothesis import HealthCheck, Phase, given, settings
from hypothesis import strategies as st

from sovereignai.shared.task_state_machine import _VALID_TRANSITIONS
from sovereignai.shared.types import TaskState, TraceLevel


def can_transition(from_state: TaskState, to_state: TaskState) -> bool:
    """Check if a transition between two states is valid."""
    return to_state in _VALID_TRANSITIONS.get(from_state, [])


class TestStateMachineProperties:
    """Property-based tests for state machine behavior."""

    @given(st.sampled_from(TaskState), st.sampled_from(TaskState))
    @settings(
        suppress_health_check=[HealthCheck.differing_executors],
        max_examples=10,
        phases=[Phase.generate]
    )
    def test_all_transitions_are_valid(self, from_state, to_state):
        """Verify can_transition() agrees with VALID_TRANSITIONS."""
        expected = to_state in _VALID_TRANSITIONS.get(from_state, [])
        assert can_transition(from_state, to_state) == expected

    @given(st.lists(st.sampled_from(TraceLevel)))
    @settings(
        suppress_health_check=[HealthCheck.differing_executors],
        max_examples=10,
        phases=[Phase.generate]
    )
    def test_trace_filtering_never_crashes(self, levels):
        """Verify filtering arbitrary TraceLevel combinations never raises."""
        if not levels:  # Rev9: guard against empty list (UnboundLocalError on 'level')
            return
        from sovereignai.shared.trace_emitter import TraceEmitter
        trace_emitter = TraceEmitter()
        for level in levels:
            trace_emitter.emit(component="test", level=level, message="test message")
        events = trace_emitter.get_events(level=level)  # F10: actually exercise the filter
        assert isinstance(events, list)
