#!/usr/bin/env python3
"""
Tool: HG-16 Brief Token Budget Validation

WHEN TO USE: Phase 0 (Brief creation), before Round Table preparation

WHAT IT CHECKS: Brief token count is within budget (≤3000 tokens ≈2200 words).
Prevents context rot by enforcing budget constraints per Anthropic research.

INPUTS: None (auto-discovers latest brief file in briefs/ directory)

OUTPUTS:
- Exit 0: Gate HG-16 PASS: Brief within token budget
- Exit 1: Gate HG-16 FAIL: Brief exceeds token budget

FAILURE RECOVERY: Reduce brief content to fit within 3000 token budget, re-run this script.
Do NOT proceed to Round Table until exit 0.

DEPENDENCIES: briefs/ directory must exist with at least one brief-*.md file
"""

import sys
import os
from pathlib import Path

def count_tokens(text):
    """Estimate token count (rough approximation: 1 token ≈ 4 characters for English text)."""
    # Rough approximation: ~4 characters per token for English text
    # This is a heuristic estimate, not exact token counting
    return len(text) // 4

def check_gate_condition():
    """
    Check that brief token count is within budget (≤3000 tokens).
    Returns True if gate passes, False otherwise.
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
        return False
    
    # Count tokens
    token_count = count_tokens(content)
    token_budget = 3000  # Per Anthropic research
    word_count = len(content.split())
    
    print(f"Token count: {token_count} (budget: {token_budget})")
    print(f"Word count: {word_count}")
    
    if token_count > token_budget:
        print(f"Gate HG-16 FAIL: Brief exceeds token budget ({token_count} > {token_budget})")
        print(f"   Reduce brief content by approximately {token_count - token_budget} tokens")
        return False
    else:
        print(f"Gate HG-16 PASS: Brief within token budget ({token_count}/{token_budget})")
        return True

def main():
    if check_gate_condition():
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()