#!/usr/bin/env python3
"""Consolidated runner for all landmine detection scripts with output caching.

Runs all landmine detection scripts in the scripts/landmine_checks directory and caches
results to skip unchanged files between runs. Cache is invalidated when
files are modified or the cache is manually cleared.
"""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

CACHE_DIR = Path(__file__).parent / ".cache"
CACHE_FILE = CACHE_DIR / "landmine_check_cache.json"


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
    """Run a single landmine detection script and return exit code and output."""
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
    """Run all landmine detection scripts with caching."""
    cache = get_cache()
    landmine_checks_dir = Path(__file__).parent

    scripts = sorted(landmine_checks_dir.glob("detect_*.py"))

    if not scripts:
        print("No landmine detection scripts found in scripts/landmine_checks/")
        print("Landmine checks not yet implemented - add detect_*.py scripts as needed")
        return 0

    print(f"Found {len(scripts)} landmine detection scripts")
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
        print("All landmine checks passed")
        return 0
    else:
        print("Some landmine checks failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
