# Scripts/Rules/Validation/lint_dead_references.py
# Frontmatter: id: lint_dead_references, version: 1.0.0, owner: SovereignAI, updated: 2026-08-02, purpose: Dead reference linter — flags dead .md links in governance files, agent: all, persona: governance
#!/usr/bin/env python3
"""Dead reference linter — flags dead .md links in governance files."""
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
GOVERNANCE_DIR = PROJECT_ROOT / "Rules"

def extract_markdown_links(content: str):
    """Extract all markdown links from content."""
    # Match [text](path) and [text](path "title")
    pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    return re.findall(pattern, content)

def main():
    errors = []
    
    for md_file in GOVERNANCE_DIR.rglob("*.md"):
        content = md_file.read_text()
        links = extract_markdown_links(content)
        
        for text, link in links:
            # Remove fragment identifiers and query strings
            link_path = link.split('#')[0].split('?')[0]
            
            # Skip external links
            if link_path.startswith(('http://', 'https://', 'mailto:')):
                continue
            
            # Resolve relative path
            target_path = md_file.parent / link_path
            
            # Check if file exists
            if not target_path.exists():
                errors.append(f"{md_file}: Dead link to '{link}'")
    
    if errors:
        print("X Dead references found:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    
    print("No dead references found")
    sys.exit(0)

if __name__ == "__main__":
    main()
