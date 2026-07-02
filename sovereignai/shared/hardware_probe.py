import json
import platform
from pathlib import Path

from sovereignai.shared.types import DiskUsage, GpuInfo, HardwareSnapshot

GPU_MEMORY_TYPE_MAP: dict[str, str] = {
    "RTX 4090": "GDDR6X",
    "RTX 4080": "GDDR6X",
    "RTX 4070": "GDDR6X",
    "RTX 4060": "GDDR6",
    "RTX 3080": "GDDR6X",
    "RTX 3070": "GDDR6",
    "RTX 3060": "GDDR6",
    "A100": "HBM2",
    "A6000": "GDDR6",
    "V100": "HBM2",
}


MEMORY_BANDWIDTH_GBPS: dict[str, int] = {
    "GDDR6": 768,
    "GDDR6X": 1008,
    "HBM2": 2000,
    "HBM2e": 2600,
    "HBM3": 3350,
    "DDR5": 480,
    "DDR4": 384,
}


def _load_gpu_bandwidth_db() -> dict[str, dict[str, dict[str, int | str]]]:
    """Load PCI-ID to GPU bandwidth mapping from JSON database.

    Returns:
        Nested dict structure: {vendor_id: {device_id: {name, bandwidth_gbps}}}
    """
    db_path = Path(__file__).parent / "gpu_bandwidth_db.json"
    try:
        with open(db_path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


class HardwareProbe:
    GPU_BANDWIDTH_MAP: dict[str, int] = {
        "RTX 4090": 1008,
        "RTX 4080": 717,
        "RTX 4070 Ti": 504,
        "RTX 4070": 504,
        "RTX 4060 Ti": 288,
        "RTX 4060": 288,
        "RTX 3060 Laptop": 192,
        "RTX 3060": 360,
        "RTX 3070": 448,
        "RTX 3080": 760,
        "RTX 3090": 936,
        "RTX 2080 Ti": 616,
        "RTX 2080": 448,
        "RTX 2070": 448,
        "RTX 2060": 336,
        "GTX 1660 Ti": 288,
        "GTX 1660": 192,
        "GTX 1650": 128,
    }

    def has_nvidia_gpu(self) -> bool:
        if platform.system() == "Windows":
            try:
                import subprocess
                result = subprocess.run(
                    ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                return result.returncode == 0 and bool(result.stdout.strip())
            except (FileNotFoundError, subprocess.TimeoutExpired):
                return False
        else:
            # Linux/macOS: check for nvidia-smi in PATH
            try:
                import shutil
                return shutil.which("nvidia-smi") is not None
            except Exception:
                return False

    def get_vram_mb(self) -> int:
        if platform.system() == "Windows":
            try:
                import subprocess
                result = subprocess.run(
                    ["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    return int(result.stdout.strip())
            except (FileNotFoundError, subprocess.TimeoutExpired, ValueError):
                pass
        return 0

    def has_cuda_via_torch(self) -> bool:
        try:
            import importlib.util
            if importlib.util.find_spec("torch") is None:
                return False
            import torch
            result: bool = torch.cuda.is_available()
            return result
        except (ImportError, OSError):
            return False

    def _get_gpu_bandwidth_by_pci_id(self, vendor_id: str, device_id: str) -> int | None:
        """Get GPU bandwidth from PCI-ID database lookup.

        Args:
            vendor_id: PCI vendor ID (e.g., "10DE" for NVIDIA)
            device_id: PCI device ID

        Returns:
            Bandwidth in GB/s or None if not found in database
        """
        db = _load_gpu_bandwidth_db()
        if vendor_id in db and device_id in db[vendor_id]:
            return db[vendor_id][device_id].get("bandwidth_gbps")
        return None

    def _get_gpu_bandwidth_by_name(self, gpu_name: str) -> int | None:
        """Get GPU bandwidth from substring-based name lookup (fallback).

        Args:
            gpu_name: GPU name string

        Returns:
            Bandwidth in GB/s or None if not found
        """
        for key, bandwidth in self.GPU_BANDWIDTH_MAP.items():
            if key in gpu_name:
                return bandwidth
        return None

    def _detect_gpus(self) -> list[GpuInfo]:
        """Detect GPUs and their information.

        Returns:
            List of GpuInfo objects with detected GPU information
        """
        gpus: list[GpuInfo] = []

        if not self.has_nvidia_gpu():
            return gpus

        try:
            import subprocess
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split("\n"):
                    if not line:
                        continue
                    parts = line.split(",")
                    if len(parts) >= 2:
                        name = parts[0].strip()
                        vram_mb = int(parts[1].strip())
                        bandwidth = self._get_gpu_bandwidth_by_name(name) or 0.0
                        gpus.append(
                            GpuInfo(
                                name=name,
                                vram_mb=vram_mb,
                                memory_bandwidth_gbps=bandwidth,
                            )
                        )
        except (FileNotFoundError, subprocess.TimeoutExpired, ValueError):
            pass

        return gpus

    def sample(self) -> HardwareSnapshot:
        import psutil

        cpu_percent = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()
        ram_percent = mem.percent
        ram_used_gb = mem.used / (1024**3)
        ram_total_gb = mem.total / (1024**3)
        ram_available_gb = mem.available / (1024**3)

        disks: list[DiskUsage] = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disks.append(
                    DiskUsage(
                        path=partition.mountpoint,
                        total_gb=usage.total / (1024**3),
                        used_gb=usage.used / (1024**3),
                        free_gb=usage.free / (1024**3),
                        percent=usage.percent,
                    )
                )
            except (PermissionError, OSError):
                continue

        gpus = self._detect_gpus()
        memory_bandwidth_gbps = 512.0

        return HardwareSnapshot(
            cpu_percent=cpu_percent,
            ram_percent=ram_percent,
            ram_used_gb=ram_used_gb,
            ram_total_gb=ram_total_gb,
            ram_available_gb=ram_available_gb,
            memory_bandwidth_gbps=memory_bandwidth_gbps,
            disks=disks,
            gpus=gpus,
        )
