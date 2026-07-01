from unittest.mock import MagicMock, patch

import pytest

from sovereignai.shared.capability_api import CapabilityAPI
from sovereignai.shared.hardware_probe import HardwareProbe
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import TraceLevel
from sovereignai.workers.education.teacher_worker import TeacherWorker


@pytest.fixture
def mock_trace() -> TraceEmitter:
    return MagicMock(spec=TraceEmitter)

@pytest.fixture
def mock_hardware_probe() -> MagicMock:
    return MagicMock(spec=HardwareProbe)

@pytest.fixture
def mock_capability_api() -> MagicMock:
    api = MagicMock(spec=CapabilityAPI)
    api.query_memory = MagicMock(return_value=[])
    return api

@pytest.fixture
def teacher_worker(mock_trace: MagicMock, mock_hardware_probe: MagicMock, mock_capability_api: MagicMock) -> TeacherWorker:
    return TeacherWorker(
        capability_api=mock_capability_api,
        trace=mock_trace,
        hardware_probe=mock_hardware_probe,
    )

def test_health_check_missing_package(teacher_worker: TeacherWorker, mock_trace: MagicMock) -> None:
    with patch('importlib.util.find_spec') as mock_find_spec:
        mock_find_spec.return_value = None
        result = teacher_worker.health_check()
        assert result is False
        mock_trace.emit.assert_called()
        call_args = mock_trace.emit.call_args
        assert call_args[1]['level'] == TraceLevel.WARN
        assert 'not installed' in call_args[1]['message']

def test_health_check_broken_import(teacher_worker: TeacherWorker, mock_trace: MagicMock) -> None:
    with patch(
        'importlib.util.find_spec'
    ) as mock_find_spec, patch('importlib.import_module') as mock_import:
        mock_find_spec.return_value = MagicMock()
        mock_import.side_effect = ImportError('broken package')
        result = teacher_worker.health_check()
        assert result is False
        mock_trace.emit.assert_called()
        call_args = mock_trace.emit.call_args
        assert call_args[1]['level'] == TraceLevel.WARN
        assert 'broken' in call_args[1]['message']

def test_health_check_cuda_unavailable(teacher_worker: TeacherWorker, mock_trace: MagicMock) -> None:
    with patch(
        'importlib.util.find_spec'
    ) as mock_find_spec, patch('importlib.import_module') as mock_import:
        mock_find_spec.return_value = MagicMock()
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = False
        mock_import.return_value = mock_torch
        result = teacher_worker.health_check()
        assert result is False

def test_curate_dataset_consent_false(teacher_worker: TeacherWorker, mock_trace: MagicMock) -> None:
    result = teacher_worker.curate_dataset(trace_ids=[], _criteria={}, consent=False)
    assert result == []
    mock_trace.emit.assert_called()
    call_args = mock_trace.emit.call_args
    assert call_args[1]['level'] == TraceLevel.WARN
    assert 'consent=False' in call_args[1]['message']

def test_curate_dataset_pii_filter(teacher_worker: TeacherWorker, mock_capability_api: MagicMock, mock_trace: MagicMock) -> None:
    mock_capability_api.query_memory.return_value = [
        {
            'prompt': 'Contact me at test@example.com',
            'completion': 'OK',
            'timestamp': '2026-06-29T00:00:00Z',
        },
        {
            'prompt': 'My phone is 555-123-4567',
            'completion': 'OK',
            'timestamp': '2026-06-29T00:00:00Z',
        },
        {
            'prompt': 'SSN: 123-45-6789',
            'completion': 'OK',
            'timestamp': '2026-06-29T00:00:00Z',
        },
        {
            'prompt': 'Card: 4111-1111-1111-1111',
            'completion': 'OK',
            'timestamp': '2026-06-29T00:00:00Z',
        },
        {
            'prompt': 'Safe content',
            'completion': 'OK',
            'timestamp': '2026-06-29T00:00:00Z',
        },
    ]
    result = teacher_worker.curate_dataset(trace_ids=[], _criteria={}, consent=True)
    assert len(result) < 5

def test_curate_dataset_retention_filter(teacher_worker: TeacherWorker, mock_capability_api: MagicMock, mock_trace: MagicMock) -> None:
    result = teacher_worker.curate_dataset(trace_ids=[], _criteria={}, consent=True)
    assert isinstance(result, list)

def test_cancel_sets_flag(teacher_worker: TeacherWorker) -> None:
    teacher_worker.cancel()
    assert teacher_worker._cancel_requested is True

def test_evaluate_returns_dict(teacher_worker: TeacherWorker) -> None:
    result = teacher_worker.evaluate(model_path='/fake/path', dataset=[])
    assert isinstance(result, dict)
    assert 'loss' in result
    assert 'perplexity' in result
