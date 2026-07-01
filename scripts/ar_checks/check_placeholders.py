#!/usr/bin/env python3
import re
import sys
from pathlib import Path


def main():
    search_dirs = ["sovereignai", "web", "adapters", "skills", "databases", "services"]
    patterns = [r"TODO", r"FIXME", r"XXX", r"NotImplementedError", r"pass\s+#\s*placeholder"]
    
    violations = []
    
    for directory in search_dirs:
        dir_path = Path(directory)
        if not dir_path.exists():
            continue
        
        for py_file in dir_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                for pattern in patterns:
                    if re.search(pattern, content):
                        violations.append(f"{py_file}: contains {pattern}")
            except Exception:
                continue
    
    tests_dir = Path("tests")
    if tests_dir.exists():
        test_patterns = [r"NotImplementedError", r"pass\s+#\s*placeholder"]
        for py_file in tests_dir.rglob("*.py"):
            if py_file.name == "test_ar_checks.py":
                continue
            try:
                content = py_file.read_text()
                for pattern in test_patterns:
                    if re.search(pattern, content):
                        violations.append(f"{py_file}: contains {pattern}")
            except Exception:
                continue
    
    if violations:
        for v in violations:
            print(v)
        sys.exit(1)
    
    print("discovery clean")
    sys.exit(0)


if __name__ == "__main__":
    main()
