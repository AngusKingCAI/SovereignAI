"""Validate skill DAGs for acyclicity and type-matching before execution.

Per A6: composite skills must pass DAG validation before entering the
task state machine. Without this check, composite tasks with cycles
or type mismatches would enter the state machine and fail at runtime
(a silent failure, violating P9).

Per Q20: DAG-based execution. Each skill declares inputs (which can
be outputs of other skills). The validator checks:
  1. Acyclicity — no skill depends on its own output transitively
  2. Type-matching — every input has a producer with a matching type
"""
from __future__ import annotations

from sovereignai.shared.trace_emitter import TraceEmitter, TraceLevel
from sovereignai.shared.types import DAGValidationError

_trace = TraceEmitter()


def validate_dag(nodes: list[str], edges: list[tuple[str, str]],
                 input_types: dict[str, str],
                 output_types: dict[str, str]) -> None:
    """Check that a skill DAG is acyclic and that all input types are produced.

    Args:
        nodes: List of skill node IDs (e.g. ["open_browser", "register_email"]).
        edges: List of (source, target) pairs meaning source's output
            feeds into target's input.
        input_types: Map of node ID -> type name it requires as input.
        output_types: Map of node ID -> type name it produces as output.

    Raises:
        DAGValidationError: If the graph has a cycle or an input has no
            matching producer.
    """
    _trace.emit(
        component="dag_validator",
        level=TraceLevel.DEBUG,
        message=f"Validating DAG with {len(nodes)} nodes and {len(edges)} edges",
    )
    # 1. Type-matching: every input must have a producer with matching type
    available_types: dict[str, str] = {}  # type_name -> producer node
    for node, out_type in output_types.items():
        if out_type in available_types:
            raise DAGValidationError(
                f"Type {out_type!r} produced by multiple nodes: "
                f"{available_types[out_type]} and {node}"
            )
        available_types[out_type] = node
    for node, in_type in input_types.items():
        if in_type not in available_types:
            raise DAGValidationError(
                f"Node {node!r} requires input type {in_type!r} "
                f"but no node produces it"
            )

    # 2. Acyclicity: topological sort via Kahn's algorithm
    in_degree: dict[str, int] = dict.fromkeys(nodes, 0)
    adj: dict[str, list[str]] = {n: [] for n in nodes}
    for src, tgt in edges:
        if src not in in_degree or tgt not in in_degree:
            raise DAGValidationError(
                f"Edge ({src}, {tgt}) references unknown node"
            )
        adj[src].append(tgt)
        in_degree[tgt] += 1

    queue: list[str] = [n for n in nodes if in_degree[n] == 0]
    visited = 0
    while queue:
        node = queue.pop(0)
        visited += 1
        for neighbor in adj[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if visited != len(nodes):
        raise DAGValidationError(
            f"DAG has a cycle — visited {visited} of {len(nodes)} nodes"
        )
