from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from sovereignai.shared.trace_emitter import TraceEmitter

from app.databases.base import NoCompatibleQuantError
from app.databases.hf_database.provider import HFDatabaseProvider


def test_init_no_io() -> None:
    trace = TraceEmitter()
    cache_dir = Path.home() / ".cache"
    provider = HFDatabaseProvider(trace, cache_dir)
    assert provider.name == "huggingface"
    assert provider._cache_dir == cache_dir


@patch("huggingface_hub.HfApi")
def test_list_models_cached(mock_hf_api: MagicMock) -> None:
    import os
    os.environ["SOVEREIGNAI_TEST_MODE"] = "0"

    trace = TraceEmitter()
    cache_dir = Path.home() / ".cache"
    provider = HFDatabaseProvider(trace, cache_dir)

    mock_api = MagicMock()
    mock_hf_api.return_value = mock_api

    mock_model = MagicMock()
    mock_model.modelId = "org/model"
    mock_api.list_models.return_value = [mock_model]
    mock_api.model_info.return_value = MagicMock(cardData={"num_layers": 32})

    models = provider.list_models()
    assert len(models) == 1
    assert models[0].org == "org"
    assert models[0].family == "model"

    models2 = provider.list_models()
    assert models2 is models

    os.environ["SOVEREIGNAI_TEST_MODE"] = "1"


@patch("huggingface_hub.HfApi")
def test_list_models_no_direction_param(mock_hf_api: MagicMock) -> None:
    import os
    os.environ["SOVEREIGNAI_TEST_MODE"] = "0"

    trace = TraceEmitter()
    cache_dir = Path.home() / ".cache"
    provider = HFDatabaseProvider(trace, cache_dir)

    mock_api = MagicMock()
    mock_hf_api.return_value = mock_api

    mock_model = MagicMock()
    mock_model.modelId = "org/model"
    mock_api.list_models.return_value = [mock_model]
    mock_api.model_info.return_value = MagicMock(cardData={"num_layers": 32})

    provider.list_models()

    call_args = mock_api.list_models.call_args
    assert "direction" not in call_args.kwargs
    assert call_args.kwargs["filter"] == "gguf"
    assert call_args.kwargs["sort"] == "downloads"
    assert call_args.kwargs["limit"] == 500

    os.environ["SOVEREIGNAI_TEST_MODE"] = "1"


@patch("huggingface_hub.hf_hub_download")
@patch("huggingface_hub.HfApi")
@patch("databases.hf_database.provider.os.unlink")
@patch("databases.hf_database.provider.json.dump")
@patch("builtins.open")
@patch("databases.hf_database.provider.os.close")
@patch("databases.hf_database.provider.os.replace")
@patch("databases.hf_database.provider.tempfile.mkstemp")
def test_download_model(
    mock_mkstemp: MagicMock,
    _mock_replace: MagicMock,
    _mock_close: MagicMock,
    mock_open: MagicMock,
    mock_json_dump: MagicMock,
    _mock_unlink: MagicMock,
    mock_hf_api: MagicMock,
    mock_download: MagicMock,
) -> None:
    trace = TraceEmitter()
    cache_dir = Path.home() / ".cache"
    provider = HFDatabaseProvider(trace, cache_dir)

    mock_api = MagicMock()
    mock_hf_api.return_value = mock_api

    mock_repo_info = MagicMock()
    mock_file = MagicMock()
    mock_file.rfilename = "model-q4_K_M.gguf"
    mock_repo_info.siblings = [mock_file]
    mock_api.model_info.return_value = mock_repo_info

    mock_mkstemp.return_value = (123, "/tmp/temp.json")  # nosec B108
    mock_open.return_value.__enter__.return_value = MagicMock()
    _mock_close.return_value = None

    provider.download_model("org/model")

    mock_download.assert_called_once()
    call_args = mock_download.call_args
    assert call_args.kwargs["repo_id"] == "org/model"


@patch("huggingface_hub.HfApi")
def test_no_compatible_quant_error(mock_hf_api: MagicMock) -> None:
    if not os.environ.get('SOVEREIGNAI_FULL_STACK_TESTS'):
        pytest.skip("Set SOVEREIGNAI_FULL_STACK_TESTS=1 to run")
    trace = TraceEmitter()
    cache_dir = Path.home() / ".cache"
    provider = HFDatabaseProvider(trace, cache_dir)

    mock_api = MagicMock()
    mock_hf_api.return_value = mock_api

    mock_repo_info = MagicMock()
    mock_repo_info.siblings = []
    mock_api.model_info.return_value = mock_repo_info

    with pytest.raises(NoCompatibleQuantError) as exc_info:
        provider.download_model("org/model")
    assert exc_info.value.repo_id == "org/model"


@patch("huggingface_hub.hf_hub_download")
@patch("huggingface_hub.HfApi")
@patch("databases.hf_database.provider.os.unlink")
@patch("databases.hf_database.provider.json.dump")
@patch("builtins.open")
@patch("databases.hf_database.provider.os.close")
@patch("databases.hf_database.provider.os.replace")
@patch("databases.hf_database.provider.tempfile.mkstemp")
def test_download_uses_path_home(
    mock_mkstemp: MagicMock,
    _mock_replace: MagicMock,
    mock_close: MagicMock,
    mock_open: MagicMock,
    mock_json_dump: MagicMock,
    _mock_unlink: MagicMock,
    mock_hf_api: MagicMock,
    mock_download: MagicMock,
) -> None:
    trace = TraceEmitter()
    cache_dir = Path.home() / ".cache"
    provider = HFDatabaseProvider(trace, cache_dir)

    mock_api = MagicMock()
    mock_hf_api.return_value = mock_api

    mock_repo_info = MagicMock()
    mock_file = MagicMock()
    mock_file.rfilename = "model-q4_K_M.gguf"
    mock_repo_info.siblings = [mock_file]
    mock_api.model_info.return_value = mock_repo_info

    mock_mkstemp.return_value = (123, "/tmp/temp.json")  # nosec B108
    mock_open.return_value.__enter__.return_value = MagicMock()
    mock_close.return_value = None

    provider.download_model("org/model")

    call_args = mock_download.call_args
    local_dir = call_args.kwargs["local_dir"]
    assert str(local_dir).startswith(str(Path.home()))
    assert "~" not in str(local_dir)


@patch("huggingface_hub.hf_hub_download")
@patch("huggingface_hub.HfApi")
@patch("databases.hf_database.provider.os.unlink")
@patch("databases.hf_database.provider.json.dump")
@patch("builtins.open")
@patch("databases.hf_database.provider.os.close")
@patch("databases.hf_database.provider.os.replace")
@patch("databases.hf_database.provider.tempfile.mkstemp")
def test_quant_fallback_chain(
    mock_mkstemp: MagicMock,
    _mock_replace: MagicMock,
    mock_close: MagicMock,
    mock_open: MagicMock,
    mock_json_dump: MagicMock,
    _mock_unlink: MagicMock,
    mock_hf_api: MagicMock,
    mock_download: MagicMock,
) -> None:
    trace = TraceEmitter()
    cache_dir = Path.home() / ".cache"
    provider = HFDatabaseProvider(trace, cache_dir)

    mock_api = MagicMock()
    mock_hf_api.return_value = mock_api

    mock_repo_info = MagicMock()
    mock_file1 = MagicMock()
    mock_file1.rfilename = "model-q6_K.gguf"
    mock_file2 = MagicMock()
    mock_file2.rfilename = "model-q8_0.gguf"
    mock_repo_info.siblings = [mock_file1, mock_file2]
    mock_api.model_info.return_value = mock_repo_info

    mock_mkstemp.return_value = (123, "/tmp/temp.json")  # nosec B108
    mock_open.return_value.__enter__.return_value = MagicMock()
    mock_close.return_value = None

    provider.download_model("org/model")

    call_args = mock_download.call_args
    assert call_args.kwargs["filename"] == "model-q6_K.gguf"


@patch("huggingface_hub.hf_hub_download")
@patch("huggingface_hub.HfApi")
@patch("databases.hf_database.provider.os.unlink")
@patch("databases.hf_database.provider.json.dump")
@patch("builtins.open")
@patch("databases.hf_database.provider.os.close")
@patch("databases.hf_database.provider.os.replace")
@patch("databases.hf_database.provider.tempfile.mkstemp")
def test_model_info_persistence(
    mock_mkstemp: MagicMock,
    _mock_replace: MagicMock,
    mock_close: MagicMock,
    mock_open: MagicMock,
    mock_json_dump: MagicMock,
    _mock_unlink: MagicMock,
    mock_hf_api: MagicMock,
    mock_download: MagicMock,
) -> None:
    trace = TraceEmitter()
    cache_dir = Path.home() / ".cache"
    provider = HFDatabaseProvider(trace, cache_dir)

    mock_api = MagicMock()
    mock_hf_api.return_value = mock_api

    mock_repo_info = MagicMock()
    mock_file = MagicMock()
    mock_file.rfilename = "model-q4_K_M.gguf"
    mock_repo_info.siblings = [mock_file]
    mock_api.model_info.return_value = mock_repo_info

    mock_mkstemp.return_value = (123, "/tmp/temp.json")  # nosec B108
    mock_open.return_value.__enter__.return_value = MagicMock()
    mock_close.return_value = None

    provider.download_model("org/model")

    mock_json_dump.assert_called_once()
    call_args = mock_json_dump.call_args
    data = call_args.args[0]
    assert data["model_id"] == "org/model"
    assert data["filename"] == "model-q4_K_M.gguf"
    assert data["quant"] == "q4_K_M"
    assert "downloaded_at" in data


@patch("databases.hf_database.provider.shutil.rmtree")
@patch("huggingface_hub.hf_hub_download")
@patch("huggingface_hub.HfApi")
@patch("databases.hf_database.provider.os.unlink")
@patch("databases.hf_database.provider.json.dump")
@patch("builtins.open")
@patch("databases.hf_database.provider.os.close")
@patch("databases.hf_database.provider.os.replace")
@patch("databases.hf_database.provider.tempfile.mkstemp")
def test_partial_file_cleanup_on_failure(
    mock_mkstemp: MagicMock,
    _mock_replace: MagicMock,
    mock_close: MagicMock,
    mock_open: MagicMock,
    mock_json_dump: MagicMock,
    _mock_unlink: MagicMock,
    mock_hf_api: MagicMock,
    mock_download: MagicMock,
    mock_rmtree: MagicMock,
) -> None:
    trace = TraceEmitter()
    cache_dir = Path.home() / ".cache"
    provider = HFDatabaseProvider(trace, cache_dir)

    mock_api = MagicMock()
    mock_hf_api.return_value = mock_api

    mock_repo_info = MagicMock()
    mock_file = MagicMock()
    mock_file.rfilename = "model-q4_K_M.gguf"
    mock_repo_info.siblings = [mock_file]
    mock_api.model_info.return_value = mock_repo_info

    mock_mkstemp.return_value = (123, "/tmp/temp.json")  # nosec B108
    mock_open.return_value.__enter__.return_value = MagicMock()
    mock_close.return_value = None
    mock_download.side_effect = RuntimeError("Download failed")

    with pytest.raises(RuntimeError):
        provider.download_model("org/model")

    mock_rmtree.assert_called_once()
