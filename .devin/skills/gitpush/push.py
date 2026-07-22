#!/usr/bin/env python3
"""
Git Push Skill: Automated tagging and push

Creates semantic version tag and pushes all changes to remote repository.
Implements Gate A10: Git push blocked without user confirmation.
"""

import sys
import subprocess
import re
from pathlib import Path

def run_command(cmd, check=True, capture_output=True):
    """Run a shell command with error handling"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=capture_output,
            text=True,
            check=check
        )
        if capture_output:
            return result.stdout.strip(), result.stderr.strip()
        return None, None
    except subprocess.CalledProcessError as e:
        if capture_output:
            return e.stdout.strip(), e.stderr.strip()
        return None, str(e)

def get_current_version():
    """Get the most recent semantic version tag"""
    stdout, stderr = run_command("git tag --list 'v*'", check=False)
    if stdout:
        # Get all semantic version tags and find the most recent one
        tags = stdout.split('\n')
        if tags:
            # Sort tags and get the most recent one
            # For now, just return the last one (git tag --list returns in chronological order)
            return tags[-1]
    return "v0.0.0"  # Default if no semantic version tags exist

def increment_version(version, increment_type="patch"):
    """Increment semantic version"""
    # Remove 'v' prefix if present
    version = version.lstrip('v')
    
    # Parse version components
    match = re.match(r'(\d+)\.(\d+)\.(\d+)', version)
    if not match:
        print(f"Invalid version format: {version}")
        sys.exit(1)
    
    major, minor, patch = map(int, match.groups())
    
    # Increment based on type
    if increment_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif increment_type == "minor":
        minor += 1
        patch = 0
    else:  # patch
        patch += 1
    
    return f"v{major}.{minor}.{patch}"

def check_uncommitted_changes():
    """Check for uncommitted changes"""
    stdout, stderr = run_command("git status --porcelain")
    if stdout:
        return True
    return False

def check_remote_exists():
    """Check if git remote exists"""
    stdout, stderr = run_command("git remote", check=False)
    if stdout:
        return True
    return False

def get_current_branch():
    """Get current git branch"""
    stdout, stderr = run_command("git branch --show-current")
    return stdout if stdout else "main"

def main():
    """Main push function"""
    print("=" * 60)
    print("Git Push Skill: Automated Tagging and Push")
    print("=" * 60)
    
    # Parse arguments
    increment_type = "patch"
    
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg in ["major", "minor", "patch"]:
            increment_type = arg
        i += 1
    
    if increment_type not in ["major", "minor", "patch"]:
        print(f"[ERROR] Invalid increment type: {increment_type}")
        print("[INFO] Valid types: major, minor, patch")
        sys.exit(1)
    
    # Check for uncommitted changes
    if check_uncommitted_changes():
        print("[WARN] Uncommitted changes detected:")
        stdout, stderr = run_command("git status --short")
        print(stdout)
        print("[ERROR] Please commit changes before pushing")
        sys.exit(1)
    
    # Check if remote exists
    if not check_remote_exists():
        print("[ERROR] No git remote configured")
        sys.exit(1)
    
    # Get current branch
    current_branch = get_current_branch()
    print(f"[INFO] Current branch: {current_branch}")
    
    # Get current version
    current_version = get_current_version()
    print(f"[INFO] Current version: {current_version}")
    
    # Calculate new version
    new_version = increment_version(current_version, increment_type)
    print(f"[INFO] New version: {new_version} ({increment_type} increment)")
    
    # Get commits since last tag
    stdout, stderr = run_command(f"git log {current_version}..HEAD --oneline", check=False)
    if stdout:
        print(f"[INFO] Commits to push:")
        print(stdout)
    else:
        print("[INFO] No new commits since last tag")
    
    # Get remote name
    remote_stdout, _ = run_command("git remote")
    remote = remote_stdout.split('\n')[0] if remote_stdout else "origin"
    
    # Summary of actions
    print("\n" + "=" * 60)
    print("Push Summary")
    print("=" * 60)
    print(f"Branch: {current_branch}")
    print(f"Remote: {remote}")
    print(f"Version: {current_version} -> {new_version}")
    print(f"Tag: {new_version}")
    print("=" * 60)
    
    # User confirmation (Gate A10)
    # Always require explicit user confirmation before pushing
    is_interactive = sys.stdin.isatty()
    
    if is_interactive:
        print("\n[CONFIRM] Do you want to proceed with push? (yes/no)")
        try:
            confirmation = input().strip().lower()
        except EOFError:
            print("[ERROR] No input received, cancelling push")
            sys.exit(0)
    else:
        # Non-interactive mode not allowed per Gate A10
        print("[ERROR] Non-interactive mode not allowed for git push")
        print("[INFO] Gate A10: Git push requires explicit user confirmation")
        print("[INFO] Please run in interactive mode to confirm push")
        sys.exit(1)
    
    if confirmation not in ["yes", "y"]:
        print("[CANCELLED] Push cancelled by user")
        sys.exit(0)
    
    # Create tag
    print(f"\n[INFO] Creating tag: {new_version}")
    
    # Check if tag already exists
    stdout, stderr = run_command(f"git tag -l {new_version}", check=False)
    if stdout:
        print(f"[ERROR] Tag {new_version} already exists")
        print("[INFO] Delete existing tag first: git tag -d {new_version}")
        sys.exit(1)
    
    stdout, stderr = run_command(f'git tag -a "{new_version}" -m "Release {new_version}"')
    if stderr:
        print(f"[ERROR] Failed to create tag: {stderr}")
        sys.exit(1)
    print(f"[SUCCESS] Tag created: {new_version}")
    
    # Push commits
    print(f"\n[INFO] Pushing commits to {remote}/{current_branch}")
    stdout, stderr = run_command(f"git push {remote} {current_branch}")
    # Git push sometimes outputs to stderr even on success
    # Check if the push actually succeeded by checking the exit code
    if stderr and "error" in stderr.lower():
        print(f"[ERROR] Failed to push commits: {stderr}")
        sys.exit(1)
    print(f"[SUCCESS] Commits pushed to {remote}/{current_branch}")
    
    # Push tags
    print(f"\n[INFO] Pushing tags to {remote}")
    stdout, stderr = run_command(f"git push {remote} --tags")
    # Git push sometimes outputs to stderr even on success
    if stderr and "error" in stderr.lower():
        print(f"[ERROR] Failed to push tags: {stderr}")
        sys.exit(1)
    print(f"[SUCCESS] Tags pushed to {remote}")
    
    print("\n" + "=" * 60)
    print("[SUCCESS] Git push completed successfully")
    print(f"[INFO] Version: {new_version}")
    print(f"[INFO] Branch: {current_branch}")
    print(f"[INFO] Remote: {remote}")
    print("=" * 60)

if __name__ == "__main__":
    main()