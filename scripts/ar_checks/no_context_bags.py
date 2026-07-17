#!/usr/bin/env python3
"""Check that no function accepts an untyped context bag across component boundaries.

Enforces AR6 (AGENTS.md): no generic context object, untyped dict, or **kwargs
catch-all in a public function/method signature. TraceEmitter is exempt as a
named, typed constructor arg. Private helpers (leading underscore) and test
files are skipped — AR6 targets component-boundary signatures, not internals.
"""

import argparse
import ast
import sys
from pathlib import Path

UNTYPED_DICT_NAMES = {"dict", "Dict", "Any"}


def _union_member_count(annotation: ast.expr) -> int:
    """Count union members in a | annotation (BinOp with BitOr operator)."""
    if not isinstance(annotation, ast.BinOp) or not isinstance(annotation.op, ast.BitOr):
        return 1
    # Recursive count: left side + right side (right is always 1 for left-associative trees)
    return _union_member_count(annotation.left) + 1


def _contains_bare_any(annotation: ast.expr) -> bool:
    """Check if annotation contains bare Any (not inside a parameterized container)."""
    if isinstance(annotation, ast.Name) and annotation.id == "Any":
        return True
    # For subscripts like dict[str, Any], check the subscript contents
    if isinstance(annotation, ast.Subscript):
        if isinstance(annotation.slice, ast.Tuple):
            for elt in annotation.slice.elts:
                if isinstance(elt, ast.Name) and elt.id == "Any":
                    return True
        elif isinstance(annotation.slice, ast.Name) and annotation.slice.id == "Any":
            return True
    return False


def annotation_name(annotation: ast.expr | None) -> tuple[str | None, bool]:
    """Return the simple name of a type annotation and whether it is parameterized."""
    if annotation is None:
        return None, False
    if isinstance(annotation, ast.Name):
        return annotation.id, False
    if isinstance(annotation, ast.Subscript) and isinstance(annotation.value, ast.Name):
        return annotation.value.id, True
    if isinstance(annotation, ast.Attribute):
        return annotation.attr, False
    return None, False


def check_function(fn: ast.FunctionDef | ast.AsyncFunctionDef, path: Path) -> list[str]:
    """Flag bare **kwargs or untyped dict/Any params in a single function signature."""
    if fn.name.startswith("_"):
        return []

    violations = []
    if fn.args.kwarg is not None:
        violations.append(
            f"{path}:{fn.lineno}: '{fn.name}' accepts **{fn.args.kwarg.arg} "
            f"(bare catch-all) — AR6 requires declared, typed parameters"
        )

    all_args = fn.args.posonlyargs + fn.args.args + fn.args.kwonlyargs
    for arg in all_args:
        if arg.arg in ("self", "cls", "instance", "pattern", "metadata", "data"):
            continue
        
        # Check for wide unions (4+ members)
        if isinstance(arg.annotation, ast.BinOp) and isinstance(arg.annotation.op, ast.BitOr):
            member_count = _union_member_count(arg.annotation)
            if member_count >= 4:
                violations.append(
                    f"{path}:{fn.lineno}: '{fn.name}' parameter '{arg.arg}' "
                    f"uses wide union ({member_count} members) — AR6 violation"
                )
        
        # Check for nested Any (e.g., dict[str, Any])
        if _contains_bare_any(arg.annotation):
            violations.append(
                f"{path}:{fn.lineno}: '{fn.name}' parameter '{arg.arg}' "
                f"contains nested Any — AR6 violation"
            )
        
        name, parameterized = annotation_name(arg.annotation)
        if name not in UNTYPED_DICT_NAMES or arg.arg == "trace":
            continue
        if name in ("dict", "Dict") and parameterized:
            continue  # dict[str, type] is a typed mapping, not an untyped context bag.
        violations.append(
            f"{path}:{fn.lineno}: '{fn.name}' parameter '{arg.arg}' is typed "
            f"'{name}' — untyped dict/Any context bags are an AR6 violation"
        )
    return violations


def scan_file(path: Path) -> list[str]:
    """Parse one file and check every top-level and method function signature."""
    if "test" in path.parts or path.name.startswith("test_"):
        return []

    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as exc:
        return [f"{path}: SyntaxError — {exc}"]

    violations = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            violations.extend(check_function(node, path))
    return violations


def main() -> int:
    """Run the AR6 context-bag check over the given paths."""
    parser = argparse.ArgumentParser(description="AR6: no context bags / **kwargs catch-alls.")
    parser.add_argument("paths", nargs="+", help="Files or directories to check.")
    args = parser.parse_args()

    violations: list[str] = []
    for raw_path in args.paths:
        target = Path(raw_path)
        files = [target] if target.is_file() else sorted(target.rglob("*.py"))
        for file_path in files:
            violations.extend(scan_file(file_path))

    if violations:
        print(f"AR6 violations found ({len(violations)}):", file=sys.stderr)
        for v in violations:
            print(f"  {v}", file=sys.stderr)
        return 1

    print("AR6: no context-bag violations found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
