from __future__ import annotations

import json
import tempfile
from pathlib import Path

from scripts.ar_checks.run_all import get_file_hash


def test_get_file_hash() -> None:
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
        f.write("test content")
        temp_path = Path(f.name)

    try:
        hash1 = get_file_hash(temp_path)
        hash2 = get_file_hash(temp_path)
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256 hex digest length
    finally:
        temp_path.unlink()


def test_cache_hash_consistency() -> None:
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
        f.write("test content")
        temp_path = Path(f.name)

    try:
        hash1 = get_file_hash(temp_path)
        # Modify file
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write("modified content")
        hash2 = get_file_hash(temp_path)
        assert hash1 != hash2
    finally:
        temp_path.unlink()
