"""Check that Orchestrator never imports ReActLoop.

Enforces architecture rule: Orchestrator should not directly import ReActLoop
as it violates the separation of concerns between the CEO-level orchestrator
and domain execution (ReActLoop is for department Workers).

AR Rule: Custom - Orchestrator separation
"""

import ast
import sys
from pathlib import Path


def check_orchestrator_no_react() -> int:
    """Check that orchestrator files don't import ReActLoop."""
    orchestrator_dir = Path("app/sovereignai/orchestrator")

    if not orchestrator_dir.exists():
        print("Orchestrator directory not found, skipping check.")
        return 0

    violations = []

    for py_file in orchestrator_dir.glob("*.py"):
        if py_file.name == "__init__.py":
            continue

        try:
            with open(py_file, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    if node.module and "react" in node.module.lower():
                        violations.append(
                            f"{py_file}: imports from {node.module}"
                        )
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        if "react" in alias.name.lower():
                            violations.append(
                                f"{py_file}: imports {alias.name}"
                            )
        except Exception as e:
            print(f"Error parsing {py_file}: {e}", file=sys.stderr)
            return 1

    if violations:
        print("Orchestrator ReActLoop import violations:", file=sys.stderr)
        for violation in violations:
            print(f"  {violation}", file=sys.stderr)
        return 1

    print("Orchestrator does not import ReActLoop.")
    return 0


if __name__ == "__main__":
    sys.exit(check_orchestrator_no_react())
