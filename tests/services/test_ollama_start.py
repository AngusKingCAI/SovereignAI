"""Tests for Ollama service start pre-flight check."""
from pathlib import Path
from unittest.mock import MagicMock, patch

from sovereignai.services.base import ServiceStatus
from sovereignai.services.ollama.service import OllamaService


def test_ollama_start_with_running_service() -> None:
    """Test that start() skips if service is already running."""
    mock_trace = MagicMock()
    service = OllamaService(trace=mock_trace)

    # Mock binary path exists and status to return running=True
    with patch.object(Path, 'exists', return_value=True), \
         patch.object(service, 'status', return_value=ServiceStatus(
            installed=True,
            running=True,
            version="0.1.0",
            pid=12345,
            error=None
        )):
        service.start()

        # Verify warning was emitted
        mock_trace.emit.assert_any_call(
            component="OllamaService",
            level=mock_trace.emit.call_args_list[1][1]['level'],
            message="Ollama is already running, skipping start",
        )


def test_ollama_start_with_stopped_service() -> None:
    """Test that start() proceeds if service is not running."""
    mock_trace = MagicMock()
    service = OllamaService(trace=mock_trace)

    # Mock binary path exists and status to return running=False
    with patch.object(Path, 'exists', return_value=True), \
         patch.object(service, 'status', return_value=ServiceStatus(
            installed=True,
            running=False,
            version="0.1.0",
            pid=None,
            error=None
        )), patch('subprocess.Popen') as mock_popen:
        mock_popen.return_value = MagicMock()
        service.start()

        # Verify Popen was called
        mock_popen.assert_called_once()
