"""Detect system hardware resources for the Hardware panel.

This module probes CPU, RAM, GPU, and VRAM availability using
platform-appropriate methods. It runs in the web layer, not the core.
"""
from __future__ import annotations

import asyncio
import os
import platform
import subprocess
from dataclasses import dataclass

try:
    import psutil
except ImportError:
    psutil = None  # type: ignore[assignment]

try:
    import ctypes
except ImportError:
    ctypes = None  # type: ignore[assignment]


@dataclass
class HardwareInfo:
    """Snapshot of system hardware resources."""
    cpu_count: int | None
    cpu_freq_mhz: int | None
    ram_total_mb: int | None
    ram_available_mb: int | None
    gpu_name: str | None
    gpu_vram_mb: int | None
    timestamp: float


class HardwareProbe:
    """Probe system hardware resources using platform-appropriate methods.

    This class provides methods to detect CPU, RAM, GPU, and VRAM on
    Windows, macOS, and Linux. It uses asyncio.to_thread() to wrap
    blocking calls when called from async contexts.
    """

    def __init__(self) -> None:
        """Create a hardware probe instance."""
        pass

    async def probe_async(self) -> HardwareInfo:
        """Probe hardware asynchronously using asyncio.to_thread.

        Returns:
            HardwareInfo with current system resource snapshot.
        """
        return await asyncio.to_thread(self.probe)

    def probe(self) -> HardwareInfo:
        """Probe hardware synchronously.

        Returns:
            HardwareInfo with current system resource snapshot.
        """
        import time
        timestamp = time.time()

        cpu_count = self._get_cpu_count()
        cpu_freq_mhz = self._get_cpu_freq()
        ram_total_mb, ram_available_mb = self._get_ram()
        gpu_name, gpu_vram_mb = self._get_gpu()

        return HardwareInfo(
            cpu_count=cpu_count,
            cpu_freq_mhz=cpu_freq_mhz,
            ram_total_mb=ram_total_mb,
            ram_available_mb=ram_available_mb,
            gpu_name=gpu_name,
            gpu_vram_mb=gpu_vram_mb,
            timestamp=timestamp,
        )

    def _get_cpu_count(self) -> int | None:
        """Get the number of CPU cores.

        Returns:
            CPU count or None if detection fails.
        """
        try:
            return os.cpu_count()
        except Exception:
            return None

    def _get_cpu_freq(self) -> int | None:
        """Get CPU frequency in MHz.

        Per Finding 20: Use psutil.cpu_freq() if available, else None.
        Do NOT use os.cpu_freq() (requires Python 3.13+).

        Returns:
            CPU frequency in MHz or None if detection fails.
        """
        if psutil is not None:
            try:
                freq = psutil.cpu_freq()
                if freq:
                    return int(freq.current)
            except Exception:
                pass
        return None

    def _get_ram(self) -> tuple[int | None, int | None]:
        """Get total and available RAM in MB.

        Returns:
            Tuple of (total_mb, available_mb) or (None, None) if detection fails.
        """
        system = platform.system()
        try:
            if system == "Windows":
                return self._get_ram_windows()
            elif system == "Darwin":  # macOS
                return self._get_ram_macos()
            elif system == "Linux":
                return self._get_ram_linux()
        except Exception:
            pass
        return None, None

    def _get_ram_windows(self) -> tuple[int | None, int | None]:
        """Get RAM on Windows using ctypes.

        Returns:
            Tuple of (total_mb, available_mb).
        """
        if ctypes is None:
            return None, None
        try:
            kernel32 = ctypes.windll.kernel32
            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [
                    ("dwLength", ctypes.c_ulong),
                    ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
                ]
            stat = MEMORYSTATUSEX()
            stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
            kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
            total_mb = int(stat.ullTotalPhys // (1024 * 1024))
            available_mb = int(stat.ullAvailPhys // (1024 * 1024))
            return total_mb, available_mb
        except Exception:
            return None, None

    def _get_ram_macos(self) -> tuple[int | None, int | None]:
        """Get RAM on macOS using sysctl.

        Returns:
            Tuple of (total_mb, available_mb).
        """
        try:
            import sysctl
            total_bytes = sysctl.control("hw.memsize")
            total_mb = int(total_bytes // (1024 * 1024))
            # macOS doesn't easily expose available memory
            return total_mb, None
        except Exception:
            return None, None

    def _get_ram_linux(self) -> tuple[int | None, int | None]:
        """Get RAM on Linux by reading /proc/meminfo.

        Returns:
            Tuple of (total_mb, available_mb).
        """
        from sovereignai.shared.trace_emitter import TraceEmitter, TraceLevel
        trace = TraceEmitter()
        trace.emit(
            component="hardware_probe",
            level=TraceLevel.DEBUG,
            message="Reading RAM from /proc/meminfo",
        )
        try:
            with open("/proc/meminfo") as f:
                meminfo = f.read()
            total_kb = None
            available_kb = None
            for line in meminfo.split("\n"):
                if line.startswith("MemTotal:"):
                    total_kb = int(line.split()[1])
                elif line.startswith("MemAvailable:"):
                    available_kb = int(line.split()[1])
            if total_kb:
                total_mb = total_kb // 1024
                available_mb = available_kb // 1024 if available_kb else None
                return total_mb, available_mb
        except Exception:
            pass
        return None, None

    def _get_gpu(self) -> tuple[str | None, int | None]:
        """Get GPU name and VRAM in MB.

        Per Finding 8: Multi-platform GPU detection using WMI on Windows,
        system_profiler on macOS, and lspci on Linux.

        Returns:
            Tuple of (gpu_name, vram_mb) or (None, None) if no GPU detected.
        """
        system = platform.system()
        try:
            if system == "Windows":
                return self._get_gpu_windows()
            elif system == "Darwin":  # macOS
                return self._get_gpu_macos()
            elif system == "Linux":
                return self._get_gpu_linux()
        except Exception:
            pass
        return None, None

    def _get_gpu_windows(self) -> tuple[str | None, int | None]:
        """Get GPU on Windows using WMIC.

        Per Finding 16: Use /format:csv not --format:csv.

        Returns:
            Tuple of (gpu_name, vram_mb).
        """
        try:
            result = subprocess.run(
                ["wmic", "path", "win32_VideoController", "get", "Name,AdapterRAM", "/format:csv"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            lines = result.stdout.strip().split("\n")
            if len(lines) > 1:
                # Skip header line
                for line in lines[1:]:
                    parts = line.split(",")
                    if len(parts) >= 2:
                        name = parts[1].strip()
                        ram_bytes = parts[2].strip()
                        if name and name != "Node":
                            if ram_bytes and ram_bytes.isdigit():
                                vram_mb = int(int(ram_bytes) // (1024 * 1024))
                            else:
                                vram_mb = None
                            return name, vram_mb
        except Exception:
            pass
        return None, None

    def _get_gpu_macos(self) -> tuple[str | None, int | None]:
        """Get GPU on macOS using system_profiler.

        Returns:
            Tuple of (gpu_name, vram_mb).
        """
        try:
            result = subprocess.run(
                ["system_profiler", "SPDisplaysDataType"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            output = result.stdout
            # Parse GPU name from output
            for line in output.split("\n"):
                if "Chipset Model" in line or "VRAM" in line:
                    parts = line.split(":")
                    if len(parts) >= 2:
                        value = parts[1].strip()
                        if "Chipset Model" in line:
                            gpu_name = value
                        elif "VRAM" in line:
                            # Parse VRAM (e.g., "8 GB")
                            vram_mb = self._parse_vram_string(value)
                            return gpu_name, vram_mb
        except Exception:
            pass
        return None, None

    def _get_gpu_linux(self) -> tuple[str | None, int | None]:
        """Get GPU on Linux using lspci.

        Returns:
            Tuple of (gpu_name, vram_mb).
        """
        try:
            result = subprocess.run(
                ["lspci", "-vmm"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            output = result.stdout
            gpu_name = None
            for line in output.split("\n"):
                if line.startswith("Device:"):
                    gpu_name = line.split(":", 1)[1].strip()
                    if "VGA" in gpu_name or "3D" in gpu_name:
                        break
            # Try to get VRAM from lspci -v
            if gpu_name:
                vram_result = subprocess.run(
                    ["lspci", "-v", "-s", gpu_name.split()[0]],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                # Parse VRAM from output
                for line in vram_result.stdout.split("\n"):
                    if "prefetchable" in line.lower():
                        # Extract size (e.g., "256M")
                        size_str = line.split()[-1]
                        vram_mb = self._parse_vram_string(size_str)
                        return gpu_name, vram_mb
                return gpu_name, None
        except Exception:
            pass
        return None, None

    def _parse_vram_string(self, vram_str: str) -> int | None:
        """Parse VRAM string like "8 GB" or "256M" into MB.

        Args:
            vram_str: String like "8 GB", "256M", "4096 MB".

        Returns:
            VRAM in MB or None if parsing fails.
        """
        try:
            vram_str = vram_str.strip().upper()
            if "GB" in vram_str:
                value = float(vram_str.replace("GB", "").strip())
                return int(value * 1024)
            elif "MB" in vram_str:
                value = float(vram_str.replace("MB", "").strip())
                return int(value)
            elif "M" in vram_str:
                value = float(vram_str.replace("M", "").strip())
                return int(value)
        except Exception:
            pass
        return None
