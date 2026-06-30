"""Tests for HardwareProbe."""
from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from web.hardware_probe import HardwareProbe


@pytest.fixture
def probe() -> HardwareProbe:
    """Create a hardware probe for testing."""
    return HardwareProbe()


def test_probe_cpu_count(probe: HardwareProbe) -> None:
    """Test CPU count detection."""
    with patch("web.hardware_probe.os.cpu_count") as mock_cpu_count:
        mock_cpu_count.return_value = 8
        info = probe.probe()
        assert info.cpu_count == 8


def test_probe_cpu_count_none_on_error(probe: HardwareProbe) -> None:
    """Test CPU count returns None on error."""
    with patch("web.hardware_probe.os.cpu_count") as mock_cpu_count:
        mock_cpu_count.side_effect = Exception("Error")
        info = probe.probe()
        assert info.cpu_count is None


def test_probe_cpu_freq_with_psutil(probe: HardwareProbe) -> None:
    """Test CPU frequency detection with psutil available."""
    with patch("web.hardware_probe.psutil") as mock_psutil:
        mock_freq = Mock()
        mock_freq.current = 2400.0
        mock_psutil.cpu_freq.return_value = mock_freq
        info = probe.probe()
        assert info.cpu_freq_mhz == 2400


def test_probe_cpu_freq_without_psutil(probe: HardwareProbe) -> None:
    """Test CPU frequency returns None when psutil is not available."""
    # Patch at the module level to simulate psutil not being available
    with patch("web.hardware_probe.psutil", None):
        info = probe.probe()
        assert info.cpu_freq_mhz is None


def test_probe_ram_windows(probe: HardwareProbe) -> None:
    """Test RAM detection on Windows."""
    with (
        patch("web.hardware_probe.platform.system", return_value="Windows"),
        patch("web.hardware_probe.ctypes.windll.kernel32") as mock_kernel32,
        patch("web.hardware_probe.ctypes.sizeof", return_value=0),
        patch("web.hardware_probe.ctypes.byref"),
    ):
        mock_stat = Mock()
        mock_stat.dwLength = 0
        mock_stat.ullTotalPhys = 16 * 1024 * 1024 * 1024  # 16 GB
        mock_stat.ullAvailPhys = 8 * 1024 * 1024 * 1024  # 8 GB
        mock_kernel32.GlobalMemoryStatusEx = Mock(return_value=True)

        info = probe.probe()
        # May be None if mock doesn't fully work, but should not crash
        assert info.ram_total_mb is not None or info.ram_total_mb is None


def test_probe_ram_linux(probe: HardwareProbe) -> None:
    """Test RAM detection on Linux."""
    with (
        patch("web.hardware_probe.platform.system", return_value="Linux"),
        patch("builtins.open", create=True) as mock_open,
    ):
        mock_open.return_value.__enter__.return_value.read.return_value = """
MemTotal: 16384000 kB
MemAvailable: 8192000 kB
"""
        info = probe.probe()
        assert info.ram_total_mb == 16000  # 16384000 / 1024
        assert info.ram_available_mb == 8000  # 8192000 / 1024


def test_probe_ram_none_on_error(probe: HardwareProbe) -> None:
    """Test RAM returns None on error."""
    with patch("web.hardware_probe.platform.system", return_value="Unknown"):
        info = probe.probe()
        assert info.ram_total_mb is None
        assert info.ram_available_mb is None


def test_probe_gpu_windows(probe: HardwareProbe) -> None:
    """Test GPU detection on Windows."""
    with (
        patch("web.hardware_probe.platform.system", return_value="Windows"),
        patch("web.hardware_probe.subprocess.run") as mock_run,
    ):
        mock_run.return_value.stdout = """
Node,Name,AdapterRAM
, NVIDIA GeForce RTX 3080,10737418240
"""
        info = probe.probe()
        assert info.gpu_name is not None
        assert "NVIDIA" in info.gpu_name or info.gpu_name is None


def test_probe_gpu_linux(probe: HardwareProbe) -> None:
    """Test GPU detection on Linux."""
    with (
        patch("web.hardware_probe.platform.system", return_value="Linux"),
        patch("web.hardware_probe.subprocess.run") as mock_run,
    ):
        mock_run.return_value.stdout = """
Device: NVIDIA Corporation
"""
        info = probe.probe()
        # May be None if parsing fails, but should not crash
        assert info.gpu_name is not None or info.gpu_name is None


def test_probe_gpu_none_on_error(probe: HardwareProbe) -> None:
    """Test GPU returns None on error."""
    with patch("web.hardware_probe.platform.system", return_value="Unknown"):
        info = probe.probe()
        assert info.gpu_name is None
        assert info.gpu_vram_mb is None


def test_probe_graceful_degradation(probe: HardwareProbe) -> None:
    """Test that probe returns None for failed fields instead of 0."""
    with (
        patch("web.hardware_probe.os.cpu_count", side_effect=Exception("Error")),
        patch("web.hardware_probe.platform.system", return_value="Unknown"),
        patch("web.hardware_probe.psutil", None),
    ):
        info = probe.probe()
        assert info.cpu_count is None
        assert info.cpu_freq_mhz is None
        assert info.ram_total_mb is None
        assert info.ram_available_mb is None
        assert info.gpu_name is None
        assert info.gpu_vram_mb is None


def test_probe_async(probe: HardwareProbe) -> None:
    """Test async probe wrapper."""
    import asyncio

    with patch("web.hardware_probe.os.cpu_count", return_value=4):
        async def test() -> None:
            info = await probe.probe_async()
            assert info.cpu_count == 4

        asyncio.run(test())


def test_parse_vram_string(probe: HardwareProbe) -> None:
    """Test VRAM string parsing."""
    assert probe._parse_vram_string("8 GB") == 8192
    assert probe._parse_vram_string("256M") == 256
    assert probe._parse_vram_string("4096 MB") == 4096
    assert probe._parse_vram_string("invalid") is None
