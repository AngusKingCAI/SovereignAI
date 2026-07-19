#!/usr/bin/env python3
"""Consolidated runner for all AR-check scripts with output caching.

Runs all AR-check scripts in the scripts/ar_checks directory and caches
results to skip unchanged files between runs. Cache is invalidated when
files are modified or the cache is manually cleared.
"""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

CACHE_DIR = Path(__file__).parent / ".cache"
CACHE_FILE = CACHE_DIR / "ar_check_cache.json"


def get_file_hash(file_path: Path) -> str:
    """Return SHA256 hash of file contents."""
    return hashlib.sha256(file_path.read_bytes()).hexdigest()


def get_cache() -> dict:
    """Load cached results from disk."""
    if not CACHE_FILE.exists():
        return {}
    try:
        with open(CACHE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except OSError:
        return {}


def save_cache(cache: dict) -> None:
    """Save cached results to disk."""
    CACHE_DIR.mkdir(exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)


def run_check(
    script_path: Path,
    cache: dict,
    default_args: list[str] | None = None,
) -> tuple[int, list[str]]:
    """Run a single AR-check script and return exit code and output."""
    script_name = script_path.name
    script_hash = get_file_hash(script_path)

    cache_key = f"{script_name}:{script_hash}"
    if cache_key in cache:
        print(f"[CACHED] {script_name} (unchanged)")
        return cache[cache_key]["exit_code"], cache[cache_key]["output"]

    print(f"[RUNNING] {script_name}")
    cmd = [sys.executable, str(script_path)]
    if default_args:
        cmd.extend(default_args)

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent.parent,
    )

    output_lines = []
    if result.stdout:
        output_lines.extend(result.stdout.splitlines())
    if result.stderr:
        output_lines.extend(result.stderr.splitlines())

    cache[cache_key] = {
        "exit_code": result.returncode,
        "output": output_lines,
    }
    return result.returncode, output_lines


def main() -> int:
    """Run all AR-check scripts with caching."""
    cache = get_cache()
    ar_checks_dir = Path(__file__).parent

    scripts = sorted(ar_checks_dir.glob("*.py"))
    scripts = [
        s for s in scripts
        if s.name != "run_all.py" and not s.name.startswith("_")
    ]

    if not scripts:
        print("No AR-check scripts found in scripts/ar_checks/")
        return 0

    print(f"Found {len(scripts)} AR-check scripts")
    print(f"Cache: {CACHE_FILE}")
    print()

    # Scripts that require specific arguments - skip in consolidated run
    # These are meant to be run in specific contexts (plan validation, etc.)
    skip_scripts = {
        "check_changelog.py",  # Requires plan number
        "check_plan_immutability.py",  # Requires --open-hash
        "spec_match.py",  # Requires plan file
    }

    # Scripts that accept path arguments - provide default paths
    path_scripts = {
        "constructor_arg_cap.py": [
            "sovereignai",
            "databases",
            "services",
            "web",
            "tui",
            "adapters",
        ],
        "no_context_bags.py": ["sovereignai"],
        "no_globals.py": ["sovereignai"],
        "no_hardcoded_component_names.py": ["web", "tui"],
    }

    all_passed = True
    for script in scripts:
        if script.name in skip_scripts:
            print(f"[SKIPPED] {script.name} (requires specific arguments)")
            continue

        default_args = None
        if script.name in path_scripts:
            default_args = path_scripts[script.name]

        exit_code, output = run_check(script, cache, default_args)
        if exit_code != 0:
            all_passed = False
            print(f"[FAILED] {script.name}")
            for line in output:
                print(f"  {line}")
        else:
            print(f"[PASSED] {script.name}")

    save_cache(cache)

    print()
    if all_passed:
        print("All AR-checks passed")
        return 0
    else:
        print("Some AR-checks failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
