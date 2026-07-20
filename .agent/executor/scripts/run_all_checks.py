#!/usr/bin/env python3
"""Unified runner for all check scripts with namespaced caching.

Runs AR, OR, Landmine, and Placeholder checks with a single unified cache.
Eliminates duplicate git state computation (3x overhead reduction) and provides
a single point of control for check execution.

Cache namespace prevents conflicts between check types while maintaining
single repo-state hash computation for performance.

Usage:
  python run_all_checks.py                    # Run all checks
  python run_all_checks.py --namespace ar    # Run only AR checks
  python run_all_checks.py --namespace or    # Run only OR checks
  python run_all_checks.py --clear-cache      # Clear all caches
"""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

# Configuration for each check namespace
CHECK_NAMESPACES = {
    "ar": {
        "dir": "ar_checks",
        "cache_file": "ar_check_cache.json",
        "skip_scripts": {
            "check_changelog.py",  # Requires plan number
            "check_plan_immutability.py",  # Requires --open-hash
            "spec_match.py",  # Requires plan file
        },
        "path_scripts": {
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
        },
        "truncate_output": True,  # Show first 3 lines, 60 chars
    },
    "or": {
        "dir": "or_checks",
        "cache_file": "or_check_cache.json",
        "skip_scripts": set(),
        "path_scripts": {},
        "truncate_output": False,  # Show full output
    },
    "landmine": {
        "dir": "landmine_checks",
        "cache_file": "landmine_check_cache.json",
        "skip_scripts": set(),
        "path_scripts": {},
        "truncate_output": False,  # Show full output
    },
    "placeholder": {
        "dir": "ar_checks",  # Placeholder check is in ar_checks directory
        "cache_file": "placeholder_check_cache.json",
        "scripts": ["check_placeholders.py"],  # Specific scripts to run
        "skip_scripts": set(),
        "path_scripts": {},
        "truncate_output": False,  # Show full output
    },
}

CACHE_DIR = Path(__file__).parent / ".cache"


def get_file_hash(file_path: Path) -> str:
    """Return SHA256 hash of file contents."""
    return hashlib.sha256(file_path.read_bytes()).hexdigest()


def get_repo_state_hash(repo_root: Path) -> str:
    """Hash of current repo state (HEAD commit + any uncommitted changes).

    Computed once and shared across all namespaces to eliminate 3x git overhead.
    Falls back to constant if git is unavailable.
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


def get_cache(namespace: str) -> dict:
    """Load cached results from disk for a specific namespace."""
    cache_file = CACHE_DIR / CHECK_NAMESPACES[namespace]["cache_file"]
    if not cache_file.exists():
        return {}
    try:
        with open(cache_file, encoding="utf-8") as f:
            return json.load(f)
    except OSError:
        return {}


def save_cache(namespace: str, cache: dict) -> None:
    """Save cached results to disk for a specific namespace."""
    CACHE_DIR.mkdir(exist_ok=True)
    cache_file = CACHE_DIR / CHECK_NAMESPACES[namespace]["cache_file"]
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)


def run_check(
    script_path: Path,
    cache: dict,
    repo_state_hash: str,
    namespace: str,
    default_args: list[str] | None = None,
) -> tuple[int, list[str]]:
    """Run a single check script and return exit code and output."""
    script_name = script_path.name
    script_hash = get_file_hash(script_path)

    # Namespaced cache key
    cache_key = f"{namespace}:{script_name}:{script_hash}:{repo_state_hash}"
    if cache_key in cache:
        print(f"[CACHED] {namespace}/{script_name} (unchanged)")
        return cache[cache_key]["exit_code"], cache[cache_key]["output"]

    print(f"[RUNNING] {namespace}/{script_name}")
    cmd = [sys.executable, str(script_path)]
    if default_args:
        cmd.extend(default_args)

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
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


def run_namespace_checks(
    namespace: str,
    repo_state_hash: str,
) -> tuple[bool, int]:
    """Run all checks for a specific namespace.
    
    Returns (all_passed, total_scripts_run).
    """
    config = CHECK_NAMESPACES[namespace]
    checks_dir = Path(__file__).parent / config["dir"]
    
    # Get scripts to run
    if "scripts" in config:
        # Explicit script list (for placeholder namespace)
        scripts = [checks_dir / script for script in config["scripts"]]
    else:
        # Auto-discover scripts
        scripts = sorted(checks_dir.glob("*.py"))
        runner_name = f"run_all_{namespace}_checks.py"
        scripts = [
            s for s in scripts
            if s.name != runner_name and not s.name.startswith("_")
        ]

    if not scripts:
        print(f"No {namespace} checks found")
        return True, 0

    print(f"Found {len(scripts)} {namespace} check scripts")
    print(f"Cache: {CACHE_DIR / config['cache_file']}")
    print()

    cache = get_cache(namespace)
    skip_scripts = config["skip_scripts"]
    path_scripts = config["path_scripts"]
    truncate_output = config["truncate_output"]

    all_passed = True
    for script in scripts:
        if script.name in skip_scripts:
            print(f"[SKIPPED] {namespace}/{script.name} (requires specific arguments)")
            continue

        default_args = None
        if script.name in path_scripts:
            default_args = path_scripts[script.name]

        exit_code, output = run_check(script, cache, repo_state_hash, namespace, default_args)
        if exit_code != 0:
            all_passed = False
            print(f"[FAILED] {namespace}/{script.name}")
            if truncate_output:
                for i, line in enumerate(output):
                    if i < 3:  # Only first 3 lines
                        print(f"  {line[:60]}")  # Truncate to 60 chars
            else:
                for line in output:
                    print(f"  {line}")
        else:
            print(f"[PASSED] {namespace}/{script.name}")

    save_cache(namespace, cache)
    return all_passed, len(scripts)


def main() -> int:
    """Run all checks with unified caching."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Unified check runner")
    parser.add_argument(
        "--namespace",
        choices=list(CHECK_NAMESPACES.keys()),
        help="Run only checks for specific namespace"
    )
    parser.add_argument(
        "--clear-cache",
        action="store_true",
        help="Clear all caches before running"
    )
    args = parser.parse_args()

    # Clear cache if requested
    if args.clear_cache:
        for namespace in CHECK_NAMESPACES:
            cache_file = CACHE_DIR / CHECK_NAMESPACES[namespace]["cache_file"]
            if cache_file.exists():
                cache_file.unlink()
                print(f"Cleared cache: {cache_file}")
        print()

    # Get repo state hash once (shared across all namespaces)
    repo_root = Path(__file__).parent.parent.parent
    repo_state_hash = get_repo_state_hash(repo_root)

    # Determine which namespaces to run
    if args.namespace:
        namespaces = [args.namespace]
    else:
        namespaces = list(CHECK_NAMESPACES.keys())

    # Run checks for each namespace
    all_passed = True
    total_scripts = 0
    for namespace in namespaces:
        print(f"=== Running {namespace.upper()} checks ===")
        namespace_passed, script_count = run_namespace_checks(namespace, repo_state_hash)
        all_passed = all_passed and namespace_passed
        total_scripts += script_count
        print()

    print(f"Total scripts run: {total_scripts}")
    if all_passed:
        print("All checks passed")
        return 0
    else:
        print("Some checks failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())