#!/usr/bin/env python3
"""Check that no constructor exceeds the AR5 argument cap.

Enforces AR5 (AGENTS.md): no constructor takes more than --max-args arguments
(excluding self/cls). Pure-DTO dataclasses (no methods besides __init__/dunder)
and main.py (Composition Root) are exempt per AR5's stated exceptions.
"""

import argparse
import ast
import sys
from pathlib import Path


def is_dataclass(node: ast.ClassDef) -> bool:
    """Return True if the class is decorated with @dataclass (any form)."""
    for dec in node.decorator_list:
        name = dec.id if isinstance(dec, ast.Name) else getattr(dec, "attr", None)
        if name == "dataclass":
            return True
    return False


def is_pure_dto(node: ast.ClassDef) -> bool:
    """Return True if a dataclass has no methods beyond dunders (i.e. no behaviour)."""
    for stmt in node.body:
        if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)) and not (
            stmt.name.startswith("__") and stmt.name.endswith("__")
        ):
            return False
    return True


def count_args(fn: ast.FunctionDef) -> int:
    """Count constructor arguments excluding self/cls and excluding *args/**kwargs flags."""
    args = fn.args
    positional = [a for a in args.posonlyargs + args.args if a.arg not in ("self", "cls")]
    kwonly = list(args.kwonlyargs)
    return len(positional) + len(kwonly)


def scan_file(path: Path, max_args: int) -> list[str]:  # EXEMPT-OR97
    """Parse one file and flag any __init__ method exceeding the constructor arg cap."""
    if path.name == "main.py":
        return []  # Composition Root exemption, AR5.

    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as exc:
        return [f"{path}: SyntaxError — {exc}"]

    violations = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        if is_dataclass(node) and is_pure_dto(node):
            continue  # Auto-generated dataclass __init__ exemption, AR5.
        for stmt in node.body:
            if isinstance(stmt, ast.FunctionDef) and stmt.name == "__init__":
                n = count_args(stmt)
                if n > max_args:
                    violations.append(
                        f"{path}:{stmt.lineno}: '{node.name}.__init__' has {n} args "
                        f"(cap is {max_args})"
                    )
    return violations


def main() -> int:  # EXEMPT-OR97
    """Run the AR5 constructor-argument-cap check over the given paths."""
    parser = argparse.ArgumentParser(description="AR5: constructor arg cap.")
    parser.add_argument("paths", nargs="+", help="Files or directories to check.")
    parser.add_argument("--max-args", type=int, default=15, help="Cap, excluding self/cls.")
    args = parser.parse_args()

    violations: list[str] = []
    for raw_path in args.paths:
        target = Path(raw_path)
        files = [target] if target.is_file() else sorted(target.rglob("*.py"))
        for file_path in files:
            violations.extend(scan_file(file_path, args.max_args))

    if violations:
        print("AR5 violations found:", file=sys.stderr)
        for v in violations:
            print(f"  {v}", file=sys.stderr)
        return 1

    print(f"AR5: no constructors exceed {args.max_args} args.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
