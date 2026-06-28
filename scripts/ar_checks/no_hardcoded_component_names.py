#!/usr/bin/env python3
"""Check that UI processes import only the Capability API, never core packages directly.

Enforces AR7 (AGENTS.md): web/, cli/, tui/, phone/ may not import from
orchestrator/, managers/, workers/, librarian/, adapters/, or skills/. Business
logic and routing live in core/pluggable layers, never in a UI process.
"""

import argparse
import ast
import sys
from pathlib import Path

FORBIDDEN_PACKAGES = {"orchestrator", "managers", "workers", "librarian", "adapters", "skills"}


def imported_top_level_package(node: ast.Import | ast.ImportFrom) -> set[str]:
    """Return the top-level package name(s) referenced by an import statement."""
    if isinstance(node, ast.Import):
        return {alias.name.split(".")[0] for alias in node.names}
    if isinstance(node, ast.ImportFrom) and node.module:
        return {node.module.split(".")[0]}
    return set()


def scan_file(path: Path) -> list[str]:
    """Parse one UI-layer file and flag imports from forbidden core packages."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as exc:
        return [f"{path}: SyntaxError — {exc}"]

    violations = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            hit = imported_top_level_package(node) & FORBIDDEN_PACKAGES
            if hit:
                violations.append(
                    f"{path}:{node.lineno}: imports forbidden core package(s) "
                    f"{sorted(hit)} — AR7 requires UI to consume only the Capability API"
                )
    return violations


def main() -> int:
    """Run the AR7 UI-import-boundary check over the given UI-layer paths."""
    parser = argparse.ArgumentParser(description="AR7: UI consumes Capability API only.")
    parser.add_argument("paths", nargs="+", help="UI-layer directories to check (web/, cli/, ...).")
    args = parser.parse_args()

    violations: list[str] = []
    for raw_path in args.paths:
        target = Path(raw_path)
        if not target.exists():
            continue  # Directory may not exist yet in early plans.
        files = [target] if target.is_file() else sorted(target.rglob("*.py"))
        for file_path in files:
            violations.extend(scan_file(file_path))

    if violations:
        print("AR7/AR9 violations found:", file=sys.stderr)
        for v in violations:
            print(f"  {v}", file=sys.stderr)
        return 1

    print("AR7/AR9: no forbidden UI-to-core imports found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
