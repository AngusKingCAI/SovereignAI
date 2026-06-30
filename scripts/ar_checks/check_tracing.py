"""Static check for universal tracing compliance.

Per OR97: Every function that performs work MUST emit at least one trace event.
Per OR98: Every trace event from user-initiated actions MUST carry a correlation_id.
"""
import ast
import os
import sys
from pathlib import Path


class FunctionTracingAuditor(ast.NodeVisitor):
    """Audit Python functions for tracing compliance."""

    def __init__(self, file_path: str) -> None:
        """Initialize the auditor for a file.

        Args:
            file_path: Path to the Python file being audited.
        """
        self.file_path = file_path
        self.functions: list[dict] = []
        self.current_class: str | None = None

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit a class definition."""
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit a function definition."""
        # Skip abstract methods
        if any(isinstance(d, ast.Expr) and isinstance(d.value, ast.Constant) and d.value.value is Ellipsis for d in node.body):
            self.generic_visit(node)
            return

        # Skip pass-only methods
        if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
            self.generic_visit(node)
            return

        # Check for emit calls
        has_emit = self._has_emit_call(node)
        has_trace_emitter_attr = self._has_trace_emitter_attr(node)
        has_logger_call = self._has_logger_call(node)

        # Determine classification
        classification = self._classify_function(node, has_emit, has_trace_emitter_attr, has_logger_call)

        self.functions.append({
            "file": self.file_path,
            "class": self.current_class,
            "function": node.name,
            "line": node.lineno,
            "has_emit": has_emit,
            "has_trace_emitter_attr": has_trace_emitter_attr,
            "has_logger_call": has_logger_call,
            "classification": classification,
        })
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit an async function definition."""
        self.visit_FunctionDef(node)

    def _has_emit_call(self, node: ast.FunctionDef) -> bool:
        """Check if function contains an emit() call."""
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Attribute):
                    if child.func.attr == "emit":
                        return True
        return False

    def _has_trace_emitter_attr(self, node: ast.FunctionDef) -> bool:
        """Check if function accesses trace_emitter attribute."""
        for child in ast.walk(node):
            if isinstance(child, ast.Attribute):
                if child.attr == "trace_emitter" or child.attr == "_trace":
                    return True
        return False

    def _has_logger_call(self, node: ast.FunctionDef) -> bool:
        """Check if function contains a logger call."""
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Attribute):
                    if child.func.attr in ["info", "debug", "warning", "error", "critical"]:
                        return True
        return False

    def _classify_function(
        self,
        node: ast.FunctionDef,
        has_emit: bool,
        has_trace_emitter: bool,
        has_logger: bool,
    ) -> str:
        """Classify a function by its tracing requirements.

        Returns:
            One of: MUST_TRACE, DELEGATE_ONLY, PURE, ABSTRACT, DATACLASS_INIT, PROPERTY, DUNDER_PROTOCOL
        """
        # Check for abstract
        if any(isinstance(d, ast.Expr) and isinstance(d.value, ast.Constant) and d.value.value is Ellipsis for d in node.body):
            return "ABSTRACT"

        # Check for pass-only
        if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
            return "ABSTRACT"

        # Check for dataclass __init__
        if node.name == "__init__" and self._is_dataclass_init(node):
            return "DATACLASS_INIT"

        # Check for property
        if any(isinstance(d, ast.Call) and isinstance(d.func, ast.Name) and d.func.id == "property" for d in node.decorator_list):
            return "PROPERTY"

        # Check for dunder protocol
        if node.name.startswith("__") and node.name.endswith("__"):
            return "DUNDER_PROTOCOL"

        # Check for pure function (no I/O, no side effects)
        if self._is_pure_function(node):
            return "PURE"

        # Has emit or logger - already traced
        if has_emit or has_logger:
            return "TRACED"

        # Has trace_emitter attribute - likely traced
        if has_trace_emitter:
            return "TRACED"

        # Otherwise, must trace
        return "MUST_TRACE"

    def _is_dataclass_init(self, node: ast.FunctionDef) -> bool:
        """Check if this is an auto-generated dataclass __init__."""
        # Simple heuristic: if body only has pass or docstring, likely auto-generated
        if len(node.body) <= 2:
            return True
        return False

    def _is_pure_function(self, node: ast.FunctionDef) -> bool:
        """Check if function is pure (no I/O, no side effects)."""
        # This is a simplified check - a real implementation would be more sophisticated
        # For now, assume functions with I/O patterns are not pure
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                # Check for common I/O patterns
                if isinstance(child.func, ast.Name):
                    if child.func.id in ["open", "print", "input", "exit"]:
                        return False
                if isinstance(child.func, ast.Attribute):
                    if child.func.attr in ["write", "read", "append", "extend", "insert", "remove", "pop"]:
                        return False
        return True


def audit_directory(root_dir: str) -> list[dict]:
    """Audit all Python files in a directory.

    Args:
        root_dir: Root directory to audit.

    Returns:
        List of function audit results.
    """
    results = []
    root_path = Path(root_dir)

    # Skip certain directories
    skip_dirs = {".git", "__pycache__", ".venv", "node_modules", ".pytest_cache", "build", "dist"}

    for py_file in root_path.rglob("*.py"):
        # Skip files in skip directories
        if any(skip_dir in py_file.parts for skip_dir in skip_dirs):
            continue

        try:
            with open(py_file, encoding="utf-8") as f:
                source = f.read()
            tree = ast.parse(source, filename=str(py_file))
            auditor = FunctionTracingAuditor(str(py_file))
            auditor.visit(tree)
            results.extend(auditor.functions)
        except Exception as e:
            print(f"Error auditing {py_file}: {e}", file=sys.stderr)

    return results


def main() -> int:
    """Run the tracing audit and report violations."""
    # Audit sovereignai/ directory
    results = audit_directory("sovereignai")

    # Also audit web/, cli/, tui/, scripts/, phone/, adapters/, skills/
    for dir_name in ["web", "cli", "tui", "scripts", "phone", "adapters", "skills"]:
        if os.path.exists(dir_name):
            results.extend(audit_directory(dir_name))

    # Write CSV output
    csv_path = "temp/tracing_audit.csv"
    os.makedirs("temp", exist_ok=True)
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("file,class,function,line,has_emit,has_trace_emitter_attr,has_logger_call,classification\n")
        for func in results:
            f.write(
                f"{func['file']},{func['class'] or ''},{func['function']},"
                f"{func['line']},{func['has_emit']},{func['has_trace_emitter_attr']},"
                f"{func['has_logger_call']},{func['classification']}\n"
            )
    print(f"Audit results written to {csv_path}")

    # Filter for MUST_TRACE and DELEGATE_ONLY functions without emits
    violations = []
    for func in results:
        if func["classification"] in ["MUST_TRACE"] and not func["has_emit"]:
            violations.append(func)

    # Report violations
    if violations:
        print(f"Found {len(violations)} tracing violations:", file=sys.stderr)
        for func in violations:
            print(
                f"  {func['file']}:{func['line']} - {func['class']}.{func['function'] if func['class'] else func['function']}",
                file=sys.stderr,
            )
        return 1
    else:
        print("No tracing violations found.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
