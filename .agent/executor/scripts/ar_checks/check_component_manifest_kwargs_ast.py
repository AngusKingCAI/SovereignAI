#!/usr/bin/env python3
"""AST-based scan to reject ComponentManifest with >1 positional arg."""

import ast
import sys
from pathlib import Path


class ComponentManifestChecker(ast.NodeVisitor):
    def __init__(self):
        self.violations = []

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id == "ComponentManifest":
            positional_args = [arg for arg in node.args if not isinstance(arg, ast.Starred)]
            if len(positional_args) > 1:
                self.violations.append(
                    (node.lineno, node.col_offset, len(positional_args))
                )
        self.generic_visit(node)


def check_file(file_path: Path) -> list[tuple[int, int, int]]:
    try:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(file_path))
        checker = ComponentManifestChecker()
        checker.visit(tree)
        return checker.violations
    except Exception:
        return []


def main() -> int:
    repo_root = Path(__file__).parent.parent
    violations_found = False

    for py_file in repo_root.rglob("*.py"):
        if "vendor" in py_file.parts or ".venv" in py_file.parts:
            continue

        violations = check_file(py_file)
        if violations:
            violations_found = True
            for lineno, col_offset, arg_count in violations:
                print(
                    f"{py_file}:{lineno}:{col_offset}: "
                    f"ComponentManifest called with {arg_count} positional arguments "
                    f"(max 1 allowed)"
                )

    if violations_found:
        print(
            "\nERROR: ComponentManifest must use keyword arguments "
            "for all fields except component_id"
        )
        return 1

    print("OK: All ComponentManifest calls use keyword arguments")
    return 0


if __name__ == "__main__":
    sys.exit(main())
