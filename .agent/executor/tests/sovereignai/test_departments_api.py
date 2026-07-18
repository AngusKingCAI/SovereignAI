"""Tests for departments API endpoints (Plan 24 S9)."""
from __future__ import annotations

from app.web.schemas import DepartmentListDTO, DepartmentTaskResponseDTO, SymbolMapResponseDTO


def test_departments_list_dto():
    """Test DepartmentListDTO structure."""
    dto = DepartmentListDTO(departments=[
        {"id": "coding", "name": "Coding Manager", "description": "Test"}
    ])

    assert len(dto.departments) == 1
    assert dto.departments[0]["id"] == "coding"


def test_department_task_response_dto():
    """Test DepartmentTaskResponseDTO structure."""
    dto = DepartmentTaskResponseDTO(
        task_id="test-id",
        status="success",
        output="test output",
        error=None
    )

    assert dto.task_id == "test-id"
    assert dto.status == "success"
    assert dto.output == "test output"
    assert dto.error is None


def test_symbol_map_response_dto():
    """Test SymbolMapResponseDTO structure."""
    dto = SymbolMapResponseDTO(
        status="success",
        health="healthy",
        symbols=[{"name": "test", "type": "function"}],
        error=None
    )

    assert dto.status == "success"
    assert dto.health == "healthy"
    assert len(dto.symbols) == 1
    assert dto.error is None


def test_symbol_map_response_dto_error():
    """Test SymbolMapResponseDTO with error."""
    dto = SymbolMapResponseDTO(
        status="error",
        health="degraded",
        symbols=[],
        error="tree-sitter unavailable"
    )

    assert dto.status == "error"
    assert dto.health == "degraded"
    assert len(dto.symbols) == 0
    assert dto.error == "tree-sitter unavailable"
