#!/usr/bin/env python3
"""Consolidated runner for all OR-check scripts with output caching.

Runs all OR-check scripts in the scripts/or_checks directory and caches
results to skip unchanged files between runs. Cache is invalidated when
files are modified or the cache is manually cleared.
"""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

CACHE_DIR = Path(__file__).parent / ".cache"
CACHE_FILE = CACHE_DIR / "or_check_cache.json"


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
    """Run a single OR-check script and return exit code and output."""
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
    """Run all OR-check scripts with caching."""
    cache = get_cache()
    or_checks_dir = Path(__file__).parent

    scripts = sorted(or_checks_dir.glob("*.py"))
    scripts = [s for s in scripts if s.name != "run_all.py" and not s.name.startswith("_")]

    if not scripts:
        print("No OR checks defined")
        return 0

    print(f"Found {len(scripts)} OR-check scripts")
    print(f"Cache: {CACHE_FILE}")
    print()

    all_passed = True
    for script in scripts:
        exit_code, output = run_check(script, cache)
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
        print("All OR-checks passed")
        return 0
    else:
        print("Some OR-checks failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
