# Governance/GovernanceScripts/Validation/check_rule_coverage.py
# Frontmatter: id: check_rule_coverage, version: 1.0.0, owner: SovereignAI, updated: 2026-08-02, purpose: Check that every .md file is covered by at least one rule, agent: all, persona: governance
#!/usr/bin/env python3
"""Check that every .md file is covered by at least one rule."""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
GOVERNANCE_DIR = PROJECT_ROOT / "Governance"
POLICY_CARDS_DIR = PROJECT_ROOT / "Governance" / "Policy-cards"

def main():
    # Find all .md files in governance
    md_files = set()
    for md_file in GOVERNANCE_DIR.rglob("*.md"):
        if md_file.name not in ["README.md", "CHANGELOG.md"]:
            if "Docs" not in md_file.parts:
                md_files.add(md_file.relative_to(PROJECT_ROOT))
    
    # Find all policy cards and check their scope
    covered_files = set()
    for card_file in POLICY_CARDS_DIR.rglob("*.yaml"):
        import yaml
        card = yaml.safe_load(card_file.read_text())
        check_params = card.get("check", {}).get("params", {})
        
        # Check if this card covers .md files
        file_glob = check_params.get("file_glob", "")
        if "*.md" in file_glob:
            scope_dirs = check_params.get("scope_dirs", [])
            for scope_dir in scope_dirs:
                scope_path = PROJECT_ROOT / scope_dir
                if scope_path.exists():
                    for md_file in scope_path.rglob("*.md"):
                        if md_file.name not in ["README.md", "CHANGELOG.md"]:
                            if "Docs" not in md_file.parts:
                                covered_files.add(md_file.relative_to(PROJECT_ROOT))
    
    # Find uncovered files
    uncovered = md_files - covered_files
    
    if uncovered:
        print("! Governance .md files not covered by any rule:")
        for f in sorted(uncovered):
            print(f"  - {f}")
        print("\nConsider adding a Policy Card to cover these files.")
        sys.exit(1)
    
    print("All governance .md files are covered by at least one rule")
    sys.exit(0)

if __name__ == "__main__":
    main()
