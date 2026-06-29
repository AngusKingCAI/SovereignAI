"""End-to-end tests for Education department integration."""
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from sovereignai.librarian.librarian import Librarian
from sovereignai.shared.capability_api import CapabilityAPI
from sovereignai.shared.hardware_probe import HardwareProbe
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import TASK_STATE_CHANNEL, TaskState, TaskStateChanged, now_utc
from sovereignai.skills.official.self_correction.skill import SelfCorrectionSkill
from sovereignai.workers.education.teacher_worker import TeacherWorker


@pytest.fixture
def mock_trace():
    """Create a mock TraceEmitter."""
    return MagicMock(spec=TraceEmitter)


@pytest.fixture
def mock_hardware_probe():
    """Create a mock HardwareProbe."""
    return MagicMock(spec=HardwareProbe)


@pytest.fixture
def mock_capability_api():
    """Create a mock CapabilityAPI."""
    return MagicMock(spec=CapabilityAPI)


@pytest.fixture
def mock_librarian():
    """Create a mock Librarian."""
    return MagicMock(spec=Librarian)


def test_education_department_integration(
    mock_trace, mock_hardware_probe, mock_capability_api, mock_librarian,
):
    """Test end-to-end Education department integration."""
    # Create Teacher worker
    teacher = TeacherWorker(
        capability_api=mock_capability_api,
        trace=mock_trace,
        hardware_probe=mock_hardware_probe,
    )

    # Create Self-correction skill
    self_correction = SelfCorrectionSkill(
        librarian=mock_librarian,
        trace=mock_trace,
    )

    # Verify components are instantiated
    assert teacher is not None
    assert self_correction is not None

    # Verify Teacher worker has required methods
    assert hasattr(teacher, 'health_check')
    assert hasattr(teacher, 'finetune')
    assert hasattr(teacher, 'evaluate')
    assert hasattr(teacher, 'curate_dataset')

    # Verify Self-correction skill has required methods
    assert hasattr(self_correction, 'on_task_state_changed')
    assert hasattr(self_correction, 'analyze_task')
    assert hasattr(self_correction, 'update_procedural_memory')


def test_teacher_worker_health_check_graceful_degradation(
    mock_trace, mock_hardware_probe, mock_capability_api,
):
    """Test Teacher worker gracefully degrades when dependencies are unavailable."""
    teacher = TeacherWorker(
        capability_api=mock_capability_api,
        trace=mock_trace,
        hardware_probe=mock_hardware_probe,
    )

    # Mock health_check to return False (dependencies missing)
    with patch('importlib.util.find_spec', return_value=None):
        result = teacher.health_check()
        assert result is False
        mock_trace.emit.assert_called()


def test_self_correction_subscribes_to_events(mock_librarian, mock_trace):
    """Test Self-correction skill can subscribe to TaskStateChanged events."""
    self_correction = SelfCorrectionSkill(
        librarian=mock_librarian,
        trace=mock_trace,
    )

    event = TaskStateChanged(
        channel=TASK_STATE_CHANNEL,
        correlation_id=uuid4(),
        timestamp=now_utc(),
        task_id="test-123",
        old_state=TaskState.EXECUTING,
        new_state=TaskState.COMPLETE,
    )

    # Should not raise an exception
    self_correction.on_task_state_changed(event)
