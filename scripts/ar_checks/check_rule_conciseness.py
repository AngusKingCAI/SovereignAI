#!/usr/bin/env python3
import re
import sys
from pathlib import Path


def main():
    agents_md = Path(__file__).parent.parent.parent / "AGENTS.md"
    
    if not agents_md.exists():
        print(f"Error: {agents_md} not found", file=sys.stderr)
        sys.exit(1)
    
    with open(agents_md, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    rule_pattern = re.compile(r"^(AR\d+|OR\d+)\. \[Mandatory\]")
    
    i = 0
    errors = []
    
    while i < len(lines):
        match = rule_pattern.match(lines[i])
        if match:
            rule_id = match.group(1)
            rule_start = i
            
            i += 1
            line_count = 1
            
            while i < len(lines) and not rule_pattern.match(lines[i]):
                if lines[i].strip() and not lines[i].strip().startswith("---"):
                    line_count += 1
                i += 1
            
            if line_count > 2:
                errors.append(f"{rule_id}: {line_count} lines (max 2)")
            
            rule_text = lines[rule_start].strip()
            char_count = len(rule_text) - len(rule_id) - 2
            if char_count > 600:
                errors.append(f"{rule_id}: {char_count} chars (hard limit 600)")
            elif char_count > 400:
                print(f"Advisory: {rule_id}: {char_count} chars (advisory limit 400)", file=sys.stderr)
        else:
            i += 1
    
    if errors:
        print("Rules exceed conciseness limits:", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()
