from __future__ import annotations

import shutil
import subprocess
import time
from typing import TYPE_CHECKING

import httpx

from services.base import ServiceNotFoundError, ServiceStartError, ServiceStatus
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import TraceLevel

if TYPE_CHECKING:
    pass


class OllamaServiceProvider:
    name = "ollama"

    def __init__(self, trace: TraceEmitter, port: int = 11434) -> None:
        self._trace = trace
        self._port = port
        self._proc: subprocess.Popen[bytes] | None = None

    def start(self) -> None:
        if shutil.which("ollama") is None:
            self._trace.emit(
                component="OllamaServiceProvider",
                level=TraceLevel.ERROR,
                message="ollama not on PATH",
            )
            raise ServiceNotFoundError("ollama not on PATH")

        self._proc = subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        start_time = time.monotonic()
        timeout = 10
        while time.monotonic() - start_time < timeout:
            try:
                response = httpx.get(f"http://localhost:{self._port}/api/version", timeout=1)
                if response.status_code == 200:
                    self._trace.emit(
                        component="OllamaServiceProvider",
                        level=TraceLevel.INFO,
                        message=f"Ollama started on port {self._port}",
                    )
                    return
            except Exception:
                time.sleep(0.1)

        self._proc.terminate()
        try:
            self._proc.wait(timeout=2)
        except Exception:
            self._proc.kill()

        self._trace.emit(
            component="OllamaServiceProvider",
            level=TraceLevel.ERROR,
            message=f"startup timeout: port {self._port}",
        )
        raise ServiceStartError(f"Ollama startup timeout on port {self._port}")

    def stop(self) -> None:
        if self._proc is None:
            return

        self._proc.terminate()
        try:
            self._proc.wait(timeout=5)
        except Exception:
            self._proc.kill()

        self._proc = None

    def health_check(self) -> ServiceStatus:
        if self._proc is None:
            return ServiceStatus(running=False, pid=None, port=None)

        try:
            response = httpx.get(f"http://localhost:{self._port}/api/version", timeout=1)
            if response.status_code == 200:
                return ServiceStatus(running=True, pid=self._proc.pid, port=self._port)
        except Exception:
            pass

        return ServiceStatus(running=False, pid=self._proc.pid, port=self._port)
