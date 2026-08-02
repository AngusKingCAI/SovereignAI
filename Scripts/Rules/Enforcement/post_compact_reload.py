# Scripts/Rules/Enforcement/post_compact_reload.py
# Frontmatter: id: post_compact_reload, version: 1.0.0, owner: SovereignAI, updated: 2026-08-02, purpose: Reload constitution + rule index after context compaction, agent: all, persona: governance
#!/usr/bin/env python3
"""Reload constitution + rule index after context compaction."""
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
CONSTITUTION = PROJECT_ROOT / "Rules" / "constitution.yaml"
RULE_INDEX = PROJECT_ROOT / "Rules" / "rule-index.yaml"

def main():
    try:
        constitution = CONSTITUTION.read_text(encoding='utf-8')
        
        # Try to load rule index, fall back to minimal placeholder if not exists
        if RULE_INDEX.exists():
            rule_index = RULE_INDEX.read_text(encoding='utf-8')
        else:
            rule_index = "# Rule Index\n# Auto-generated from Policy Cards\n# Run: python \"Scripts/Rules/Validation/generate_rule_index.py\"\n"
        
        # Inject as additionalContext — this re-populates the model's context
        output = {
            "hookSpecificOutput": {
                "additionalContext": (
                    "# Constitution (reloaded after compaction)\n"
                    f"{constitution}\n\n"
                    "# Rule Index (reloaded after compaction)\n"
                    f"{rule_index}\n"
                )
            }
        }
        print(json.dumps(output))
    except Exception as e:
        # Fail gracefully — don't block the session
        print(json.dumps({"error": str(e)}))
    
    exit(0)

if __name__ == "__main__":
    main()
