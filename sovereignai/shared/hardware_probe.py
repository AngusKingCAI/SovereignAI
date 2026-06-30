import platform


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
