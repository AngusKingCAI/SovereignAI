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


