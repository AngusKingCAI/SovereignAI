#!/usr/bin/env python3
"""
Fix workflow step numbers to be sequential throughout the document.
This script reads a workflow file and renumbers all steps sequentially.
"""

import re
import sys
from pathlib import Path


def fix_workflow_step_numbers(file_path):
    """Fix step numbers in a workflow file to be sequential."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all step numbers and track current step count
    lines = content.split('\n')
    current_step = 1
    
    for i, line in enumerate(lines):
        # Match step pattern: "- {number}. " at start of line
        match = re.match(r'^-\s*(\d+)\.\s', line)
        if match:
            old_number = int(match.group(1))
            # Replace with current sequential number
            lines[i] = re.sub(r'^-\s*\d+\.\s', f'- {current_step}. ', line)
            current_step += 1
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"Fixed step numbers in {file_path}")
    print(f"Total steps renumbered: {current_step - 1}")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python fix_workflow_step_numbers.py <workflow_file>")
        sys.exit(1)
    
    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    
    fix_workflow_step_numbers(file_path)
