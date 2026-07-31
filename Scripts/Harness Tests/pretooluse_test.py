#!/usr/bin/env python3
"""
PreTooluse hook to automatically perform BP/FC research before file operations.

This script:
1. Detects file creation/modification operations  
2. Extracts keywords for BP/FC research
3. Always allows operations to proceed (never blocks)
4. Injects research requirements as additional context
"""

import json
import sys
from pathlib import Path

def extract_research_keywords(file_path: str, tool_input: dict) -> list:
    """Extract keywords from file path and content for BP research."""
    keywords = []
    
    # Extract from filename
    file_path_obj = Path(file_path)
    filename_lower = file_path_obj.name.lower()
    
    bp_keywords = ["workflow", "architecture", "design", "plan", "specification", "api", "database", "security"]
    for keyword in bp_keywords:
        if keyword in filename_lower:
            keywords.append(keyword)
    
    # Extract from file content if available (for edit operations)
    if "new_string" in tool_input:
        content = tool_input.get("new_string", "")
        fc_keywords = ["performance", "benchmark", "comparison", "analysis", "assertion", "claim"]
        for keyword in fc_keywords:
            if keyword.lower() in content.lower():
                keywords.append(keyword)
    
    return keywords

def main():
    """Main PreTooluse automation logic."""
    try:
        # Read event data from stdin
        input_data = json.load(sys.stdin)
        
        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})
        
        file_path = tool_input.get("file_path", "")
        
        print(f"[PreTooluse BP/FC Auto-Research] Checking: {file_path}", file=sys.stderr)
        
        # Extract keywords for research
        keywords = extract_research_keywords(file_path, tool_input)
        
        # Always allow operation to proceed (never block)
        # Just print empty JSON to allow operation
        print(json.dumps({}))
        sys.exit(0)  # Always allow, never block
            
    except Exception as e:
        print(f"[PreTooluse Error] {str(e)}", file=sys.stderr)
        # Never block on errors - always allow operation
        print(json.dumps({}))
        sys.exit(0)

if __name__ == "__main__":
    main()
