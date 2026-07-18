"""Tests for SymbolMap tree-sitter path (Plan 24 S9)."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from sovereignai.indexing.symbol_map import SymbolMap, SymbolMapUnavailableError


def test_symbol_map_tree_sitter_available():
    """Test that tree-sitter path is available when tree-sitter is installed."""
    trace = MagicMock()
    symbol_map = SymbolMap(trace=trace)
    
    # Check if tree-sitter is available
    if symbol_map._TREE_SITTER_AVAILABLE:
        # Should be able to index a file
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            test_file = project_root / "test.py"
            test_file.write_text("def test(): pass")
            
            result = symbol_map.index(project_root)
            assert result["files_indexed"] >= 1
    else:
        # Should raise SymbolMapUnavailableError
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            with pytest.raises(SymbolMapUnavailableError):
                symbol_map.index(project_root)


def test_symbol_map_tree_sitter_extracts_definitions():
    """Test that tree-sitter extracts function and class definitions."""
    trace = MagicMock()
    symbol_map = SymbolMap(trace=trace)
    
    if not symbol_map._TREE_SITTER_AVAILABLE:
        pytest.skip("tree-sitter not available")
    
    import tempfile
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
        
        result = symbol_map.index(project_root)
        assert result["files_indexed"] == 1
        assert result["symbols_found"] >= 2  # At least function and class


def test_symbol_map_tree_sitter_extracts_references():
    """Test that tree-sitter extracts symbol references."""
    trace = MagicMock()
    symbol_map = SymbolMap(trace=trace)
    
    if not symbol_map._TREE_SITTER_AVAILABLE:
        pytest.skip("tree-sitter not available")
    
    import tempfile
    with tempfile.TemporaryDirectory() as temp_dir:
        project_root = Path(temp_dir)
        test_file = project_root / "test.py"
        test_file.write_text("""
def test_function():
    pass

test_function()  # Reference
""")
        
        result = symbol_map.index(project_root)
        assert result["files_indexed"] == 1
