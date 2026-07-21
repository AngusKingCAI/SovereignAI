#!/usr/bin/env python3
"""AR check: Enforce v1 hook caps (max 5 startup hooks, max 5 shutdown hooks)."""

import ast
import sys
from pathlib import Path


def check_hook_caps(file_path: Path) -> bool:
    """Check that hook caps are enforced correctly (max 5 for both startup and shutdown)."""
    try:
        content = file_path.read_text()
        tree = ast.parse(content)
        
        caps = {}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        if target.id in ("MAX_STARTUP_HOOKS", "MAX_SHUTDOWN_HOOKS"):
                            if isinstance(node.value, ast.Constant):
                                value = node.value.value
                                caps[target.id] = value
        
        if caps.get("MAX_STARTUP_HOOKS") != 5:
            print(f"FAIL: MAX_STARTUP_HOOKS must be 5, got {caps.get('MAX_STARTUP_HOOKS')}")
            return False
        
        if caps.get("MAX_SHUTDOWN_HOOKS") != 5:
            print(f"FAIL: MAX_SHUTDOWN_HOOKS must be 5, got {caps.get('MAX_SHUTDOWN_HOOKS')}")
            return False
        
        return True
    except Exception as e:
        print(f"ERROR: Failed to parse {file_path}: {e}")
        return False


def main():
    hooks_file = Path("app/sovereignai/lifecycle/hooks.py")
    
    if not hooks_file.exists():
        print(f"FAIL: {hooks_file} does not exist")
        return 1
    
    if check_hook_caps(hooks_file):
        print("PASS: Hook caps enforced correctly (MAX_STARTUP_HOOKS=5, MAX_SHUTDOWN_HOOKS=5)")
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
