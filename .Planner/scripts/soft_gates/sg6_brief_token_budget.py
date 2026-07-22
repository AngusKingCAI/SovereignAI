#!/usr/bin/env python3
"""
Soft Gate SG-6: Brief Token Budget

Warns if brief exceeds token budget (≤3000 tokens).
This is a non-blocking gate that alerts to context budget violations.
Returns exit code 0 (always passes) but outputs warning if violated.
"""

import sys
import os
from pathlib import Path

def count_tokens(text):
    """Estimate token count (rough approximation: 1 token ≈ 4 characters for English text)."""
    return len(text) // 4

def check_gate_condition():
    """
    Check that brief token count is within budget (≤3000 tokens).
    Returns True if gate passes, False otherwise (but always returns exit code 0).
    """
    # Find the most recent brief file (case-insensitive for cross-platform compatibility)
    briefs_dir = None
    for possible_dir in ["briefs", "Briefs", ".Planner/roundtable/briefs"]:
        if Path(possible_dir).exists():
            briefs_dir = Path(possible_dir)
            break
    
    if briefs_dir is None:
        print("Briefs directory not found, skipping validation")
        return True
    
    # Look for brief files
    brief_files = []
    for pattern in ["brief-*.md", "brief_*.md", "*.md"]:
        brief_files.extend(briefs_dir.glob(pattern))
    
    # Filter out non-brief files
    brief_files = [f for f in brief_files if "brief" in f.name.lower()]
    
    if not brief_files:
        print("No brief files found, skipping validation")
        return True
    
    # Get the most recently modified brief file
    latest_brief = max(brief_files, key=lambda f: f.stat().st_mtime)
    
    print(f"Validating brief: {latest_brief.name}")
    
    try:
        with open(latest_brief, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading brief file: {e}")
        return True
    
    # Count tokens
    token_count = count_tokens(content)
    token_budget = 3000  # Per Anthropic research
    word_count = len(content.split())
    
    print(f"Token count: {token_count} (budget: {token_budget})")
    print(f"Word count: {word_count}")
    
    if token_count > token_budget:
        print(f"Gate SG-6 WARN: Brief exceeds token budget ({token_count} > {token_budget})")
        print(f"   Recommendation: Reduce brief content by approximately {token_count - token_budget} tokens")
        print(f"   Context budget: Treating context as finite resource with diminishing returns per Anthropic research")
        return False
    else:
        print(f"Gate SG-6 PASS: Brief within token budget ({token_count}/{token_budget})")
        return True

def main():
    # Always return exit code 0 (soft gate never blocks)
    check_gate_condition()
    sys.exit(0)

if __name__ == "__main__":
    main()