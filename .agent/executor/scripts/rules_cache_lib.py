#!/usr/bin/env python3
"""Rules cache library for reading and validating cached governance rules.

Provides functions to:
- Load rules from cache with validation
- Check cache validity against source files
- Invalidate and regenerate cache when needed
- Fall back to file reads when cache is stale

Usage:
    from rules_cache_lib import get_rule_content, validate_cache, invalidate_cache_if_needed
    
    # Get rule content with automatic cache validation
    rule_text = get_rule_content("UOR-1")
    
    # Validate cache at session start
    is_valid = validate_cache()
    
    # Invalidate if governance files changed
    invalidate_cache_if_needed()
"""

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


CACHE_PATH = Path(".agent/executor/.rules-cache.json")
GOVERNANCE_FILES = [
    "AGENTS.md",
    ".agent/executor/ARCHITECTURE.md", 
    ".agent/executor/OR_RULES.md"
]

# Map file paths to cache keys (used for validation)
GOVERNANCE_FILE_KEYS = {
    "AGENTS.md": "AGENTS.md",
    ".agent/executor/ARCHITECTURE.md": "ARCHITECTURE.md",
    ".agent/executor/OR_RULES.md": "OR_RULES.md"
}


def get_file_hash(file_path: Path) -> str:
    """Calculate SHA256 hash of file contents."""
    if not file_path.exists():
        return ""
    return hashlib.sha256(file_path.read_bytes()).hexdigest()


def load_cache() -> dict[str, Any] | None:
    """Load rules cache from disk."""
    if not CACHE_PATH.exists():
        return None
    
    try:
        with open(CACHE_PATH) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def validate_cache() -> tuple[bool, str]:
    """Validate cache against current governance file hashes.
    
    Returns:
        (is_valid, message) - True if cache is up-to-date, False otherwise
    """
    cache = load_cache()
    if not cache:
        return False, "Cache file not found or invalid"
    
    # Check cache version
    if cache.get("version") != "2.0":
        return False, f"Cache version mismatch: expected 2.0, got {cache.get('version')}"
    
    # Validate each governance file hash
    governance_hashes = cache.get("governance_files", {})
    
    for file_path in GOVERNANCE_FILES:
        full_path = Path(file_path)
        if not full_path.exists():
            continue  # File might not exist in all environments
        
        current_hash = get_file_hash(full_path)
        
        # Use the proper cache key from GOVERNANCE_FILE_KEYS
        cache_key = GOVERNANCE_FILE_KEYS.get(file_path, full_path.name)
        cached_data = governance_hashes.get(cache_key)
        
        if not cached_data:
            return False, f"File {file_path} not in cache (key: {cache_key})"
        
        cached_hash = cached_data.get("hash")
        if current_hash != cached_hash:
            return False, f"File {file_path} has changed (cache stale)"
    
    return True, "Cache is valid"


def invalidate_cache_if_needed() -> bool:
    """Invalidate and regenerate cache if governance files have changed.
    
    Returns:
        True if cache was regenerated, False if cache was still valid
    """
    is_valid, message = validate_cache()
    
    if is_valid:
        return False
    
    # Cache is stale, regenerate it
    print(f"Cache invalid: {message}. Regenerating...")
    
    try:
        # Import generate_rules_cache (same directory)
        import importlib.util
        script_path = Path(__file__).parent / "generate_rules_cache.py"
        spec = importlib.util.spec_from_file_location("generate_rules_cache", script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        result = module.main()
        if result == 0:
            print("Cache regenerated successfully")
            return True
        else:
            print("Failed to regenerate cache", file=sys.stderr)
            return False
    except Exception as e:
        print(f"Error regenerating cache: {e}", file=sys.stderr)
        return False


def get_rule_content(rule_id: str) -> str | None:
    """Get rule content from cache with fallback to file read.
    
    Args:
        rule_id: Rule identifier (e.g., "UOR-1", "AR1", "INVARIANT-1")
    
    Returns:
        Rule content string, or None if not found
    """
    # Ensure cache is valid before using it
    invalidate_cache_if_needed()
    
    cache = load_cache()
    if not cache:
        return fallback_read_from_file(rule_id)
    
    rules = cache.get("rules", {})
    rule_data = rules.get(rule_id)
    
    if not rule_data:
        return fallback_read_from_file(rule_id)
    
    return rule_data.get("content")


def fallback_read_from_file(rule_id: str) -> str | None:
    """Fallback: read rule directly from governance files."""
    # Try to determine which file contains the rule based on ID pattern
    if rule_id.startswith("AR"):
        file_path = Path(".agent/executor/ARCHITECTURE.md")
    elif rule_id.startswith(("UOR-", "VOR-", "COR-", "SOR-")):
        file_path = Path(".agent/executor/OR_RULES.md")
    elif rule_id.startswith("INVARIANT-"):
        file_path = Path("AGENTS.md")
    else:
        # Try all files
        for potential_path in GOVERNANCE_FILES:
            if Path(potential_path).exists():
                file_path = Path(potential_path)
                break
        else:
            return None
    
    if not file_path.exists():
        return None
    
    try:
        content = file_path.read_text()
        
        # Simple search for the rule ID in the file
        if rule_id in content:
            # Find the rule content (simple extraction)
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if rule_id in line:
                    # Return this line and maybe the next few lines
                    rule_lines = [line.strip()]
                    j = i + 1
                    while j < len(lines) and lines[j].strip() and not lines[j].strip().startswith('#'):
                        rule_lines.append(lines[j].strip())
                        j += 1
                    return ' '.join(rule_lines)
        
        return None
    except Exception:
        return None


def get_all_rules() -> dict[str, str]:
    """Get all rules from cache as a simple dict of rule_id -> content."""
    invalidate_cache_if_needed()
    
    cache = load_cache()
    if not cache:
        return {}
    
    rules = cache.get("rules", {})
    return {rule_id: rule_data.get("content", "") for rule_id, rule_data in rules.items()}


def get_rules_by_section(section: str) -> dict[str, str]:
    """Get all rules from a specific section (e.g., "UOR", "AR")."""
    all_rules = get_all_rules()
    
    if section == "UOR":
        return {k: v for k, v in all_rules.items() if k.startswith("UOR-")}
    elif section == "AR":
        return {k: v for k, v in all_rules.items() if k.startswith("AR")}
    elif section == "VOR":
        return {k: v for k, v in all_rules.items() if k.startswith("VOR-")}
    elif section == "COR":
        return {k: v for k, v in all_rules.items() if k.startswith("COR-")}
    elif section == "SOR":
        return {k: v for k, v in all_rules.items() if k.startswith("SOR-")}
    elif section == "INVARIANT":
        return {k: v for k, v in all_rules.items() if k.startswith("INVARIANT-")}
    else:
        return {}


def main():
    """CLI interface for cache operations."""
    if len(sys.argv) < 2:
        print("Usage: rules_cache_lib.py <command> [args]")
        print("Commands:")
        print("  validate - Check if cache is valid")
        print("  invalidate - Force cache regeneration")
        print("  get <rule_id> - Get rule content")
        print("  section <section> - Get all rules from section")
        return 1
    
    command = sys.argv[1]
    
    if command == "validate":
        is_valid, message = validate_cache()
        print(f"Cache valid: {is_valid} - {message}")
        return 0 if is_valid else 1
    
    elif command == "invalidate":
        result = invalidate_cache_if_needed()
        print(f"Cache regenerated: {result}")
        return 0 if result else 1
    
    elif command == "get":
        if len(sys.argv) < 3:
            print("Usage: rules_cache_lib.py get <rule_id>")
            return 1
        rule_id = sys.argv[2]
        content = get_rule_content(rule_id)
        if content:
            print(f"{rule_id}: {content}")
            return 0
        else:
            print(f"Rule {rule_id} not found")
            return 1
    
    elif command == "section":
        if len(sys.argv) < 3:
            print("Usage: rules_cache_lib.py section <section>")
            return 1
        section = sys.argv[2]
        rules = get_rules_by_section(section)
        for rule_id, content in rules.items():
            print(f"{rule_id}: {content}")
        return 0
    
    else:
        print(f"Unknown command: {command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())