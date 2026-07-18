#!/usr/bin/env python3
"""
Landmine M6 Detection: Namespace package collision — test directory shadows installed package

Checks for test directories named after installed packages (e.g., sovereignai/) that create
namespace packages that shadow app/sovereignai/, breaking isinstance() on all dataclasses/protocols.
"""

import sys
from pathlib import Path


def get_repo_root() -> Path:
    """Get repository root using git rev-parse."""
    import subprocess
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True
        )
        return Path(result.stdout.strip())
    except subprocess.CalledProcessError:
        # Fallback to current directory if not in git repo
        return Path.cwd()


def detect_m6_namespace_collision() -> int:
    """Check for test directories that shadow installed packages."""
    repo_root = get_repo_root()

    # Read pyproject.toml to get installed package names
    pyproject = repo_root / "pyproject.toml"
    if not pyproject.exists():
        print("ERROR: pyproject.toml not found")
        return 1

    # Parse pyproject.toml to get package names
    # Simple parsing for setuptools.packages.find configuration
    package_names = []
    try:
        content = pyproject.read_text()
        if "[tool.setuptools.packages.find]" in content:
            # Extract include patterns
            in_packages_section = False
            for line in content.split('\n'):
                if "[tool.setuptools.packages.find]" in line:
                    in_packages_section = True
                elif in_packages_section and line.strip().startswith('include ='):
                    # Parse include list like ["sovereignai*", "databases*", ...]
                    include_line = line.strip()
                    if '=' in include_line:
                        patterns = include_line.split('=', 1)[1].strip()
                        # Remove brackets and quotes
                        patterns = patterns.strip('[]').replace('"', '').replace("'", '')
                        for pattern in patterns.split(','):
                            pattern = pattern.strip()
                            if pattern:
                                # Extract base name from pattern
                                # (e.g., "sovereignai*" -> "sovereignai")
                                base_name = pattern.rstrip('*')
                                if base_name:
                                    package_names.append(base_name)
                elif in_packages_section and line.strip().startswith('['):
                    # End of packages section
                    break
    except Exception as e:
        print(f"WARNING: Could not parse pyproject.toml: {e}")

    if not package_names:
        print("WARNING: Could not determine package names from pyproject.toml")
        return 0

    # Check test directories for namespace collisions
    # Note: .agent/executor/tests/ is legitimate testing infrastructure and excluded
    # from M6 check per Plan 25 S2.2
    test_dirs = [
        repo_root / "tests",
    ]

    violations = []

    for test_dir in test_dirs:
        if not test_dir.exists():
            continue

        for item in test_dir.iterdir():
            if (
                item.is_dir()
                and not item.name.startswith('_')
                and not item.name.startswith('.')
                and item.name in package_names
            ):
                violations.append((item.relative_to(repo_root), item.name))

    if violations:
        print("M6 LANDMINE DETECTED: Test directory shadows installed package")
        print("Test directories named after installed packages create namespace collisions")
        print("that break isinstance() on all dataclasses/protocols")
        print()
        for dir_path, package_name in violations:
            print(f"  {dir_path} shadows package '{package_name}'")
        return 1
    else:
        print("M6 check passed: No test directory shadows installed package")
        return 0


if __name__ == "__main__":
    sys.exit(detect_m6_namespace_collision())
