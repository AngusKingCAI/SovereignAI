"""Tests for QLoRA integration — GPU lock, fine-tuning logic, model registry."""
from unittest.mock import MagicMock, patch

import pytest

from sovereignai.shared.capability_api import CapabilityAPI
from sovereignai.shared.hardware_probe import HardwareProbe
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.workers.education.teacher_worker import _GPU_LOCK, TeacherWorker


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
def teacher_worker(mock_trace, mock_hardware_probe, mock_capability_api):
    """Create a Teacher worker instance."""
    return TeacherWorker(
        capability_api=mock_capability_api,
        trace=mock_trace,
        hardware_probe=mock_hardware_probe,
    )


@pytest.mark.skip(reason="transformers package not installed in test environment")
def test_gpu_lock_acquired_released(teacher_worker, mock_trace):
    """Test GPU lock is acquired and released during finetune (per N3)."""
    with patch('transformers.AutoModelForCausalLM'), \
         patch('transformers.AutoTokenizer'), \
         patch('peft.LoraConfig'), \
         patch('peft.get_peft_model'), \
         patch('peft.prepare_model_for_kbit_training'), \
         patch('transformers.BitsAndBytesConfig'), \
         patch('trl.SFTTrainer'), \
         patch('datasets.Dataset'), \
         patch('os.makedirs'), \
         patch('os.path.expanduser', return_value='/fake/path'), \
         patch.object(teacher_worker, '_enforce_model_size_limit'), \
         patch.object(teacher_worker, '_register_model'):

        # Acquire lock first to test timeout
        _GPU_LOCK.acquire()

        try:
            # This should timeout since lock is held
            with pytest.raises(RuntimeError, match="GPU lock timeout"):
                teacher_worker.finetune(
                    base_model="test-model",
                    dataset=[{"prompt": "test"}],
                    output_name="test-output"
                )
        finally:
            _GPU_LOCK.release()


def test_gpu_lock_in_process_scope_only(teacher_worker, mock_trace):
    """Test GPU lock is in-process only (per N3 — does not protect against Ollama)."""
    # This test documents the known limitation: the lock is threading.Lock,
    # which only protects against in-process consumers. Cross-process contention
    # (e.g., with Ollama) is NOT handled in v1.
    assert type(_GPU_LOCK).__name__.lower() == 'lock'
    # The lock is documented in DEBT.md as a known limitation


@pytest.mark.skip(reason="transformers package not installed in test environment")
def test_finetune_uses_expanduser(teacher_worker, mock_trace):
    """Test finetune uses os.path.expanduser for model path."""
    with patch('transformers.AutoModelForCausalLM'), \
         patch('transformers.AutoTokenizer'), \
         patch('peft.LoraConfig'), \
         patch('peft.get_peft_model'), \
         patch('peft.prepare_model_for_kbit_training'), \
         patch('transformers.BitsAndBytesConfig'), \
         patch('trl.SFTTrainer'), \
         patch('datasets.Dataset'), \
         patch('os.makedirs'), \
         patch('os.path.expanduser') as mock_expand, \
         patch.object(teacher_worker, '_enforce_model_size_limit'), \
         patch.object(teacher_worker, '_register_model'):

        mock_expand.return_value = '/expanded/path'
        teacher_worker.finetune(
            base_model="test-model",
            dataset=[{"prompt": "test"}],
            output_name="test-output"
        )
        mock_expand.assert_called_with('~/.sovereignai/models/test-output')


@pytest.mark.skip(reason="transformers package not installed in test environment")
def test_finetune_emits_progress_traces(teacher_worker, mock_trace):
    """Test finetune emits progress traces every 100 steps."""
    with patch('transformers.AutoModelForCausalLM'), \
         patch('transformers.AutoTokenizer'), \
         patch('peft.LoraConfig'), \
         patch('peft.get_peft_model'), \
         patch('peft.prepare_model_for_kbit_training'), \
         patch('transformers.BitsAndBytesConfig'), \
         patch('trl.SFTTrainer') as mock_trainer, \
         patch('datasets.Dataset'), \
         patch('os.makedirs'), \
         patch('os.path.expanduser', return_value='/fake/path'), \
         patch.object(teacher_worker, '_enforce_model_size_limit'), \
         patch.object(teacher_worker, '_register_model'):

        mock_trainer_instance = MagicMock()
        mock_trainer_instance.max_steps = 200
        mock_trainer_instance.train_step = MagicMock()
        mock_trainer.return_value = mock_trainer_instance

        teacher_worker.finetune(
            base_model="test-model",
            dataset=[{"prompt": "test"}],
            output_name="test-output"
        )

        # Check that progress traces were emitted
        progress_calls = [call for call in mock_trace.emit.call_args_list
                         if 'Training step' in str(call)]
        assert len(progress_calls) >= 1
