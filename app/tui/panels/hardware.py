from __future__ import annotations

from typing import Any

from sovereignai.shared.capability_api import CapabilityAPI
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, DataTable, Static


class HardwarePanel(Vertical):
    def __init__(self, container: Any, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._container = container
        self._api = None

    def compose(self) -> ComposeResult:
        yield Static("Hardware Information", id="hardware-title")
        yield Horizontal(
            Static("CPU", id="cpu-card"),
            Static("Memory", id="memory-card"),
            Static("GPU", id="gpu-card"),
            Static("Disk", id="disk-card"),
            id="cards-container"
        )
        yield Button("Refresh", id="btn-refresh")
        yield DataTable(id="process-table")

    def on_mount(self) -> None:
        self.call_after_refresh(self._refresh_hardware)

    def _refresh_hardware(self) -> None:
        if self._api is None:
            try:
                self._api = self._container.retrieve(CapabilityAPI)
            except Exception as e:
                import traceback
                print(f"HardwarePanel load error: {e}")
                traceback.print_exc()
                return

        from textual import work

        @work(thread=True)
        def fetch_hardware():
            from sovereignai.shared.auth import AuthError
            try:
                return self._api.query_hardware_status("dummy_token")
            except AuthError:
                return None

        snapshot = fetch_hardware()
        if snapshot is None:
            return

        cpu_card = self.query_one("#cpu-card", Static)
        cpu_model = self._get_cpu_model()
        cpu_cores = self._get_cpu_cores()
        cpu_card.update(f"CPU: {snapshot.cpu_percent:.1f}%\nModel: {cpu_model}\nCores: {cpu_cores}")

        memory_card = self.query_one("#memory-card", Static)
        memory_speed = f"{snapshot.memory_bandwidth_gbps:.0f} GB/s"
        memory_card.update(
            f"Memory: {snapshot.ram_used_gb:.1f}GB / {snapshot.ram_total_gb:.1f}GB\n"
            f"({snapshot.ram_percent:.1f}%)\nSpeed: {memory_speed}"
        )

        gpu_card = self.query_one("#gpu-card", Static)
        if snapshot.gpus:
            gpu = snapshot.gpus[0]
            gpu_card.update(
                f"GPU: {gpu.name}\n"
                f"VRAM: {gpu.vram_used_mb}MB / {gpu.vram_total_mb}MB\n"
                f"Util: {gpu.utilization_percent:.1f}%"
            )
        else:
            gpu_card.update("GPU: Not detected")

        disk_card = self.query_one("#disk-card", Static)
        if snapshot.disks:
            disk = snapshot.disks[0]
            disk_card.update(
                f"Disk: {disk.used_gb:.1f}GB / {disk.total_gb:.1f}GB\n"
                f"({disk.percent:.1f}%)\nPath: {disk.path}"
            )
        else:
            disk_card.update("Disk: Not detected")

        self._refresh_process_table()

    def _get_cpu_model(self) -> str:
        import platform
        return platform.processor() or "Unknown"

    def _get_cpu_cores(self) -> int:
        import psutil
        return psutil.cpu_count(logical=False) or 0

    def _refresh_process_table(self) -> None:
        table = self.query_one("#process-table", DataTable)
        table.clear(columns=True)
        table.add_column("Name")
        table.add_column("PID")
        table.add_column("CPU%")
        table.add_column("Mem%")

        import psutil
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                table.add_row(
                    proc.info['name'] or "Unknown",
                    str(proc.info['pid']),
                    f"{proc.info['cpu_percent'] or 0:.1f}",
                    f"{proc.info['memory_percent'] or 0:.1f}"
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-refresh":
            self._refresh_hardware()
