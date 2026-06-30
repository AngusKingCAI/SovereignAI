"""Tests for pull model endpoint with mocked subprocess."""
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient


def test_pull_model_subprocess_error(client: TestClient) -> None:
    """Test that pull model handles subprocess errors gracefully."""
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = Exception("Subprocess failed")
        response = client.post("/api/models/pull", json={"model": "test-org/test-model", "quant": "Q4_K_M"})
        # Should still return 200 (error handled in background thread)
        assert response.status_code == 200


def test_pull_model_with_hf_api_error(client: TestClient) -> None:
    """Test that pull model handles HF API errors."""
    with patch('urllib.request.urlopen') as mock_urlopen:
        mock_urlopen.side_effect = Exception("Network error")
        response = client.post("/api/models/pull", json={"model": "test-org/test-model", "quant": "Q4_K_M"})
        assert response.status_code == 200


def test_pull_model_no_gguf_files(client: TestClient) -> None:
    """Test that pull model handles no GGUF files case."""
    with patch('urllib.request.urlopen') as mock_urlopen:
        # Mock response with no GGUF files
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"siblings": [{"rfilename": "README.md"}]}'
        mock_urlopen.return_value.__enter__.return_value = mock_response

        response = client.post("/api/models/pull", json={"model": "test-org/test-model", "quant": "Q4_K_M"})
        assert response.status_code == 200
