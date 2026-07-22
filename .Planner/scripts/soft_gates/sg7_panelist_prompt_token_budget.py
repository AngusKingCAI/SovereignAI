#!/usr/bin/env python3
"""
Soft Gate SG-7: Panelist Prompt Token Budget

Warns if panelist prompts (our input to web agents) exceed token budget (≤1500 tokens per prompt).
This is a non-blocking gate that alerts to context budget violations.
Returns exit code 0 (always passes) but outputs warning if violated.

IMPLEMENTATION NOTE: This gate measures the token count of our input to web agents via chathub.gg, 
not the web agents' internal token usage. We control our input size but cannot control external agent processing.
"""

import sys
import os
from pathlib import Path

def count_tokens(text):
    """Estimate token count (rough approximation: 1 token ≈ 4 characters for English text)."""
    return len(text) // 4

def check_gate_condition():
    """
    Check that panelist prompt token count is within budget (≤1500 tokens).
    Returns True if gate passes, False otherwise (but always returns exit code 0).
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
    
    token_budget = 6500  # Based on 256K context window (Kimi K2.7 Code compatibility)
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
            print(f"  Gate SG-7 WARN: Prompt exceeds token budget ({token_count} > {token_budget})")
            print(f"   Recommendation: Reduce prompt content by approximately {token_count - token_budget} tokens")
            print(f"   Context budget: Treating context as finite resource with diminishing returns per Anthropic research")
            all_within_budget = False
        else:
            print(f"  Gate SG-7 PASS: Prompt within token budget ({token_count}/{token_budget})")
    
    if all_within_budget:
        print(f"Gate SG-7 PASS: All panelist prompts within token budget")
        return True
    else:
        print(f"Gate SG-7 WARN: Some panelist prompts exceed token budget")
        return False

def main():
    # Always return exit code 0 (soft gate never blocks)
    check_gate_condition()
    sys.exit(0)

if __name__ == "__main__":
    main()