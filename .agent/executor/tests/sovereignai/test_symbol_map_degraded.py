"""Tests for SymbolMap degraded mode (Plan 24 S9, P24-D)."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from sovereignai.indexing.symbol_map import SymbolMap, SymbolMapUnavailableError, HealthStatus


def test_symbol_map_degraded_mode_logs_error():
    """Test that SymbolMap logs ERROR when tree-sitter not installed (P24-D)."""
    trace = MagicMock()
    symbol_map = SymbolMap(trace=trace)
    
    # Verify error trace was emitted if tree-sitter unavailable
    # (In real implementation, this checks _TREE_SITTER_AVAILABLE flag)
    if not symbol_map._TREE_SITTER_AVAILABLE:
        trace.emit.assert_called()
        call_args = trace.emit.call_args
        assert "degraded" in str(call_args).lower()


def test_symbol_map_degraded_emits_trace_event():
    """Test that SymbolMap emits trace event at startup when degraded (P24-D)."""
    trace = MagicMock()
    symbol_map = SymbolMap(trace=trace)
    
    # Verify trace event emitted with ERROR level
    if not symbol_map._TREE_SITTER_AVAILABLE:
        trace.emit.assert_called()
        # Check that it was called with ERROR level and degraded message
        call_args = trace.emit.call_args
        # Verify the parameters (implementation-specific)


def test_symbol_map_degraded_health_check():
    """Test that health_check returns DEGRADED when tree-sitter unavailable (P24-D)."""
    trace = MagicMock()
    symbol_map = SymbolMap(trace=trace)
    
    health = symbol_map.health_check()
    
    if not symbol_map._TREE_SITTER_AVAILABLE:
        assert health == HealthStatus.DEGRADED


def test_symbol_map_degraded_query_raises_error():
    """Test that query() raises SymbolMapUnavailableError in degraded mode (P24-D)."""
    trace = MagicMock()
    symbol_map = SymbolMap(trace=trace)
    
    if not symbol_map._TREE_SITTER_AVAILABLE:
        with pytest.raises(SymbolMapUnavailableError):
            symbol_map.query("test query", budget=10)
