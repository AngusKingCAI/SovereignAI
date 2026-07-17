from hypothesis import HealthCheck, Phase, given, settings
from hypothesis import strategies as st

from sovereignai.shared.task_state_machine import _VALID_TRANSITIONS
from sovereignai.shared.types import TaskState, TraceLevel


def can_transition(from_state: TaskState, to_state: TaskState) -> bool:
    return to_state in _VALID_TRANSITIONS.get(from_state, [])

class TestStateMachineProperties:

    @given(st.sampled_from(TaskState), st.sampled_from(TaskState))
    @settings(  # noqa: E501
        suppress_health_check=[HealthCheck.differing_executors],
        max_examples=10,
        phases=[Phase.generate]
    )
    def test_all_transitions_are_valid(self, from_state, to_state):
        expected = to_state in _VALID_TRANSITIONS.get(from_state, [])
        assert can_transition(from_state, to_state) == expected

    @given(st.lists(st.sampled_from(TraceLevel)))
    @settings(  # noqa: E501
        suppress_health_check=[HealthCheck.differing_executors],
        max_examples=10,
        phases=[Phase.generate]
    )
    def test_trace_filtering_never_crashes(self, levels):
        if not levels:
            return
        from sovereignai.shared.trace_emitter import TraceEmitter
        trace_emitter = TraceEmitter()
        for level in levels:
            trace_emitter.emit(component='test', level=level, message='test message')
        events = trace_emitter.get_events(level=level)
        assert isinstance(events, list)
