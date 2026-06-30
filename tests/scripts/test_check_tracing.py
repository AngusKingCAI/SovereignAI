"""Tests for check_tracing.py static analysis tool."""
import ast
import tempfile
from pathlib import Path

from scripts.ar_checks.check_tracing import FunctionTracingAuditor, audit_directory


def test_auditor_init():
    """Test FunctionTracingAuditor initialization."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=True) as f:
        f.write("")
        f.flush()
        path = Path(f.name)
        auditor = FunctionTracingAuditor(str(path))
        assert auditor is not None
        assert auditor.functions == []


def test_auditor_respects_exempt_comment():
    """Test that auditor respects # EXEMPT-OR97 comment."""
    code = """
def do_something():  # EXEMPT-OR97
    pass
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=True) as f:
        f.write(code)
        f.flush()
        path = Path(f.name)
        auditor = FunctionTracingAuditor(str(path))
        tree = ast.parse(code)
        auditor.visit(tree)
        # Should have no functions due to exempt comment
        assert len(auditor.functions) == 0


def test_auditor_classifies_pure_functions():
    """Test that auditor classifies pure functions."""
    code = """
def add(a, b):
    return a + b
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=True) as f:
        f.write(code)
        f.flush()
        path = Path(f.name)
        auditor = FunctionTracingAuditor(str(path))
        tree = ast.parse(code)
        auditor.visit(tree)
        # Pure functions are collected but classified as PURE
        assert len(auditor.functions) == 1
        assert auditor.functions[0]['classification'] == 'PURE'


def test_audit_directory():
    """Test audit_directory function."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create a test file
        test_file = tmpdir_path / "test.py"
        test_file.write_text("""
def do_something():
    pass
""")

        violations = audit_directory(str(tmpdir_path))
        # audit_directory only scans sovereignai/, web/, skills/, adapters/
        # So it won't find violations in a temp directory
        assert isinstance(violations, list)
