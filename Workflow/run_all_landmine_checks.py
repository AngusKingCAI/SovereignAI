#!/usr/bin/env python3
"""Consolidated runner for all landmine detection scripts with output caching.

Runs all landmine detection scripts in the scripts/landmine_checks directory
and caches results to skip unchanged files between runs. Cache is invalidated
when the checker script's own content changes, OR when the repo's tracked
source changes (committed or uncommitted), or when the cache is manually
cleared.

NOTE: the cache key previously included only the checker script's own
hash. That meant a checker whose own file was untouched, but whose target
source had changed, would return a stale cached PASS/FAIL. The repo-state
hash below closes that gap without requiring per-checker knowledge of
which directories it scans.
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


def get_repo_state_hash(repo_root: Path) -> str:
    """Hash of current repo state (HEAD commit + any uncommitted changes).

    Used as part of the cache key so that source changes invalidate the
    cache even when the checker script itself hasn't changed. Falls back
    to a constant if git is unavailable (cache then behaves as before,
    keyed only on checker script hash).
    """
    try:
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, cwd=repo_root,
        ).stdout.strip()
        diff = subprocess.run(
            ["git", "diff", "HEAD"],
            capture_output=True, text=True, cwd=repo_root,
        ).stdout
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, cwd=repo_root,
        ).stdout
        combined = f"{head}\n{diff}\n{status}"
        return hashlib.sha256(combined.encode("utf-8")).hexdigest()
    except Exception:
        return "no-git-state"


def get_cache() -> dict[str, str]:
    """Load cached results from disk."""
    if not CACHE_FILE.exists():
        return {}
    try:
        with open(CACHE_FILE, encoding="utf-8") as f:
            return json.load(f)  # type: ignore[no-any-return]
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
    repo_state_hash: str,
    default_args: list[str] | None = None,
) -> tuple[int, list[str]]:
    """Run a single landmine detection script and return exit code and output."""
    script_name = script_path.name
    script_hash = get_file_hash(script_path)

    cache_key = f"{script_name}:{script_hash}:{repo_state_hash}"
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
    repo_root = landmine_checks_dir.parent.parent.parent
    repo_state_hash = get_repo_state_hash(repo_root)

    scripts = sorted(landmine_checks_dir.glob("*.py"))
    scripts = [s for s in scripts if s.name != "run_all_landmine_checks.py" and not s.name.startswith("_")]

    if not scripts:
        print("No landmine detection scripts found in scripts/landmine_checks/")
        return 0

    print(f"Found {len(scripts)} landmine detection scripts")
    print(f"Cache: {CACHE_FILE}")
    print()

    # NOTE: previously mapped both scripts to `[]` (empty list). An empty
    # list is falsy in Python, so `if default_args:` below never applied it —
    # this dict had no effect. Left as an explicit empty dict now since
    # neither script is known to require default args; if either needs
    # specific arguments, add them here as a non-empty list.
    path_scripts: dict[str, list[str]] = {}

    all_passed = True
    for script in scripts:
        default_args = None
        if script.name in path_scripts:
            default_args = path_scripts[script.name]

        exit_code, output = run_check(script, cache, repo_state_hash, default_args)
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
