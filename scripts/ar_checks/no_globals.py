#!/usr/bin/env python3
"""Check that no module declares global mutable state or mutable class defaults.

Enforces AR4 (AGENTS.md): no module-level mutable variables, no class-level
mutable defaults, no monkey-patching. Constants (UPPER_CASE names bound to an
immutable literal) and type aliases are allowed. This is a heuristic, not a
formal proof — review findings before treating them as ground truth.
"""

import argparse
import ast
import sys
from pathlib import Path

MUTABLE_LITERAL_NODES = (ast.List, ast.Dict, ast.Set, ast.ListComp, ast.DictComp, ast.SetComp)


def is_mutable_default(node: ast.AST) -> bool:
    """Return True if the given assignment value is a mutable literal expression."""
    return isinstance(node, MUTABLE_LITERAL_NODES)


def is_constant_name(name: str) -> bool:
    """Return True if the given name follows the UPPER_CASE constant convention."""
    return name.isupper() or (name.startswith("_") and name[1:].isupper())


def check_module_globals(tree: ast.Module, path: Path) -> list[str]:
    """Walk top-level assignments in a module and flag non-constant mutable globals."""
    violations = []
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            value = node.value
            for target in targets:
                if not isinstance(target, ast.Name):
                    continue
                if is_constant_name(target.id):
                    continue
                if value is not None and is_mutable_default(value):
                    violations.append(
                        f"{path}:{node.lineno}: module-level mutable global '{target.id}'"
                    )
                elif value is not None and not isinstance(
                    value,
                    (
                        ast.Constant,
                        ast.Tuple,
                        ast.Name,
                        ast.Attribute,
                        ast.Call,
                        ast.Subscript,  # type aliases, e.g. Subscriber = Callable[[Event], None]
                        ast.BinOp,      # PEP 604 union-style aliases, e.g. X | Y
                    ),
                ):
                    violations.append(
                        f"{path}:{node.lineno}: module-level variable '{target.id}' "
                        f"is not an obvious constant — review manually"
                    )
    return violations


def check_class_defaults(tree: ast.Module, path: Path) -> list[str]:
    """Walk class bodies and flag mutable literal defaults assigned as class attributes."""
    violations = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        for stmt in node.body:
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Name) and is_mutable_default(stmt.value):
                        violations.append(
                            f"{path}:{stmt.lineno}: class '{node.name}' has mutable "
                            f"class-attribute default '{target.id}'"
                        )
    return violations


def scan_file(path: Path) -> list[str]:
    """Parse one Python file and return all AR4 violations found within it."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as exc:
        return [f"{path}: SyntaxError — {exc}"]
    return check_module_globals(tree, path) + check_class_defaults(tree, path)


def main() -> int:
    """Run the AR4 global-state check over the given paths and report violations."""
    parser = argparse.ArgumentParser(description="AR4: no global mutable state.")
    parser.add_argument("paths", nargs="+", help="Files or directories to check.")
    args = parser.parse_args()

    violations: list[str] = []
    for raw_path in args.paths:
        target = Path(raw_path)
        files = [target] if target.is_file() else sorted(target.rglob("*.py"))
        for file_path in files:
            violations.extend(scan_file(file_path))

    if violations:
        print("AR4 violations found:", file=sys.stderr)
        for v in violations:
            print(f"  {v}", file=sys.stderr)
        return 1

    print("AR4: no violations found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
