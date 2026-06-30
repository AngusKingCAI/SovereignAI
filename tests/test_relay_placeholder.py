from __future__ import annotations

import contextlib

import pytest

from sovereignai.shared.relay_placeholder import RelayPlaceholder
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import RelayNotSupportedError, TraceLevel


@pytest.fixture
def relay() -> RelayPlaceholder:
    trace = TraceEmitter()
    return RelayPlaceholder(trace=trace)

def test_attempt_connection_raises_relay_not_supported_error(relay: RelayPlaceholder) -> None:
    with pytest.raises(RelayNotSupportedError):
        relay.attempt_connection('phone_app')

def test_attempt_connection_emits_trace(relay: RelayPlaceholder) -> None:
    with contextlib.suppress(RelayNotSupportedError):
        relay.attempt_connection('phone_app')
    events = relay._trace.get_events(component='RelayPlaceholder', level=TraceLevel.WARN)
    assert len(events) > 0
    assert "Connection attempt from 'phone_app'" in events[0].message

def test_placeholder_does_not_open_socket(relay: RelayPlaceholder) -> None:
    import sovereignai.shared.relay_placeholder as relay_module
    assert 'socket' not in dir(relay_module)
    assert not hasattr(relay, '_socket')
    assert not hasattr(relay, '_server')
