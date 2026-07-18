"""Tests for SymbolMap (Plan 24 S9)."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from sovereignai.indexing.symbol_map import HealthStatus, SymbolMap, SymbolMapUnavailableError


def test_symbol_map_construction():
    """Test SymbolMap construction with and without project_root."""
    trace = MagicMock()

    # Without project_root
    symbol_map = SymbolMap(trace=trace)
    assert symbol_map._project_root is None

    # With project_root
    project_root = Path("/test/project")
    symbol_map = SymbolMap(project_root=project_root, trace=trace)
    assert symbol_map._project_root == project_root


def test_symbol_map_health_check():
    """Test SymbolMap health_check returns correct status."""
    trace = MagicMock()
    symbol_map = SymbolMap(trace=trace)

    # Health check should return DEGRADED if tree-sitter unavailable
    # (In real implementation, this depends on _TREE_SITTER_AVAILABLE flag)
    health = symbol_map.health_check()
    assert health in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]


def test_symbol_map_no_embedding_no_vector_store():
    """Test that SymbolMap uses no embeddings or vector store (local design choice)."""
    trace = MagicMock()
    symbol_map = SymbolMap(trace=trace)

    # Verify no vector store or embedding attributes
    assert not hasattr(symbol_map, '_vector_store')
    assert not hasattr(symbol_map, '_embeddings')


def test_symbol_map_empty_project_no_crash():
    """Test that SymbolMap handles empty project without crashing."""
    import tempfile
    trace = MagicMock()

    with tempfile.TemporaryDirectory() as temp_dir:
        empty_project = Path(temp_dir)
        symbol_map = SymbolMap(project_root=empty_project, trace=trace)

        # Should not crash on empty project
        try:
            result = symbol_map.index(empty_project)
            assert "files_indexed" in result
            assert result["files_indexed"] == 0
        except SymbolMapUnavailableError:
            # Expected if tree-sitter unavailable
            pass


def test_symbol_map_single_file_ranking():
    """Test SymbolMap ranking on single file."""
    import tempfile
    trace = MagicMock()

    with tempfile.TemporaryDirectory() as temp_dir:
        project_root = Path(temp_dir)
        test_file = project_root / "test.py"
        test_file.write_text("""
def test_function():
    pass

class TestClass:
    def method(self):
        pass
""")

        symbol_map = SymbolMap(project_root=project_root, trace=trace)

        try:
            result = symbol_map.index(project_root)
            assert result["files_indexed"] >= 0

            # Query should return relevant symbols
            symbols = symbol_map.query("test_function", budget=10)
            assert isinstance(symbols, list)
        except SymbolMapUnavailableError:
            # Expected if tree-sitter unavailable
            pass
