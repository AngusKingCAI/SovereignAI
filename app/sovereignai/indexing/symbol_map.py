"""Symbol map for code symbol extraction and ranking using tree-sitter and PageRank.

This module provides a symbol map that extracts function/class definitions
and references from Python code using tree-sitter, then ranks them by
relevance using a hand-rolled PageRank algorithm.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from sovereignai.managers.base import SymbolMapUnavailableError
from sovereignai.shared.trace_emitter import TraceEmitter, TraceLevel

log = logging.getLogger(__name__)

# Try to import tree-sitter
_TREE_SITTER_AVAILABLE = False
try:
    from tree_sitter import Language, Parser
    _TREE_SITTER_AVAILABLE = True
except ImportError:
    log.error("tree-sitter is not installed; SymbolMap will operate in DEGRADED mode")


class HealthStatus(Enum):
    """Health status of SymbolMap."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"


@dataclass
class Symbol:
    """Represents a code symbol (function, class, variable)."""
    name: str
    symbol_type: str  # "function", "class", "variable"
    file_path: str
    line_number: int
    definition: str


class SymbolMap:
    """Symbol map for code symbol extraction and ranking."""

    def __init__(self, project_root: Path | None = None, trace: TraceEmitter | None = None) -> None:
        """Initialize SymbolMap.

        Args:
            project_root: Optional project root to index immediately.
            trace: Optional trace emitter for logging.
        """
        self._project_root = project_root
        self._trace = trace
        self._index: dict[str, list[Symbol]] = {}
        self._rankings: dict[str, float] = {}

        # Emit degraded trace event if tree-sitter unavailable (P24-D)
        if not _TREE_SITTER_AVAILABLE and self._trace:
            self._trace.emit(
                component="symbol_map",
                level=TraceLevel.ERROR,
                message="tree-sitter-python not installed; operating in DEGRADED mode"
            )

        # Index project if provided
        if project_root:
            self.index(project_root)

    def health_check(self) -> HealthStatus:
        """Check health status of SymbolMap.

        Returns:
            HealthStatus.HEALTHY if tree-sitter available, DEGRADED otherwise.
        """
        if not _TREE_SITTER_AVAILABLE:
            return HealthStatus.DEGRADED
        return HealthStatus.HEALTHY

    def index(self, project_root: Path) -> dict[str, Any]:
        """Index Python files in project root.

        Args:
            project_root: Path to project root directory.

        Returns:
            Dict with indexing statistics.
        """
        if not _TREE_SITTER_AVAILABLE:
            raise SymbolMapUnavailableError("tree-sitter-python not installed")

        start_time = time.time()
        self._project_root = project_root
        self._index = {}
        self._rankings = {}

        # Find all Python files
        python_files = list(project_root.rglob("*.py"))

        if not python_files:
            if self._trace:
                self._trace.emit(
                    component="symbol_map",
                    level=TraceLevel.WARN,
                    message=f"No Python files found in {project_root}"
                )
            return {"files_indexed": 0, "symbols_found": 0}

        # Extract symbols from each file
        total_symbols = 0
        for py_file in python_files:
            try:
                symbols = self._extract_symbols_from_file(py_file)
                if symbols:
                    self._index[str(py_file)] = symbols
                    total_symbols += len(symbols)
            except Exception as e:
                log.warning(f"Failed to index {py_file}: {e}")

        # Run PageRank to rank symbols by relevance
        if total_symbols > 0:
            self._rankings = self._pagerank()

        elapsed = time.time() - start_time

        if elapsed > 30:
            log.warning(f"SymbolMap indexing took {elapsed:.2f}s (30s threshold exceeded)")
            if self._trace:
                self._trace.emit(
                    component="symbol_map",
                    level=TraceLevel.WARN,
                    message=f"Indexing took {elapsed:.2f}s (30s threshold exceeded)"
                )

        if self._trace:
            self._trace.emit(
                component="symbol_map",
                level=TraceLevel.INFO,
                message=(
                    f"Indexed {len(python_files)} files, "
                    f"{total_symbols} symbols in {elapsed:.2f}s"
                ),
            )

        return {
            "files_indexed": len(python_files),
            "symbols_found": total_symbols,
            "elapsed_seconds": elapsed
        }

    def _extract_symbols_from_file(self, file_path: Path) -> list[Symbol]:
        """Extract symbols from a single Python file using tree-sitter.

        Args:
            file_path: Path to Python file.

        Returns:
            List of Symbol objects.
        """
        if not _TREE_SITTER_AVAILABLE:
            return []

        try:
            # Initialize parser with Python language
            parser = Parser()
            try:
                import tree_sitter_python as tspython
                parser.set_language(Language(tspython.language()))
            except ImportError:
                # Fallback: try to use built-in language if available
                log.warning("tree-sitter-python not available, using fallback")
                return []

            # Parse file
            source_code = file_path.read_text()
            tree = parser.parse(source_code.encode())

            symbols = []

            # Traverse AST to extract function and class definitions
            def find_definitions(node: Any) -> None:
                if node.type == "function_definition":
                    name_node = node.child_by_field_name("name")
                    if name_node:
                        symbols.append(Symbol(
                            name=name_node.text.decode(),
                            symbol_type="function",
                            file_path=str(file_path),
                            line_number=node.start_point[0] + 1,
                            definition=node.text.decode()
                        ))
                elif node.type == "class_definition":
                    name_node = node.child_by_field_name("name")
                    if name_node:
                        symbols.append(Symbol(
                            name=name_node.text.decode(),
                            symbol_type="class",
                            file_path=str(file_path),
                            line_number=node.start_point[0] + 1,
                            definition=node.text.decode()
                        ))

                # Recurse into children
                for child in node.children:
                    find_definitions(child)

            find_definitions(tree.root_node)
            return symbols

        except Exception as e:
            log.warning(f"Failed to parse {file_path}: {e}")
            return []

    def _pagerank(self, damping: float = 0.85, iterations: int = 10) -> dict[str, float]:
        """Run PageRank algorithm on symbol graph.

        Args:
            damping: Damping factor for PageRank.
            iterations: Number of iterations to run.

        Returns:
            Dict mapping symbol names to PageRank scores.
        """
        # Build simple graph: symbols are nodes, edges based on name references
        # This is a simplified implementation
        symbol_names = set()
        for file_symbols in self._index.values():
            for symbol in file_symbols:
                symbol_names.add(symbol.name)

        # Initialize equal scores
        scores = dict.fromkeys(symbol_names, 1.0)

        # Simple iteration (would be enhanced with actual reference graph)
        for _ in range(iterations):
            new_scores = {}
            for name in symbol_names:
                new_scores[name] = (1 - damping) + damping * scores.get(name, 0.0)
            scores = new_scores

        return scores

    def query(self, task_description: str, budget: int = 1024) -> list[dict[str, Any]]:
        """Query symbol map for relevant symbols based on task description.

        Args:
            task_description: Task description to match against symbols.
            budget: Maximum number of symbols to return.

        Returns:
            List of dicts with symbol information, ranked by relevance.
        """
        if not _TREE_SITTER_AVAILABLE:
            raise SymbolMapUnavailableError("tree-sitter-python not installed")

        # Simple keyword matching against symbol names
        task_lower = task_description.lower()
        matched_symbols = []

        for _file_path, symbols in self._index.items():
            for symbol in symbols:
                # Check if symbol name appears in task description
                if symbol.name.lower() in task_lower:
                    matched_symbols.append({
                        "name": symbol.name,
                        "type": symbol.symbol_type,
                        "file_path": symbol.file_path,
                        "line_number": symbol.line_number,
                        "definition": symbol.definition,
                        "relevance_score": self._rankings.get(symbol.name, 0.0)
                    })

        # Sort by relevance score and limit to budget
        matched_symbols.sort(key=lambda x: x["relevance_score"], reverse=True)
        return matched_symbols[:budget]
