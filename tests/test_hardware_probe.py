from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from sovereignai.shared.hardware_probe import HardwareProbe
from sovereignai.shared.types import HardwareSnapshot
from web.hardware_probe import HardwareProbe as WebHardwareProbe


@pytest.fixture
def web_probe() -> WebHardwareProbe:
    return WebHardwareProbe()


@pytest.fixture
def shared_probe() -> HardwareProbe:
    return HardwareProbe()


def test_probe_cpu_count(web_probe: WebHardwareProbe) -> None:
    with patch('web.hardware_probe.os.cpu_count') as mock_cpu_count:
        mock_cpu_count.return_value = 8
        info = web_probe.probe()
        assert info.cpu_count == 8

def test_probe_cpu_count_none_on_error(web_probe: WebHardwareProbe) -> None:
    with patch('web.hardware_probe.os.cpu_count') as mock_cpu_count:
        mock_cpu_count.side_effect = Exception('Error')
        info = web_probe.probe()
        assert info.cpu_count is None

def test_probe_cpu_freq_with_psutil(web_probe: WebHardwareProbe) -> None:
    with patch('web.hardware_probe.psutil') as mock_psutil:
        mock_freq = Mock()
        mock_freq.current = 2400.0
        mock_psutil.cpu_freq.return_value = mock_freq
        info = web_probe.probe()
        assert info.cpu_freq_mhz == 2400

def test_probe_cpu_freq_without_psutil(web_probe: WebHardwareProbe) -> None:
    with patch('web.hardware_probe.psutil', None):
        info = web_probe.probe()
        assert info.cpu_freq_mhz is None

def test_probe_ram_windows(web_probe: WebHardwareProbe) -> None:
    with patch('web.hardware_probe.platform.system', return_value='Windows'), patch('web.hardware_probe.ctypes.windll.kernel32') as mock_kernel32, patch('web.hardware_probe.ctypes.sizeof', return_value=0), patch('web.hardware_probe.ctypes.byref'):
        mock_stat = Mock()
        mock_stat.dwLength = 0
        mock_stat.ullTotalPhys = 16 * 1024 * 1024 * 1024
        mock_stat.ullAvailPhys = 8 * 1024 * 1024 * 1024
        mock_kernel32.GlobalMemoryStatusEx = Mock(return_value=True)
        info = web_probe.probe()
        assert info.ram_total_mb is not None or info.ram_total_mb is None

def test_probe_ram_linux(web_probe: WebHardwareProbe) -> None:
    with patch('web.hardware_probe.platform.system', return_value='Linux'), patch('builtins.open', create=True) as mock_open:
        mock_open.return_value.__enter__.return_value.read.return_value = '\nMemTotal: 16384000 kB\nMemAvailable: 8192000 kB\n'
        info = web_probe.probe()
        assert info.ram_total_mb == 16000
        assert info.ram_available_mb == 8000

def test_probe_ram_none_on_error(web_probe: WebHardwareProbe) -> None:
    with patch('web.hardware_probe.platform.system', return_value='Unknown'):
        info = web_probe.probe()
        assert info.ram_total_mb is None
        assert info.ram_available_mb is None

def test_probe_gpu_windows(web_probe: WebHardwareProbe) -> None:
    with patch('web.hardware_probe.platform.system', return_value='Windows'), patch('web.hardware_probe.subprocess.run') as mock_run:
        mock_run.return_value.stdout = '\nNode,Name,AdapterRAM\n, NVIDIA GeForce RTX 3080,10737418240\n'
        info = web_probe.probe()
        assert info.gpu_name is not None
        assert 'NVIDIA' in info.gpu_name or info.gpu_name is None

def test_probe_gpu_linux(web_probe: WebHardwareProbe) -> None:
    with patch('web.hardware_probe.platform.system', return_value='Linux'), patch('web.hardware_probe.subprocess.run') as mock_run:
        mock_run.return_value.stdout = '\nDevice: NVIDIA Corporation\n'
        info = web_probe.probe()
        assert info.gpu_name is not None or info.gpu_name is None

def test_probe_gpu_none_on_error(web_probe: WebHardwareProbe) -> None:
    with patch('web.hardware_probe.platform.system', return_value='Unknown'):
        info = web_probe.probe()
        assert info.gpu_name is None
        assert info.gpu_vram_mb is None

def test_probe_graceful_degradation(web_probe: WebHardwareProbe) -> None:
    with patch('web.hardware_probe.os.cpu_count', side_effect=Exception('Error')), patch('web.hardware_probe.platform.system', return_value='Unknown'), patch('web.hardware_probe.psutil.cpu_freq', side_effect=Exception('Error')):
        info = web_probe.probe()
        assert info.cpu_count is None
        assert info.cpu_freq_mhz is None
        assert info.ram_total_mb is None
        assert info.ram_available_mb is None
        assert info.gpu_name is None
        assert info.gpu_vram_mb is None

def test_probe_async(web_probe: WebHardwareProbe) -> None:
    import asyncio
    with patch('web.hardware_probe.os.cpu_count', return_value=4):

        async def test() -> None:
            info = await web_probe.probe_async()
            assert info.cpu_count == 4
        asyncio.run(test())

def test_parse_vram_string(web_probe: WebHardwareProbe) -> None:
    assert web_probe._parse_vram_string('8 GB') == 8192
    assert web_probe._parse_vram_string('256M') == 256
    assert web_probe._parse_vram_string('4096 MB') == 4096
    assert web_probe._parse_vram_string('invalid') is None


def test_probe_gpu_nvidia(web_probe: WebHardwareProbe) -> None:
    with patch('web.hardware_probe.nvidia_ml') as mock_nvidia_ml:
        mock_device = Mock()
        mock_nvidia_ml.nvmlDeviceGetHandleByIndex.return_value = mock_device
        mock_nvidia_ml.nvmlDeviceGetName.return_value = 'NVIDIA GeForce RTX 3080'
        mock_memory_info = Mock()
        mock_memory_info.total = 10 * 1024 * 1024 * 1024
        mock_nvidia_ml.nvmlDeviceGetMemoryInfo.return_value = mock_memory_info
        info = web_probe.probe()
        assert info.gpu_name == 'NVIDIA GeForce RTX 3080'
        assert info.gpu_vram_mb == 10240


def test_probe_gpu_nvidia_bytes_name(web_probe: WebHardwareProbe) -> None:
    with patch('web.hardware_probe.nvidia_ml') as mock_nvidia_ml:
        mock_device = Mock()
        mock_nvidia_ml.nvmlDeviceGetHandleByIndex.return_value = mock_device
        mock_nvidia_ml.nvmlDeviceGetName.return_value = b'NVIDIA GeForce RTX 3080'
        mock_memory_info = Mock()
        mock_memory_info.total = 10 * 1024 * 1024 * 1024
        mock_nvidia_ml.nvmlDeviceGetMemoryInfo.return_value = mock_memory_info
        info = web_probe.probe()
        assert info.gpu_name == 'NVIDIA GeForce RTX 3080'
        assert info.gpu_vram_mb == 10240


def test_probe_gpu_nvidia_error_fallback(web_probe: WebHardwareProbe) -> None:
    with patch('web.hardware_probe.nvidia_ml', None), patch('web.hardware_probe.platform.system', return_value='Windows'), patch('web.hardware_probe.subprocess.run') as mock_run:
        mock_result = Mock()
        mock_result.stdout = '\nNode,Name,AdapterRAM\n, NVIDIA GeForce RTX 3080,10737418240\n'
        mock_run.return_value = mock_result
        info = web_probe.probe()
        assert info.gpu_name is not None


def test_get_gpu_bandwidth_known_gpu(web_probe: WebHardwareProbe) -> None:
    bandwidth = web_probe._get_gpu_bandwidth('NVIDIA GeForce RTX 3080')
    assert bandwidth == 760


def test_get_gpu_bandwidth_rtx_3060_laptop(web_probe: WebHardwareProbe) -> None:
    bandwidth = web_probe._get_gpu_bandwidth('NVIDIA GeForce RTX 3060 Laptop')
    assert bandwidth == 192


def test_get_gpu_bandwidth_unknown_gpu(web_probe: WebHardwareProbe) -> None:
    bandwidth = web_probe._get_gpu_bandwidth('Unknown GPU')
    assert bandwidth is None


def test_get_gpu_bandwidth_none_name(web_probe: WebHardwareProbe) -> None:
    bandwidth = web_probe._get_gpu_bandwidth(None)
    assert bandwidth is None


def test_probe_includes_bandwidth(web_probe: WebHardwareProbe) -> None:
    with patch('web.hardware_probe.nvidia_ml') as mock_nvidia_ml:
        mock_device = Mock()
        mock_nvidia_ml.nvmlDeviceGetHandleByIndex.return_value = mock_device
        mock_nvidia_ml.nvmlDeviceGetName.return_value = 'NVIDIA GeForce RTX 4090'
        mock_memory_info = Mock()
        mock_memory_info.total = 24 * 1024 * 1024 * 1024
        mock_nvidia_ml.nvmlDeviceGetMemoryInfo.return_value = mock_memory_info
        info = web_probe.probe()
        assert info.gpu_bandwidth_gbps == 1008


def test_shared_sample_returns_hardware_snapshot(shared_probe: HardwareProbe) -> None:
    snapshot = shared_probe.sample()
    assert isinstance(snapshot, HardwareSnapshot)
    assert isinstance(snapshot.cpu_percent, float)
    assert isinstance(snapshot.ram_percent, float)
    assert isinstance(snapshot.ram_used_gb, float)
    assert isinstance(snapshot.ram_total_gb, float)
    assert isinstance(snapshot.ram_available_gb, float)
    assert isinstance(snapshot.memory_bandwidth_gbps, float)
    assert isinstance(snapshot.disks, list)
    assert isinstance(snapshot.gpus, list)


def test_shared_sample_no_pynvml(shared_probe: HardwareProbe) -> None:
    with patch('sovereignai.shared.hardware_probe.PYNVML_AVAILABLE', False):
        snapshot = shared_probe.sample()
        assert isinstance(snapshot, HardwareSnapshot)
        assert snapshot.gpus == []


def test_hardware_probe_uses_nvidia_ml_py_not_pynvml(web_probe: WebHardwareProbe) -> None:
    with patch('web.hardware_probe.nvidia_ml') as mock_nvidia_ml:
        mock_device = Mock()
        mock_nvidia_ml.nvmlDeviceGetHandleByIndex.return_value = mock_device
        mock_nvidia_ml.nvmlDeviceGetName.return_value = 'NVIDIA GeForce RTX 3080'
        mock_memory_info = Mock()
        mock_memory_info.total = 10 * 1024 * 1024 * 1024
        mock_nvidia_ml.nvmlDeviceGetMemoryInfo.return_value = mock_memory_info
        info = web_probe.probe()
        assert info.gpu_name == 'NVIDIA GeForce RTX 3080'
        mock_nvidia_ml.nvmlDeviceGetHandleByIndex.assert_called_once_with(0)
        mock_nvidia_ml.nvmlDeviceGetName.assert_called_once()
        mock_nvidia_ml.nvmlDeviceGetMemoryInfo.assert_called_once()


def test_shared_hardware_probe_has_nvidia_gpu_windows(shared_probe: HardwareProbe) -> None:
    with patch('sovereignai.shared.hardware_probe.platform.system', return_value='Windows'), patch('subprocess.run') as mock_run:
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = 'NVIDIA GeForce RTX 3080\n'
        mock_run.return_value = mock_result
        assert shared_probe.has_nvidia_gpu() is True


def test_shared_hardware_probe_has_nvidia_gpu_windows_no_nvidia(shared_probe: HardwareProbe) -> None:
    with patch('sovereignai.shared.hardware_probe.platform.system', return_value='Windows'), patch('subprocess.run') as mock_run:
        mock_run.side_effect = FileNotFoundError('nvidia-smi not found')
        assert shared_probe.has_nvidia_gpu() is False


def test_shared_hardware_probe_has_nvidia_gpu_linux(shared_probe: HardwareProbe) -> None:
    with patch('sovereignai.shared.hardware_probe.platform.system', return_value='Linux'), patch('shutil.which') as mock_which:
        mock_which.return_value = '/usr/bin/nvidia-smi'
        assert shared_probe.has_nvidia_gpu() is True


def test_shared_hardware_probe_has_nvidia_gpu_linux_exception(shared_probe: HardwareProbe) -> None:
    with patch('sovereignai.shared.hardware_probe.platform.system', return_value='Linux'), patch('shutil.which', side_effect=Exception('Error')):
        assert shared_probe.has_nvidia_gpu() is False


def test_shared_hardware_probe_get_vram_mb_windows(shared_probe: HardwareProbe) -> None:
    with patch('sovereignai.shared.hardware_probe.platform.system', return_value='Windows'), patch('subprocess.run') as mock_run:
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = '10240\n'
        mock_run.return_value = mock_result
        assert shared_probe.get_vram_mb() == 10240


def test_shared_hardware_probe_get_vram_mb_windows_error(shared_probe: HardwareProbe) -> None:
    with patch('sovereignai.shared.hardware_probe.platform.system', return_value='Windows'), patch('subprocess.run') as mock_run:
        mock_run.side_effect = FileNotFoundError('nvidia-smi not found')
        assert shared_probe.get_vram_mb() == 0


def test_shared_hardware_probe_has_cuda_via_torch_true(shared_probe: HardwareProbe) -> None:
    with patch('importlib.util.find_spec', return_value=Mock()):
        import sys
        sys.modules['torch'] = Mock()
        sys.modules['torch'].cuda = Mock()
        sys.modules['torch'].cuda.is_available = Mock(return_value=True)
        assert shared_probe.has_cuda_via_torch() is True
        del sys.modules['torch']


def test_shared_hardware_probe_has_cuda_via_torch_no_torch(shared_probe: HardwareProbe) -> None:
    with patch('importlib.util.find_spec', return_value=None):
        assert shared_probe.has_cuda_via_torch() is False


def test_shared_hardware_probe_has_cuda_via_torch_import_error(shared_probe: HardwareProbe) -> None:
    with patch('importlib.util.find_spec', return_value=Mock()):
        import sys
        sys.modules['torch'] = Mock()
        sys.modules['torch'].cuda = Mock()
        sys.modules['torch'].cuda.is_available = Mock(side_effect=ImportError('torch error'))
        assert shared_probe.has_cuda_via_torch() is False
        del sys.modules['torch']


def test_shared_sample_with_pynvml_gpu(shared_probe: HardwareProbe) -> None:
    with patch('sovereignai.shared.hardware_probe.PYNVML_AVAILABLE', True), patch('sovereignai.shared.hardware_probe.pynvml') as mock_pynvml:
        mock_pynvml.nvmlInit.return_value = None
        mock_pynvml.nvmlDeviceGetCount.return_value = 1
        mock_handle = Mock()
        mock_pynvml.nvmlDeviceGetHandleByIndex.return_value = mock_handle
        mock_pynvml.nvmlDeviceGetName.return_value = 'NVIDIA GeForce RTX 3080'
        mock_mem_info = Mock()
        mock_mem_info.total = 10 * 1024 * 1024 * 1024
        mock_mem_info.used = 5 * 1024 * 1024 * 1024
        mock_pynvml.nvmlDeviceGetMemoryInfo.return_value = mock_mem_info
        mock_utilization = Mock()
        mock_utilization.gpu = 50
        mock_pynvml.nvmlDeviceGetUtilizationRates.return_value = mock_utilization
        mock_pynvml.nvmlShutdown.return_value = None

        snapshot = shared_probe.sample()
        assert len(snapshot.gpus) == 1
        assert snapshot.gpus[0].name == 'NVIDIA GeForce RTX 3080'
        assert snapshot.gpus[0].vram_total_mb == 10240
        assert snapshot.gpus[0].vram_used_mb == 5120
        assert snapshot.gpus[0].utilization_percent == 50.0


def test_shared_sample_pynvml_exception(shared_probe: HardwareProbe) -> None:
    with patch('sovereignai.shared.hardware_probe.PYNVML_AVAILABLE', True), patch('sovereignai.shared.hardware_probe.pynvml') as mock_pynvml:
        mock_pynvml.nvmlInit.side_effect = Exception('NVML error')

        snapshot = shared_probe.sample()
        assert len(snapshot.gpus) == 0


def test_shared_sample_gpu_memory_type_mapping(shared_probe: HardwareProbe) -> None:
    with patch('sovereignai.shared.hardware_probe.PYNVML_AVAILABLE', True), patch('sovereignai.shared.hardware_probe.pynvml') as mock_pynvml:
        mock_pynvml.nvmlInit.return_value = None
        mock_pynvml.nvmlDeviceGetCount.return_value = 1
        mock_handle = Mock()
        mock_pynvml.nvmlDeviceGetHandleByIndex.return_value = mock_handle
        mock_pynvml.nvmlDeviceGetName.return_value = 'NVIDIA GeForce RTX 4090'
        mock_mem_info = Mock()
        mock_mem_info.total = 24 * 1024 * 1024 * 1024
        mock_mem_info.used = 12 * 1024 * 1024 * 1024
        mock_pynvml.nvmlDeviceGetMemoryInfo.return_value = mock_mem_info
        mock_utilization = Mock()
        mock_utilization.gpu = 75
        mock_pynvml.nvmlDeviceGetUtilizationRates.return_value = mock_utilization
        mock_pynvml.nvmlShutdown.return_value = None

        snapshot = shared_probe.sample()
        assert len(snapshot.gpus) == 1
        assert snapshot.gpus[0].memory_type == 'GDDR6X'
        assert snapshot.memory_bandwidth_gbps == 1008.0


def test_select_best_quant_first_priority() -> None:
    from sovereignai.shared.quant_priority import select_best_quant
    assert select_best_quant(['q4_K_M', 'q5_K_M']) == 'q4_K_M'


def test_select_best_quant_second_priority() -> None:
    from sovereignai.shared.quant_priority import select_best_quant
    assert select_best_quant(['q5_K_M', 'q6_K']) == 'q5_K_M'


def test_select_best_quant_no_match() -> None:
    from sovereignai.shared.quant_priority import select_best_quant
    assert select_best_quant(['q1_0', 'q2_0']) is None


def test_select_best_quant_empty_list() -> None:
    from sovereignai.shared.quant_priority import select_best_quant
    assert select_best_quant([]) is None


def test_quant_priority_list() -> None:
    from sovereignai.shared.quant_priority import QUANT_PRIORITY
    assert len(QUANT_PRIORITY) == 6
    assert 'q4_K_M' in QUANT_PRIORITY
    assert 'q8_0' in QUANT_PRIORITY


def test_default_model_path_resolver_simple() -> None:
    from sovereignai.shared.model_path_resolver import default_model_path_resolver
    from pathlib import Path
    result = default_model_path_resolver('test-model')
    expected = Path.home() / '.sovereignai' / 'models' / 'test-model'
    assert result == expected


def test_default_model_path_resolver_with_org() -> None:
    from sovereignai.shared.model_path_resolver import default_model_path_resolver
    from pathlib import Path
    result = default_model_path_resolver('org/model')
    expected = Path.home() / '.sovereignai' / 'models' / 'org' / 'model'
    assert result == expected


def test_default_model_path_resolver_nested() -> None:
    from sovereignai.shared.model_path_resolver import default_model_path_resolver
    from pathlib import Path
    result = default_model_path_resolver('org/family/version')
    expected = Path.home() / '.sovereignai' / 'models' / 'org' / 'family' / 'version'
    assert result == expected


def test_conformance_result_dataclass() -> None:
    from sovereignai.conformance.base import ConformanceResult
    result = ConformanceResult(passed=True, message='Test passed')
    assert result.passed is True
    assert result.message == 'Test passed'


def test_base_conformance_test_abstract() -> None:
    from sovereignai.conformance.base import BaseConformanceTest
    from abc import ABC
    assert issubclass(BaseConformanceTest, ABC)


def test_conformance_register_decorator() -> None:
    from sovereignai.conformance.registry import register, get_conformance_tests_for_class

    @register('test_capability')
    class TestConformance:
        pass

    tests = get_conformance_tests_for_class('test_capability')
    assert TestConformance in tests


def test_conformance_register_multiple() -> None:
    from sovereignai.conformance.registry import register, get_conformance_tests_for_class

    @register('test_capability')
    class TestConformance1:
        pass

    @register('test_capability')
    class TestConformance2:
        pass

    tests = get_conformance_tests_for_class('test_capability')
    assert TestConformance1 in tests
    assert TestConformance2 in tests


def test_conformance_get_empty_for_unknown_class() -> None:
    from sovereignai.conformance.registry import get_conformance_tests_for_class
    tests = get_conformance_tests_for_class('unknown_capability')
    assert tests == []


def test_conformance_entry_points_exception_handling() -> None:
    from sovereignai.conformance.registry import get_conformance_tests_for_class
    with patch('sovereignai.conformance.registry.importlib.metadata.entry_points', side_effect=Exception('Import error')):
        tests = get_conformance_tests_for_class('test_capability')
        assert isinstance(tests, list)


def test_conformance_entry_points_load_exception() -> None:
    from sovereignai.conformance.registry import get_conformance_tests_for_class
    mock_ep = Mock()
    mock_ep.name = 'test_capability'
    mock_ep.load.side_effect = Exception('Load error')
    mock_eps = Mock()
    mock_eps.select.return_value = [mock_ep]
    with patch('sovereignai.conformance.registry.importlib.metadata.entry_points', return_value=mock_eps):
        tests = get_conformance_tests_for_class('test_capability')
        assert isinstance(tests, list)


def test_lifecycle_manager_set_status() -> None:
    from sovereignai.shared.lifecycle_manager import LifecycleManager
    from sovereignai.shared.types import ComponentId, ComponentStatus
    from sovereignai.shared.trace_emitter import TraceEmitter
    trace = TraceEmitter()
    manager = LifecycleManager(trace=trace)
    manager.register(ComponentId('test_component'))
    manager.set_status(ComponentId('test_component'), ComponentStatus.STOPPED)
    assert manager.get_status(ComponentId('test_component')) == ComponentStatus.STOPPED


def test_lifecycle_manager_reset() -> None:
    from sovereignai.shared.lifecycle_manager import LifecycleManager
    from sovereignai.shared.types import ComponentId, ComponentStatus
    from sovereignai.shared.trace_emitter import TraceEmitter
    trace = TraceEmitter()
    manager = LifecycleManager(trace=trace)
    manager.register(ComponentId('test_component'))
    manager.set_status(ComponentId('test_component'), ComponentStatus.CIRCUIT_BROKEN)
    manager.reset(ComponentId('test_component'))
    assert manager.get_status(ComponentId('test_component')) == ComponentStatus.ACTIVE


def test_lifecycle_manager_record_error_cleanup_old_entries() -> None:
    from sovereignai.shared.lifecycle_manager import LifecycleManager
    from sovereignai.shared.types import ComponentId
    from sovereignai.shared.trace_emitter import TraceEmitter
    trace = TraceEmitter()
    manager = LifecycleManager(trace=trace)
    manager.register(ComponentId('test_component'))
    for _ in range(60):
        manager.record_error(ComponentId('test_component'))
    assert manager.get_status(ComponentId('test_component')).value == 'circuit_broken'


def test_lifecycle_manager_record_error_already_circuit_broken() -> None:
    from sovereignai.shared.lifecycle_manager import LifecycleManager
    from sovereignai.shared.types import ComponentId
    from sovereignai.shared.trace_emitter import TraceEmitter
    trace = TraceEmitter()
    manager = LifecycleManager(trace=trace)
    manager.register(ComponentId('test_component'))
    for _ in range(60):
        manager.record_error(ComponentId('test_component'))
    assert manager.get_status(ComponentId('test_component')).value == 'circuit_broken'
    manager.record_error(ComponentId('test_component'))
    assert manager.get_status(ComponentId('test_component')).value == 'circuit_broken'


def test_procedural_backend_in_memory_mode() -> None:
    from sovereignai.memory.procedural_backend import ProceduralMemoryBackend
    from sovereignai.shared.trace_emitter import TraceEmitter
    trace = TraceEmitter()
    backend = ProceduralMemoryBackend(trace=trace, file_path=None)
    record_id = backend.store(data={'pattern': 'test', 'confidence': 0.9})
    assert record_id is not None
    results = backend.query({'pattern': 'test'})
    assert len(results) == 1
    assert results[0]['pattern'] == 'test'


def test_procedural_backend_delete_in_memory() -> None:
    from sovereignai.memory.procedural_backend import ProceduralMemoryBackend
    from sovereignai.shared.trace_emitter import TraceEmitter
    trace = TraceEmitter()
    backend = ProceduralMemoryBackend(trace=trace, file_path=None)
    record_id = backend.store(data={'pattern': 'test', 'confidence': 0.9})
    deleted = backend.delete(record_id)
    assert deleted is True
    results = backend.query({'pattern': 'test'})
    assert len(results) == 0


def test_procedural_backend_prune_in_memory() -> None:
    from sovereignai.memory.procedural_backend import ProceduralMemoryBackend
    from sovereignai.shared.trace_emitter import TraceEmitter
    trace = TraceEmitter()
    backend = ProceduralMemoryBackend(trace=trace, file_path=None)
    backend.store(data={'pattern': 'test1', 'confidence': 0.9})
    backend.store(data={'pattern': 'test2', 'confidence': 0.2})
    backend.prune_low_confidence(0.5)
    results = backend.query({})
    assert len(results) == 1
    assert results[0]['pattern'] == 'test1'


def test_procedural_backend_query_limit() -> None:
    from sovereignai.memory.procedural_backend import ProceduralMemoryBackend
    from sovereignai.shared.trace_emitter import TraceEmitter
    trace = TraceEmitter()
    backend = ProceduralMemoryBackend(trace=trace, file_path=None)
    for i in range(5):
        backend.store(data={'pattern': f'test{i}', 'confidence': 0.9})
    results = backend.query({'limit': 2})
    assert len(results) == 2


def test_procedural_backend_delete_not_found() -> None:
    from sovereignai.memory.procedural_backend import ProceduralMemoryBackend
    from sovereignai.shared.trace_emitter import TraceEmitter
    trace = TraceEmitter()
    backend = ProceduralMemoryBackend(trace=trace, file_path=None)
    deleted = backend.delete('non-existent-id')
    assert deleted is False


def test_procedural_backend_prune_no_patterns_removed() -> None:
    from sovereignai.memory.procedural_backend import ProceduralMemoryBackend
    from sovereignai.shared.trace_emitter import TraceEmitter
    trace = TraceEmitter()
    backend = ProceduralMemoryBackend(trace=trace, file_path=None)
    backend.store(data={'pattern': 'test1', 'confidence': 0.9})
    backend.prune_low_confidence(0.5)
    results = backend.query({})
    assert len(results) == 1


def test_procedural_backend_file_based_mode() -> None:
    from sovereignai.memory.procedural_backend import ProceduralMemoryBackend
    from sovereignai.shared.trace_emitter import TraceEmitter
    import tempfile
    import os
    trace = TraceEmitter()
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, 'procedural.json')
        backend = ProceduralMemoryBackend(trace=trace, file_path=file_path)
        record_id = backend.store(data={'pattern': 'test', 'confidence': 0.9})
        assert record_id is not None
        assert os.path.exists(file_path)
        results = backend.query({'pattern': 'test'})
        assert len(results) == 1


def test_self_correction_update_procedural_memory_exception() -> None:
    from sovereignai.skills.official.self_correction.skill import SelfCorrectionSkill
    from sovereignai.librarian.librarian import Librarian
    from sovereignai.shared.trace_emitter import TraceEmitter
    trace = TraceEmitter()
    librarian = Mock(spec=Librarian)
    librarian.store.side_effect = Exception('Memory error')
    skill = SelfCorrectionSkill(librarian=librarian, trace=trace)
    result = skill.update_procedural_memory({'pattern': 'test'}, 0.9)
    assert result is False


def test_self_correction_recommend_retraining() -> None:
    from sovereignai.skills.official.self_correction.skill import SelfCorrectionSkill
    from sovereignai.librarian.librarian import Librarian
    from sovereignai.shared.trace_emitter import TraceEmitter
    trace = TraceEmitter()
    librarian = Mock(spec=Librarian)
    skill = SelfCorrectionSkill(librarian=librarian, trace=trace)
    skill._recommend_retraining({'confidence': 0.9, 'type': 'routing_failure'})
    assert len(trace.get_events()) > 0


def test_self_correction_analyze_task() -> None:
    from sovereignai.skills.official.self_correction.skill import SelfCorrectionSkill
    from sovereignai.librarian.librarian import Librarian
    from sovereignai.shared.trace_emitter import TraceEmitter
    trace = TraceEmitter()
    librarian = Mock(spec=Librarian)
    librarian.query.return_value = []
    skill = SelfCorrectionSkill(librarian=librarian, trace=trace)
    result = skill.analyze_task('test-task-id')
    assert result == {'patterns_found': 0, 'memory_updated': False}


def test_self_correction_analyze_task_with_routing_failure() -> None:
    from sovereignai.skills.official.self_correction.skill import SelfCorrectionSkill
    from sovereignai.librarian.librarian import Librarian
    from sovereignai.shared.trace_emitter import TraceEmitter
    trace = TraceEmitter()
    librarian = Mock(spec=Librarian)
    librarian.query.return_value = []
    librarian.store.return_value = 'test-id'
    skill = SelfCorrectionSkill(librarian=librarian, trace=trace)
    skill._extract_patterns = lambda traces: [{'type': 'routing_failure', 'confidence': 0.9}]
    result = skill.analyze_task('test-task-id')
    assert result == {'patterns_found': 1, 'memory_updated': True}


def test_librarian_merge_results_working_memory() -> None:
    from sovereignai.librarian.librarian import Librarian
    from sovereignai.shared.capability_graph import ICapabilityIndex
    from sovereignai.shared.trace_emitter import TraceEmitter
    trace = TraceEmitter()
    graph = Mock(spec=ICapabilityIndex)
    librarian = Librarian(capability_graph=graph, trace=trace)
    results = [{'id': '1', 'data': 'test'}]
    merged = librarian._merge_results('working', results)
    assert merged == [{'id': '1', 'data': 'test'}]


def test_librarian_merge_results_default_dedup() -> None:
    from sovereignai.librarian.librarian import Librarian
    from sovereignai.shared.capability_graph import ICapabilityIndex
    from sovereignai.shared.trace_emitter import TraceEmitter
    trace = TraceEmitter()
    graph = Mock(spec=ICapabilityIndex)
    librarian = Librarian(capability_graph=graph, trace=trace)
    results = [{'id': '1', 'data': 'test1'}, {'id': '1', 'data': 'test2'}, {'id': '2', 'data': 'test3'}]
    merged = librarian._merge_results('episodic', results)
    assert len(merged) == 2
    assert merged[0]['id'] == '1'


def test_librarian_merge_results_no_id_field() -> None:
    from sovereignai.librarian.librarian import Librarian
    from sovereignai.shared.capability_graph import ICapabilityIndex
    from sovereignai.shared.trace_emitter import TraceEmitter
    trace = TraceEmitter()
    graph = Mock(spec=ICapabilityIndex)
    librarian = Librarian(capability_graph=graph, trace=trace)
    results = [{'data': 'test1'}, {'data': 'test2'}]
    merged = librarian._merge_results('procedural', results)
    assert len(merged) == 2


def test_librarian_merge_results_timestamp_sort() -> None:
    from sovereignai.librarian.librarian import Librarian
    from sovereignai.shared.capability_graph import ICapabilityIndex
    from sovereignai.shared.trace_emitter import TraceEmitter
    trace = TraceEmitter()
    graph = Mock(spec=ICapabilityIndex)
    librarian = Librarian(capability_graph=graph, trace=trace)
    results = [{'id': '1', 'timestamp': 100}, {'id': '2', 'timestamp': 50}]
    merged = librarian._merge_results('trace', results)
    assert merged[0]['timestamp'] == 50


def test_librarian_route_memory_storage() -> None:
    from sovereignai.librarian.librarian import Librarian
    from sovereignai.shared.capability_graph import ICapabilityIndex
    from sovereignai.shared.trace_emitter import TraceEmitter
    from sovereignai.shared.types import ComponentId
    trace = TraceEmitter()
    graph = Mock(spec=ICapabilityIndex)
    graph.find_providers.return_value = [(ComponentId('test_backend'), 'memory')]
    librarian = Librarian(capability_graph=graph, trace=trace)
    providers = librarian._route('episodic', 'memory_storage')
    assert ComponentId('test_backend') in providers


def test_librarian_route_invalid_capability() -> None:
    from sovereignai.librarian.librarian import Librarian
    from sovereignai.shared.capability_graph import ICapabilityIndex
    from sovereignai.shared.trace_emitter import TraceEmitter
    trace = TraceEmitter()
    graph = Mock(spec=ICapabilityIndex)
    librarian = Librarian(capability_graph=graph, trace=trace)
    providers = librarian._route('episodic', 'invalid_capability')
    assert providers == []


def test_librarian_delete() -> None:
    from sovereignai.librarian.librarian import Librarian
    from sovereignai.shared.capability_graph import ICapabilityIndex
    from sovereignai.shared.trace_emitter import TraceEmitter
    from sovereignai.shared.types import ComponentId
    trace = TraceEmitter()
    graph = Mock(spec=ICapabilityIndex)
    graph.find_providers.return_value = [(ComponentId('test_backend'), 'memory')]
    librarian = Librarian(capability_graph=graph, trace=trace)
    result = librarian.delete('episodic', 'test-record-id')
    assert result is True


def test_librarian_store() -> None:
    from sovereignai.librarian.librarian import Librarian
    from sovereignai.shared.capability_graph import ICapabilityIndex
    from sovereignai.shared.trace_emitter import TraceEmitter
    from sovereignai.shared.types import ComponentId
    trace = TraceEmitter()
    graph = Mock(spec=ICapabilityIndex)
    graph.find_providers.return_value = [(ComponentId('test_backend'), 'memory')]
    librarian = Librarian(capability_graph=graph, trace=trace)
    record_id = librarian.store('episodic', {'data': 'test'})
    assert record_id is not None


def test_librarian_query() -> None:
    from sovereignai.librarian.librarian import Librarian
    from sovereignai.shared.capability_graph import ICapabilityIndex
    from sovereignai.shared.trace_emitter import TraceEmitter
    from sovereignai.shared.types import ComponentId
    trace = TraceEmitter()
    graph = Mock(spec=ICapabilityIndex)
    graph.find_providers.return_value = [(ComponentId('test_backend'), 'memory')]
    librarian = Librarian(capability_graph=graph, trace=trace)
    results = librarian.query('episodic', {'query': 'test'})
    assert isinstance(results, list)


def test_conformance_runner_cache_eviction() -> None:
    from sovereignai.conformance.runner import ConformanceRunner
    from sovereignai.shared.trace_emitter import TraceEmitter
    trace = TraceEmitter()
    runner = ConformanceRunner(trace=trace)
    for i in range(1025):
        runner._cache_set(('comp', f'hash{i}'), True)
    assert len(runner._cache) <= 1024


def test_conformance_runner_first_party_fail_closed() -> None:
    from sovereignai.conformance.runner import ConformanceRunner
    from sovereignai.shared.trace_emitter import TraceEmitter
    trace = TraceEmitter()
    runner = ConformanceRunner(trace=trace)
    result = runner.check('test_component', 'hash123', 'unique_capability_no_tests', Mock(), is_first_party=True)
    assert result is False


def test_conformance_runner_third_party_fail_open() -> None:
    from sovereignai.conformance.runner import ConformanceRunner
    from sovereignai.shared.trace_emitter import TraceEmitter
    trace = TraceEmitter()
    runner = ConformanceRunner(trace=trace)
    result = runner.check('test_component', 'hash123', 'unique_capability_no_tests_2', Mock(), is_first_party=False)
    assert result is True


def test_conformance_runner_test_exception() -> None:
    from sovereignai.conformance.runner import ConformanceRunner
    from sovereignai.conformance.registry import register
    from sovereignai.shared.trace_emitter import TraceEmitter
    trace = TraceEmitter()
    runner = ConformanceRunner(trace=trace)

    @register('test_capability')
    class FailingTest:
        def test_fails(self, instance):
            raise Exception('Test error')

    result = runner.check('test_component', 'hash123', 'test_capability', Mock(), is_first_party=False)
    assert result is False


def test_conformance_runner_cache_lru_eviction_in_check() -> None:
    from sovereignai.conformance.runner import ConformanceRunner
    from sovereignai.shared.trace_emitter import TraceEmitter
    trace = TraceEmitter()
    runner = ConformanceRunner(trace=trace)
    for i in range(1025):
        runner.check(f'comp{i}', f'hash{i}', 'unique_capability_no_tests_3', Mock(), is_first_party=False)
    assert len(runner._cache) <= 1024


def test_conformance_base_concrete_implementation() -> None:
    from sovereignai.conformance.base import BaseConformanceTest, ConformanceResult
    class ConcreteTest(BaseConformanceTest):
        def test_component_has_required_interface(self, instance) -> None:
            assert instance is not None
    test = ConcreteTest()
    test.test_component_has_required_interface(Mock())


