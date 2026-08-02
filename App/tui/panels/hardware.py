from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, DataTable, Static

from app.tui.client import TUIWebClient


class HardwarePanel(Vertical):
    """Hardware panel showing hardware subsystems from /api/health.

    Filters subsystems by kind="hardware" and displays hardware-specific
    subsystem details from the details field.
    Uses REST polling (SSE disabled per DEBT-7).
    """

    def __init__(
        self,
        client: TUIWebClient,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._client = client
        self._health_data: dict[str, Any] = {}

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
        yield DataTable(id="hardware-table")

    def on_mount(self) -> None:
        self.call_after_refresh(self._load_data)

    async def _load_data(self) -> None:
        """Load health data from /api/health."""
        try:
            async with self._client as client:
                response = await client.get("/api/health")
                if response.status_code == 200:
                    self._health_data = response.json()
                    self._update_display()
                else:
                    self._update_error(f"HTTP {response.status_code}")
        except Exception as e:
            self._update_error(str(e))

    def _update_display(self) -> None:
        """Update display with hardware subsystems."""
        subsystems = self._health_data.get("subsystems", [])
        hardware_subsystems = [s for s in subsystems if s.get("kind") == "hardware"]

        if not hardware_subsystems:
            self._update_no_hardware()
            return

        # Update hardware cards from subsystem details
        for subsystem in hardware_subsystems:
            details = subsystem.get("details", {})
            name = subsystem.get("name", "")

            if name == "cpu":
                self._update_cpu_card(details)
            elif name == "memory":
                self._update_memory_card(details)
            elif name == "gpu":
                self._update_gpu_card(details)
            elif name == "disk":
                self._update_disk_card(details)

        # Update hardware table
        self._update_hardware_table(hardware_subsystems)

    def _update_cpu_card(self, details: dict[str, Any]) -> None:
        """Update CPU card with details."""
        try:
            cpu_card = self.query_one("#cpu-card", Static)
            cpu_percent = details.get("cpu_percent", 0)
            cpu_model = details.get("model", "Unknown")
            cpu_cores = details.get("cores", 0)
            cpu_card.update(f"CPU: {cpu_percent:.1f}%\nModel: {cpu_model}\nCores: {cpu_cores}")
        except Exception:
            # Widget tree not mounted (e.g., during testing)
            pass

    def _update_memory_card(self, details: dict[str, Any]) -> None:
        """Update memory card with details."""
        try:
            memory_card = self.query_one("#memory-card", Static)
            ram_used = details.get("ram_used_gb", 0)
            ram_total = details.get("ram_total_gb", 0)
            ram_percent = details.get("ram_percent", 0)
            memory_speed = details.get("memory_bandwidth_gbps", 0)
            speed_str = f"{memory_speed:.0f} GB/s" if memory_speed else "Unknown"
            memory_card.update(
                f"Memory: {ram_used:.1f}GB / {ram_total:.1f}GB\n"
                f"({ram_percent:.1f}%)\nSpeed: {speed_str}"
            )
        except Exception:
            # Widget tree not mounted (e.g., during testing)
            pass

    def _update_gpu_card(self, details: dict[str, Any]) -> None:
        """Update GPU card with details."""
        try:
            gpu_card = self.query_one("#gpu-card", Static)
            gpus = details.get("gpus", [])
            if gpus:
                gpu = gpus[0]
                gpu_name = gpu.get("name", "Unknown")
                vram_used = gpu.get("vram_used_mb", 0)
                vram_total = gpu.get("vram_total_mb", 0)
                gpu_util = gpu.get("utilization_percent", 0)
                gpu_card.update(
                    f"GPU: {gpu_name}\n"
                    f"VRAM: {vram_used}MB / {vram_total}MB\n"
                    f"Util: {gpu_util:.1f}%"
                )
            else:
                gpu_card.update("GPU: Not detected")
        except Exception:
            # Widget tree not mounted (e.g., during testing)
            pass

    def _update_disk_card(self, details: dict[str, Any]) -> None:
        """Update disk card with details."""
        try:
            disk_card = self.query_one("#disk-card", Static)
            disks = details.get("disks", [])
            if disks:
                disk = disks[0]
                disk_used = disk.get("used_gb", 0)
                disk_total = disk.get("total_gb", 0)
                disk_percent = disk.get("percent", 0)
                disk_path = disk.get("path", "Unknown")
                disk_card.update(
                    f"Disk: {disk_used:.1f}GB / {disk_total:.1f}GB\n"
                    f"({disk_percent:.1f}%)\nPath: {disk_path}"
                )
            else:
                disk_card.update("Disk: Not detected")
        except Exception:
            # Widget tree not mounted (e.g., during testing)
            pass

    def _update_hardware_table(self, subsystems: list[dict[str, Any]]) -> None:
        """Update hardware table with all subsystems."""
        try:
            table = self.query_one("#hardware-table", DataTable)
            table.clear(columns=True)
            table.add_column("Name")
            table.add_column("Status")
            table.add_column("Details")

            for subsystem in subsystems:
                name = subsystem.get("name", "unknown")
                status = subsystem.get("status", "unknown")
                details = subsystem.get("details", {})

                # Summarize details
                detail_summary = str(details)[:50] + "..." if len(str(details)) > 50 else str(details)

                # Color code status
                if status == "healthy":
                    status_badge = "[green]Healthy[/green]"
                elif status == "degraded":
                    status_badge = "[yellow]Degraded[/yellow]"
                elif status == "unhealthy":
                    status_badge = "[red]Unhealthy[/red]"
                else:
                    status_badge = f"[yellow]{status}[/yellow]"

                table.add_row(name, status_badge, detail_summary)
        except Exception:
            # Widget tree not mounted (e.g., during testing)
            pass

    def _update_no_hardware(self) -> None:
        """Update display when no hardware subsystems found."""
        try:
            cpu_card = self.query_one("#cpu-card", Static)
            cpu_card.update("CPU: No data")
            memory_card = self.query_one("#memory-card", Static)
            memory_card.update("Memory: No data")
            gpu_card = self.query_one("#gpu-card", Static)
            gpu_card.update("GPU: No data")
            disk_card = self.query_one("#disk-card", Static)
            disk_card.update("Disk: No data")

            table = self.query_one("#hardware-table", DataTable)
            table.clear(columns=True)
            table.add_column("Name")
            table.add_column("Status")
            table.add_column("Details")
            table.add_row("No hardware data", "--", "--")
        except Exception:
            # Widget tree not mounted (e.g., during testing)
            pass

    def _update_error(self, error_msg: str) -> None:
        """Update display with error message."""
        try:
            cpu_card = self.query_one("#cpu-card", Static)
            cpu_card.update("CPU: Error")
            memory_card = self.query_one("#memory-card", Static)
            memory_card.update("Memory: Error")
            gpu_card = self.query_one("#gpu-card", Static)
            gpu_card.update("GPU: Error")
            disk_card = self.query_one("#disk-card", Static)
            disk_card.update("Disk: Error")

            table = self.query_one("#hardware-table", DataTable)
            table.clear(columns=True)
            table.add_column("Name")
            table.add_column("Status")
            table.add_column("Details")
            table.add_row(f"Error: {error_msg}", "--", "--")
        except Exception:
            # Widget tree not mounted (e.g., during testing)
            pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-refresh":
            self.call_after_refresh(self._load_data)
