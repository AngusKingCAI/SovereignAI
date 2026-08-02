# Scripts/Rules/Validation/validate_frontmatter.py
# Frontmatter: id: validate_frontmatter, version: 1.0.0, owner: SovereignAI, updated: 2026-08-02, purpose: Validate YAML frontmatter on governance .md files, agent: all, persona: governance
#!/usr/bin/env python3
"""Validate YAML frontmatter on governance .md files."""
import sys
import yaml
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
GOVERNANCE_DIRS = [
    PROJECT_ROOT / ".devin" / "agents",
    PROJECT_ROOT / "Rules",
    PROJECT_ROOT / "workflows"
]

def validate_frontmatter(file_path: Path):
    """Validate frontmatter in a single file."""
    content = file_path.read_text()
    
    if not content.startswith("---"):
        return False, "No YAML frontmatter found (file must start with ---)"
    
    parts = content.split("---", 2)
    if len(parts) < 2:
        return False, "Invalid frontmatter format"
    
    try:
        frontmatter = yaml.safe_load(parts[1])
        if frontmatter is None:
            return False, "Empty frontmatter"
        
        # Check for required fields (basic check)
        required_fields = ["id", "version", "purpose"]
        missing = [f for f in required_fields if f not in frontmatter]
        if missing:
            return False, f"Missing required fields: {', '.join(missing)}"
        
        return True, "Valid"
    except yaml.YAMLError as e:
        return False, f"YAML parsing error: {e}"

def main():
    errors = []
    
    for gov_dir in GOVERNANCE_DIRS:
        if not gov_dir.exists():
            continue
        
        for md_file in gov_dir.rglob("*.md"):
            # Skip exempt files
            if md_file.name in ["README.md", "CHANGELOG.md"]:
                continue
            if "Docs" in md_file.parts:
                continue
            
            valid, message = validate_frontmatter(md_file)
            if not valid:
                errors.append(f"{md_file}: {message}")
    
    if errors:
        print("X Frontmatter validation failed:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    
    print("All governance .md files have valid frontmatter")
    sys.exit(0)

if __name__ == "__main__":
    main()
