from __future__ import annotations

from sovereignai.shared.types import DAGValidationError


def validate_dag(nodes: list[str], edges: list[tuple[str, str]],
                 input_types: dict[str, str],
                 output_types: dict[str, str]) -> None:
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
