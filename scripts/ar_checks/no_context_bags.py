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


def check_function(fn: ast.FunctionDef | ast.AsyncFunctionDef, path: Path) -> list[str]:  # EXEMPT-OR97
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
        if arg.arg in ("self", "cls"):
            continue
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


def scan_file(path: Path) -> list[str]:  # EXEMPT-OR97
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


def main() -> int:  # EXEMPT-OR97
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
        print("AR6 violations found:", file=sys.stderr)
        for v in violations:
            print(f"  {v}", file=sys.stderr)
        return 1

    print("AR6: no context-bag violations found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
