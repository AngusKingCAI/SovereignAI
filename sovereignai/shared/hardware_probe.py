import platform

from sovereignai.shared.types import DiskUsage, GpuInfo, HardwareSnapshot

try:
    import nvidia_ml_py3 as pynvml
    PYNVML_AVAILABLE = True
except ImportError:
    PYNVML_AVAILABLE = False


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

        gpus: list[GpuInfo] = []
        memory_bandwidth_gbps = 512.0

        if PYNVML_AVAILABLE:
            try:
                pynvml.nvmlInit()
                device_count = pynvml.nvmlDeviceGetCount()
                for i in range(device_count):
                    handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                    name = pynvml.nvmlDeviceGetName(handle)
                    if isinstance(name, bytes):
                        name = name.decode("utf-8")

                    mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                    vram_total_mb = mem_info.total // (1024**2)
                    vram_used_mb = mem_info.used // (1024**2)

                    utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
                    utilization_percent = float(utilization.gpu)

                    memory_type = None
                    for gpu_substring, mem_type in GPU_MEMORY_TYPE_MAP.items():
                        if gpu_substring in name:
                            memory_type = mem_type
                            bandwidth = float(MEMORY_BANDWIDTH_GBPS.get(mem_type, 512))
                            if bandwidth > memory_bandwidth_gbps:
                                memory_bandwidth_gbps = bandwidth
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
                pynvml.nvmlShutdown()
            except Exception:
                pass

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
