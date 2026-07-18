from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from sovereignai.librarian.librarian import Librarian
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import (
    TASK_STATE_CHANNEL,
    TaskState,
    TaskStateChanged,
    TraceLevel,
    now_utc,
)
from sovereignai.skills.official.self_correction.skill import SelfCorrectionSkill


@pytest.fixture
def mock_librarian():
    return MagicMock(spec=Librarian)

@pytest.fixture
def mock_trace():
    return MagicMock(spec=TraceEmitter)

@pytest.fixture
def self_correction_skill(mock_librarian, mock_trace):
    return SelfCorrectionSkill(librarian=mock_librarian, trace=mock_trace)

def test_on_task_state_changed_filters_own_events(self_correction_skill, mock_trace):  # noqa: E501
    event = TaskStateChanged(  # noqa: E501
        channel=TASK_STATE_CHANNEL,
        correlation_id=uuid4(),
        timestamp=now_utc(),
        task_id='test-123',
        old_state=TaskState.EXECUTING,
        new_state=TaskState.COMPLETE
    )
    self_correction_skill.on_task_state_changed(event)

def test_on_task_state_changed_emits_debug_on_duplicate(self_correction_skill, mock_trace):  # noqa: E501
    event = TaskStateChanged(  # noqa: E501
        channel=TASK_STATE_CHANNEL,
        correlation_id=uuid4(),
        timestamp=now_utc(),
        task_id='test-123',
        old_state=TaskState.EXECUTING,
        new_state=TaskState.COMPLETE
    )
    with patch.object(self_correction_skill, 'analyze_task') as mock_analyze:
        self_correction_skill.on_task_state_changed(event)
        mock_analyze.assert_called_once()
    with patch.object(self_correction_skill, 'analyze_task') as mock_analyze:
        self_correction_skill.on_task_state_changed(event)
        mock_analyze.assert_called_once()

def test_analyze_task_filters_self_correction_emissions(self_correction_skill, mock_librarian):  # noqa: E501
    mock_librarian.query.return_value = [  # noqa: E501
        {'component': 'worker', 'message': 'test'},
        {'component': 'self_correction', 'message': 'should be filtered'}
    ]
    result = self_correction_skill.analyze_task('test-123')
    assert isinstance(result, dict)
    assert 'patterns_found' in result

def test_update_procedural_memory_lock_timeout(self_correction_skill, mock_librarian, mock_trace):
    mock_librarian.store.side_effect = Exception('Lock timeout')
    result = self_correction_skill.update_procedural_memory({'type': 'test'}, confidence=0.8)
    assert result is False
    mock_trace.emit.assert_called()
    call_args = mock_trace.emit.call_args
    assert call_args[1]['level'] == TraceLevel.WARN
    assert 'Failed to update procedural memory' in call_args[1]['message']

def test_update_procedural_memory_success(self_correction_skill, mock_librarian):
    mock_librarian.store.return_value = 'record-123'
    result = self_correction_skill.update_procedural_memory({'type': 'test'}, confidence=0.8)
    assert result is True

def test_recommend_retraining_emits_trace(self_correction_skill, mock_trace):
    pattern = {'type': 'routing_failure', 'confidence': 0.9}
    self_correction_skill._recommend_retraining(pattern)
    mock_trace.emit.assert_called()
    call_args = mock_trace.emit.call_args
    assert call_args[1]['level'] == TraceLevel.INFO
    assert 'Retraining recommended' in call_args[1]['message']

def test_on_task_state_changed_ignores_non_terminal_states(self_correction_skill):  # noqa: E501
    event = TaskStateChanged(  # noqa: E501
        channel=TASK_STATE_CHANNEL,
        correlation_id=uuid4(),
        timestamp=now_utc(),
        task_id='test-123',
        old_state=TaskState.RECEIVED,
        new_state=TaskState.QUEUED
    )
    with patch.object(self_correction_skill, 'analyze_task') as mock_analyze:
        self_correction_skill.on_task_state_changed(event)
        mock_analyze.assert_not_called()
