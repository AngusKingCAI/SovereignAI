from __future__ import annotations

from unittest.mock import MagicMock, patch

from services.base import ServiceNotFoundError, ServiceStartError
from services.ollama_service.provider import OllamaServiceProvider
from sovereignai.shared.trace_emitter import TraceEmitter


def test_init_no_io() -> None:
    trace = TraceEmitter()
    provider = OllamaServiceProvider(trace, port=8080)
    assert provider.name == "ollama"
    assert provider._port == 8080


@patch("services.ollama_service.provider.shutil.which")
def test_start_ollama_not_found(mock_which: MagicMock) -> None:
    trace = TraceEmitter()
    provider = OllamaServiceProvider(trace)
    mock_which.return_value = None

    try:
        provider.start()
        assert False, "Should have raised ServiceNotFoundError"
    except ServiceNotFoundError:
        pass


@patch("services.ollama_service.provider.httpx.get")
@patch("services.ollama_service.provider.subprocess.Popen")
@patch("services.ollama_service.provider.shutil.which")
def test_start_success(mock_which: MagicMock, mock_popen: MagicMock, mock_get: MagicMock) -> None:
    trace = TraceEmitter()
    provider = OllamaServiceProvider(trace, port=8080)

    mock_which.return_value = "/usr/bin/ollama"
    mock_proc = MagicMock()
    mock_proc.pid = 1234
    mock_popen.return_value = mock_proc

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    provider.start()

    assert provider._proc is mock_proc
    mock_popen.assert_called_once()
    assert mock_popen.call_args.args[0] == ["ollama", "serve"]


@patch("services.ollama_service.provider.httpx.get")
@patch("services.ollama_service.provider.subprocess.Popen")
@patch("services.ollama_service.provider.shutil.which")
def test_start_timeout(mock_which: MagicMock, mock_popen: MagicMock, mock_get: MagicMock) -> None:
    trace = TraceEmitter()
    provider = OllamaServiceProvider(trace, port=8080)

    mock_which.return_value = "/usr/bin/ollama"
    mock_proc = MagicMock()
    mock_proc.pid = 1234
    mock_popen.return_value = mock_proc

    mock_get.side_effect = Exception("Connection refused")

    try:
        provider.start()
        assert False, "Should have raised ServiceStartError"
    except ServiceStartError as e:
        assert "timeout" in str(e)

    mock_proc.terminate.assert_called_once()


@patch("services.ollama_service.provider.httpx.get")
@patch("services.ollama_service.provider.subprocess.Popen")
@patch("services.ollama_service.provider.shutil.which")
def test_health_check_running(mock_which: MagicMock, mock_popen: MagicMock, mock_get: MagicMock) -> None:
    trace = TraceEmitter()
    provider = OllamaServiceProvider(trace, port=8080)

    mock_which.return_value = "/usr/bin/ollama"
    mock_proc = MagicMock()
    mock_proc.pid = 1234
    mock_popen.return_value = mock_proc

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    provider.start()

    status = provider.health_check()
    assert status.running is True
    assert status.pid == 1234
    assert status.port == 8080


@patch("services.ollama_service.provider.httpx.get")
@patch("services.ollama_service.provider.subprocess.Popen")
@patch("services.ollama_service.provider.shutil.which")
def test_health_check_not_running(mock_which: MagicMock, mock_popen: MagicMock, mock_get: MagicMock) -> None:
    trace = TraceEmitter()
    provider = OllamaServiceProvider(trace, port=8080)

    status = provider.health_check()
    assert status.running is False
    assert status.pid is None
    assert status.port is None


@patch("services.ollama_service.provider.subprocess.Popen")
@patch("services.ollama_service.provider.shutil.which")
def test_stop(mock_which: MagicMock, mock_popen: MagicMock) -> None:
    trace = TraceEmitter()
    provider = OllamaServiceProvider(trace, port=8080)

    mock_which.return_value = "/usr/bin/ollama"
    mock_proc = MagicMock()
    mock_proc.pid = 1234
    mock_popen.return_value = mock_proc

    provider._proc = mock_proc
    provider.stop()

    mock_proc.terminate.assert_called_once()
    assert provider._proc is None


@patch("services.ollama_service.provider.subprocess.Popen")
@patch("services.ollama_service.provider.shutil.which")
def test_stop_kill_fallback(mock_which: MagicMock, mock_popen: MagicMock) -> None:
    trace = TraceEmitter()
    provider = OllamaServiceProvider(trace, port=8080)

    mock_which.return_value = "/usr/bin/ollama"
    mock_proc = MagicMock()
    mock_proc.pid = 1234
    mock_proc.wait.side_effect = Exception("Timeout")
    mock_popen.return_value = mock_proc

    provider._proc = mock_proc
    provider.stop()

    mock_proc.terminate.assert_called_once()
    mock_proc.kill.assert_called_once()
