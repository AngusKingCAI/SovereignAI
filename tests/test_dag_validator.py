"""Tests for the DAG validator."""
import pytest

from sovereignai.shared.dag_validator import validate_dag
from sovereignai.shared.types import DAGValidationError


def test_valid_dag_passes() -> None:
    """Verify that a valid linear DAG passes validation."""
    validate_dag(
        nodes=["node1", "node2", "node3"],
        edges=[("node1", "node2"), ("node2", "node3")],
        input_types={"node2": "type1", "node3": "type2"},
        output_types={"node1": "type1", "node2": "type2"},
    )


def test_cyclic_dag_raises() -> None:
    """Verify that a cyclic DAG raises DAGValidationError."""
    with pytest.raises(DAGValidationError, match="cycle"):
        validate_dag(
            nodes=["node1", "node2"],
            edges=[("node1", "node2"), ("node2", "node1")],
            input_types={},
            output_types={},
        )


def test_missing_input_type_raises() -> None:
    """Verify that a node requiring a missing input type raises DAGValidationError."""
    with pytest.raises(DAGValidationError, match="no node produces it"):
        validate_dag(
            nodes=["node1", "node2"],
            edges=[("node1", "node2")],
            input_types={"node2": "missing_type"},
            output_types={"node1": "type1"},
        )


def test_duplicate_output_type_raises() -> None:
    """Verify that multiple nodes producing the same type raises DAGValidationError."""
    with pytest.raises(DAGValidationError, match="produced by multiple nodes"):
        validate_dag(
            nodes=["node1", "node2"],
            edges=[],
            input_types={},
            output_types={"node1": "type1", "node2": "type1"},
        )


def test_unknown_node_in_edge_raises() -> None:
    """Verify that an edge referencing an unknown node raises DAGValidationError."""
    with pytest.raises(DAGValidationError, match="unknown node"):
        validate_dag(
            nodes=["node1"],
            edges=[("node1", "unknown_node")],
            input_types={},
            output_types={},
        )


def test_diamond_dag_passes() -> None:
    """Verify that a diamond DAG passes validation."""
    validate_dag(
        nodes=["node1", "node2", "node3", "node4"],
        edges=[("node1", "node2"), ("node1", "node3"), ("node2", "node4"), ("node3", "node4")],
        input_types={"node2": "type1", "node3": "type1", "node4": "type2"},
        output_types={"node1": "type1", "node2": "type2", "node3": "type3"},
    )
