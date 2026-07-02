#!/usr/bin/env python3
import argparse
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description="Check that plan files were not modified during execution")
    parser.add_argument("--open-hash", required=True, help="Git hash at /open time")
    args = parser.parse_args()
    
    result = subprocess.run(
        ["git", "diff", "--name-only", args.open_hash, "HEAD"],
        capture_output=True,
        text=True,
    )
    
    if result.returncode != 0:
        print(f"Error running git diff: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    
    changed_files = result.stdout.strip().splitlines()
    modified_plan_files = [f for f in changed_files if f.startswith("prompts/plan-") and f.endswith(".md")]
    
    if modified_plan_files:
        print("Error: Plan files were modified during execution:", file=sys.stderr)
        for f in modified_plan_files:
            print(f"  {f}", file=sys.stderr)
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()
