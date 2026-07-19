import platform

from sovereignai.shared.types import DiskUsage, GpuInfo, HardwareSnapshot

GPU_MEMORY_TYPE_MAP: dict[str, str] = {
    "RTX 4090": "GDDR6X",
    "RTX 4080": "GDDR6X",
    "RTX 4070": "GDDR6X",
    "RTX 4060": "GDDR6",
    "RTX 3080": "GDDR6X",
    "RTX 3070": "GDDR6",
    "RTX 3060": "GDDR6",
    "RTX 3060 Laptop": "GDDR6",
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


class HardwareProbe:

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
            except (FileNotFoundError, subprocess.TimeoutExpired) as e:
                import logging
                logging.getLogger(__name__).error(f"nvidia-smi check failed: {e}")
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
            except (FileNotFoundError, subprocess.TimeoutExpired, ValueError) as e:
                import logging
                logging.getLogger(__name__).error(f"CPU core count check failed: {e}")
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

    def _detect_gpus(self) -> list[GpuInfo]:
        gpus: list[GpuInfo] = []

        if not self.has_nvidia_gpu():
            return gpus

        try:
            import subprocess
            result = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=name,memory.total,memory.used,utilization.gpu",
                    "--format=csv,noheader,nounits",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split("\n"):
                    if not line:
                        continue
                    parts = line.split(",")
                    if len(parts) >= 4:
                        name = parts[0].strip()
                        vram_total_mb = int(parts[1].strip())
                        vram_used_mb = int(parts[2].strip())
                        utilization_percent = float(parts[3].strip())
                        memory_type = None
                        for model, mem_type in GPU_MEMORY_TYPE_MAP.items():
                            if model in name:
                                memory_type = mem_type
                                break
                        gpus.append(
                            GpuInfo(
                                name=name,
                                vram_total_mb=vram_total_mb,
                                vram_used_mb=vram_used_mb,
                                utilization_percent=utilization_percent,
                                memory_type=memory_type,
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
