import json
import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from sovereignai.shared.capability_api import CapabilityAPI
from sovereignai.shared.hardware_probe import HardwareProbe
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.workers.education.teacher_worker import TeacherWorker


@pytest.fixture
def mock_trace():
    return MagicMock(spec=TraceEmitter)

@pytest.fixture
def mock_hardware_probe():
    return MagicMock(spec=HardwareProbe)

@pytest.fixture
def mock_capability_api():
    return MagicMock(spec=CapabilityAPI)

@pytest.fixture
def teacher_worker(mock_trace, mock_hardware_probe, mock_capability_api):
    return TeacherWorker(capability_api=mock_capability_api, trace=mock_trace, hardware_probe=mock_hardware_probe)

@pytest.mark.skip(reason='Windows os.replace permission issues in test environment')
def test_register_model_creates_registry(teacher_worker):
    with tempfile.TemporaryDirectory() as tmpdir:
        registry_path = os.path.join(tmpdir, 'model_registry.json')

        def mock_replace(src, dst):
            import shutil
            shutil.copy2(src, dst)
            os.remove(src)
        with patch('sovereignai.workers.education.teacher_worker.os.path.expanduser', return_value=tmpdir), patch('sovereignai.workers.education.teacher_worker.os.replace', side_effect=mock_replace):
            teacher_worker._register_model(name='test-model', path='/fake/path', dataset=[{'prompt': 'test'}])
            assert os.path.exists(registry_path)
            with open(registry_path) as f:
                registry = json.load(f)
            assert 'test-model' in registry
            assert registry['test-model']['path'] == '/fake/path'
            assert registry['test-model']['dataset_size'] == 1

@pytest.mark.skip(reason='Windows os.replace permission issues in test environment')
def test_register_model_atomic_write(teacher_worker):
    with tempfile.TemporaryDirectory() as tmpdir:
        registry_path = os.path.join(tmpdir, 'model_registry.json')

        def mock_replace(src, dst):
            import shutil
            shutil.copy2(src, dst)
            os.remove(src)
        with patch('sovereignai.workers.education.teacher_worker.os.path.expanduser', return_value=tmpdir), patch('sovereignai.workers.education.teacher_worker.os.replace', side_effect=mock_replace):
            teacher_worker._register_model(name='test-model', path='/fake/path', dataset=[{'prompt': 'test'}])
            assert not os.path.exists(registry_path + '.tmp')
            assert os.path.exists(registry_path)

@pytest.mark.skip(reason='Windows os.replace permission issues in test environment')
def test_register_model_updates_existing_registry(teacher_worker):
    with tempfile.TemporaryDirectory() as tmpdir:
        registry_path = os.path.join(tmpdir, 'model_registry.json')
        initial_registry = {'existing-model': {'path': '/old/path', 'dataset_size': 5}}
        with open(registry_path, 'w') as f:
            json.dump(initial_registry, f)

        def mock_replace(src, dst):
            import shutil
            shutil.copy2(src, dst)
            os.remove(src)
        with patch('sovereignai.workers.education.teacher_worker.os.path.expanduser', side_effect=lambda x: tmpdir if '~/.sovereignai' in x else x), patch('sovereignai.workers.education.teacher_worker.os.replace', side_effect=mock_replace):
            teacher_worker._register_model(name='new-model', path='/new/path', dataset=[{'prompt': 'test'}])
            with open(registry_path) as f:
                registry = json.load(f)
            assert 'existing-model' in registry
            assert 'new-model' in registry
            assert registry['existing-model']['path'] == '/old/path'
            assert registry['new-model']['path'] == '/new/path'

def test_enforce_model_size_limit_evicts_oldest(teacher_worker):
    with tempfile.TemporaryDirectory() as tmpdir:
        models_dir = os.path.join(tmpdir, 'models')
        os.makedirs(models_dir)
        old_model = os.path.join(models_dir, 'old-model')
        new_model = os.path.join(models_dir, 'new-model')
        os.makedirs(old_model)
        os.makedirs(new_model)
        with open(os.path.join(old_model, 'weights.bin'), 'w') as f:
            f.write('x' * 1024)
        with open(os.path.join(new_model, 'weights.bin'), 'w') as f:
            f.write('x' * 1024)
        import time
        time.sleep(0.1)
        os.utime(old_model, (time.time() - 100, time.time() - 100))

        def mock_walk(path):
            if path == models_dir:
                for model_dir in [old_model, new_model]:
                    yield (model_dir, [], ['weights.bin'])

        def mock_getsize(path):
            return 60 * 1024 * 1024 * 1024
        with patch('sovereignai.workers.education.teacher_worker.os.path.expanduser', return_value=tmpdir), patch('sovereignai.workers.education.teacher_worker.os.walk', side_effect=mock_walk), patch('sovereignai.workers.education.teacher_worker.os.path.getsize', side_effect=mock_getsize):
            teacher_worker._enforce_model_size_limit()
        assert not os.path.exists(old_model)

def test_enforce_model_size_limit_no_op_when_under_limit(teacher_worker):
    with tempfile.TemporaryDirectory() as tmpdir:
        models_dir = os.path.join(tmpdir, 'models')
        os.makedirs(models_dir)
        small_model = os.path.join(models_dir, 'small-model')
        os.makedirs(small_model)
        with open(os.path.join(small_model, 'weights.bin'), 'w') as f:
            f.write('x' * 1024)
        with patch('sovereignai.workers.education.teacher_worker.os.path.expanduser', return_value=tmpdir):
            teacher_worker._enforce_model_size_limit()
        assert os.path.exists(small_model)

def test_enforce_model_size_limit_handles_missing_dir(teacher_worker):
    with tempfile.TemporaryDirectory() as tmpdir, patch('sovereignai.workers.education.teacher_worker.os.path.expanduser', return_value=tmpdir):
        teacher_worker._enforce_model_size_limit()
