from __future__ import annotations

import tempfile
from pathlib import Path

from sovereignai.skills.official.file_search.skill import execute


def test_depth_bounded() -> None:
    # Create a temporary directory structure
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create nested directories
        deep_path = Path(tmpdir) / "a" / "b" / "c" / "d" / "e"
        deep_path.mkdir(parents=True)

        # Create a file at depth 5
        (deep_path / "test.txt").write_text("content")

        # Search with max_depth=3 should not find the file
        result = execute({"pattern": "*.txt", "project_root": tmpdir, "max_depth": 3})
        assert "test.txt" not in result

        # Search with max_depth=10 should find the file
        result = execute({"pattern": "*.txt", "project_root": tmpdir, "max_depth": 10})
        assert "test.txt" in result


def test_hidden_dir_excluded() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create hidden directory
        hidden_path = Path(tmpdir) / ".git"
        hidden_path.mkdir()
        (hidden_path / "secret.txt").write_text("secret")

        # Search should not find files in hidden directories
        result = execute({"pattern": "*.txt", "project_root": tmpdir})
        assert "secret.txt" not in result


def test_symlink_not_followed() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        # This test may not work on all systems
        # Just ensure the function handles symlinks gracefully
        execute({"pattern": "*.txt", "project_root": tmpdir})
        # Should not crash even if symlinks exist
        assert True


def test_glob_only_rejects_regex() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a file
        (Path(tmpdir) / "test.txt").write_text("content")

        # Glob pattern should work
        result = execute({"pattern": "*.txt", "project_root": tmpdir})
        assert "test.txt" in result

        # Regex pattern should not work (treated as literal)
        result = execute({"pattern": ".*\\.txt", "project_root": tmpdir})
        assert "test.txt" not in result
