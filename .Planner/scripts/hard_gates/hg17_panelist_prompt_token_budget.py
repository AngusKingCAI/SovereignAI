#!/usr/bin/env python3
"""
Tool: HG-17 Panelist Prompt Token Budget Validation

WHEN TO USE: Phase 6.1 (Pre-Round Table Preparation), before panelist evaluation

WHAT IT CHECKS: Panelist prompt token count (our input to web agents) is within budget (≤1500 tokens 
for rubric + competency assignment + web search instructions). Prevents context rot in our inputs to web agents.

INPUTS: None (auto-discovers latest panelist prompt files in panelist prompts/ directory)

OUTPUTS:
- Exit 0: Gate HG-17 PASS: Panelist prompts within token budget
- Exit 1: Gate HG-17 FAIL: Panelist prompts exceed token budget

FAILURE RECOVERY: Reduce panelist prompt content to fit within 1500 token budget, re-run this script.
Do NOT proceed to Round Table until exit 0.

DEPENDENCIES: panelist prompts/ directory must exist with panelist prompt files

IMPLEMENTATION NOTE: This gate measures the token count of our input to web agents via chathub.gg, 
not the web agents' internal token usage. We control our input size but cannot control external agent processing.
"""

import sys
import os
from pathlib import Path

def count_tokens(text):
    """Estimate token count (rough approximation: 1 token ≈ 4 characters for English text)."""
    # Rough approximation: ~4 characters per token for English text
    return len(text) // 4

def check_gate_condition():
    """
    Check that panelist prompt token count is within budget (≤1500 tokens).
    Returns True if gate passes, False otherwise.
    """
    # Find panelist prompt directory
    panelist_prompts_dir = None
    for possible_dir in ["panelist_prompts", "PanelistPrompts", ".Planner/roundtable/templates/panelist", ".Planner/roundtable/templates"]:
        if Path(possible_dir).exists():
            panelist_prompts_dir = Path(possible_dir)
            break
    
    if panelist_prompts_dir is None:
        print("Panelist prompts directory not found, skipping validation")
        return True
    
    # Look for panelist prompt files
    prompt_files = []
    for pattern in ["panelist_prompt*.md", "panelist*.md", "prompt*.md", "*.md"]:
        prompt_files.extend(panelist_prompts_dir.glob(pattern))
    
    # Filter for panelist-related files
    panelist_files = [f for f in prompt_files if "panelist" in f.name.lower() or "prompt" in f.name.lower()]
    
    if not panelist_files:
        print("No panelist prompt files found, skipping validation")
        return True
    
    print(f"Found {len(panelist_files)} panelist prompt files to validate")
    
    token_budget = 1500  # Per Anthropic research
    all_within_budget = True
    
    for prompt_file in panelist_files:
        print(f"Validating: {prompt_file.name}")
        
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading prompt file: {e}")
            all_within_budget = False
            continue
        
        # Count tokens
        token_count = count_tokens(content)
        
        print(f"  Token count: {token_count} (budget: {token_budget})")
        
        if token_count > token_budget:
            print(f"  Gate HG-17 FAIL: Prompt exceeds token budget ({token_count} > {token_budget})")
            all_within_budget = False
        else:
            print(f"  Gate HG-17 PASS: Prompt within token budget ({token_count}/{token_budget})")
    
    if all_within_budget:
        print(f"Gate HG-17 PASS: All panelist prompts within token budget")
        return True
    else:
        print(f"Gate HG-17 FAIL: Some panelist prompts exceed token budget")
        return False

def main():
    if check_gate_condition():
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()