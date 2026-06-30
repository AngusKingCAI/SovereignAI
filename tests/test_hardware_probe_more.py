"""Additional tests for hardware probe to improve coverage."""
from web.hardware_probe import HardwareInfo, HardwareProbe


def test_hardware_probe_init() -> None:
    """Test HardwareProbe initialization."""
    probe = HardwareProbe()
    assert probe is not None


def test_hardware_probe_probe_returns_hardware_info() -> None:
    """Test that probe returns HardwareInfo with correct structure."""
    probe = HardwareProbe()
    info = probe.probe()

    assert isinstance(info, HardwareInfo)
    assert hasattr(info, 'cpu_count')
    assert hasattr(info, 'ram_total_mb')
    assert hasattr(info, 'gpu_name')
    assert hasattr(info, 'timestamp')


def test_hardware_probe_probe_async() -> None:
    """Test probe_async method."""
    import asyncio

    probe = HardwareProbe()
    info = asyncio.run(probe.probe_async())

    assert isinstance(info, HardwareInfo)


def test_hardware_info_dataclass() -> None:
    """Test HardwareInfo dataclass."""
    info = HardwareInfo(
        cpu_count=8,
        cpu_freq_mhz=3000,
        ram_total_mb=16000,
        ram_available_mb=8000,
        gpu_name="Test GPU",
        gpu_vram_mb=8000,
        timestamp=1234567890.0
    )

    assert info.cpu_count == 8
    assert info.ram_total_mb == 16000
