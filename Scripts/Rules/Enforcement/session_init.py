# Scripts/Rules/Enforcement/session_init.py
# Frontmatter: id: session_init, version: 1.0.0, owner: SovereignAI, updated: 2026-08-02, purpose: SessionStart hook - loads constitution and rule index into context, agent: all, persona: governance
#!/usr/bin/env python3
"""
SessionStart hook - loads constitution and rule index into context.
"""
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
        
        # Inject as additionalContext
        output = {
            "hookSpecificOutput": {
                "additionalContext": (
                    "# Constitution (4-tier precedence hierarchy)\n"
                    f"{constitution}\n\n"
                    "# Rule Index (compact rule lookup)\n"
                    f"{rule_index}\n\n"
                    "# Problem-Solving Guidance\n"
                    "When facing complex problems, system integration challenges, or unexpected behavior:\n"
                    "- MUST perform web search before implementing custom solutions\n"
                    "- Consult official documentation for the relevant tool/system\n"
                    "- Look for working examples and patterns from other projects\n"
                    "- Search for known issues or limitations\n"
                    "- Verify assumptions about system behavior\n"
                    "This prevents circular problem-solving and ensures awareness of current best practices."
                )
            }
        }
        print(json.dumps(output))
    except Exception as e:
        # Fail gracefully — don't block session start
        print(json.dumps({"error": str(e)}))
    
    exit(0)

if __name__ == "__main__":
    main()
