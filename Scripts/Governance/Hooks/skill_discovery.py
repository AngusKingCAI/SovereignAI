#!/usr/bin/env python3
"""
Skill discovery hook for SessionStart.
Automatically discovers all skills and injects skill metadata without using model tokens.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_utils import get_verbosity, should_print, show_hook_header, show_hook_result

def discover_skills():
    """Discover available skills from .devin/skills/ directory."""
    project_root = Path("C:/SovereignAI")
    skills_dir = project_root / ".devin" / "skills"
    
    skills = {}
    
    if not skills_dir.exists():
        return skills
    
    # Scan each skill directory
    for skill_dir in skills_dir.iterdir():
        if skill_dir.is_dir():
            skill_file = skill_dir / "SKILL.md"
            
            if skill_file.exists():
                try:
                    # Read skill metadata
                    with open(skill_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.split('\n')[:20]
                    
                    # Extract metadata from frontmatter
                    metadata = {
                        "name": skill_dir.name,
                        "path": str(skill_dir.relative_to(project_root))
                    }
                    
                    for line in lines:
                        if line.startswith("---"):
                            continue
                        if line.startswith("name:"):
                            metadata["name"] = line.split(":", 1)[1].strip()
                        elif line.startswith("description:"):
                            metadata["description"] = line.split(":", 1)[1].strip()
                        elif line.startswith("argument-hint:"):
                            metadata["argument_hint"] = line.split(":", 1)[1].strip()
                    
                    skills[skill_dir.name] = metadata
                except Exception as e:
                    pass
    
    return skills

def load_agent_context(agent_name):
    """Load agent-specific context from AGENTS.md."""
    project_root = Path("C:/SovereignAI")
    agents_file = project_root / "Agents" / agent_name / "AGENTS.md"
    
    if not agents_file.exists():
        return ""
    
    try:
        with open(agents_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract key sections
        context_lines = []
        in_section = False
        target_sections = ["Purpose", "Core Philosophy", "Boundaries", "Integration Points"]
        
        for line in content.split('\n'):
            if line.startswith("## "):
                section_name = line[3:].strip()
                if section_name in target_sections:
                    in_section = True
                    context_lines.append(line)
                else:
                    in_section = False
            elif in_section:
                context_lines.append(line)
        
        return '\n'.join(context_lines[:50])  # Limit to prevent excessive context
    except:
        return ""

def main():
    """Main skill discovery logic."""
    verbosity = get_verbosity()
    show_hook_header("Skill Discovery Hook", verbosity)
    
    # Discover skills
    skills = discover_skills()
    
    if not skills:
        show_hook_result("No skills discovered", success=True, verbosity=verbosity)
        return 0
    
    # Format as additional context
    skill_context = "Available Skills:\n"
    
    for skill_name, skill_metadata in skills.items():
        skill_context += f"\n{skill_name}:\n"
        skill_context += f"  - {skill_metadata.get('description', 'No description')}\n"
        if skill_metadata.get('argument_hint'):
            skill_context += f"  - Usage: {skill_metadata['argument_hint']}\n"
        
        # Load agent context if skill corresponds to an agent
        if skill_name in ['architect', 'executor', 'planner', 'researcher', 'reviewer']:
            agent_context = load_agent_context(skill_name)
            if agent_context:
                skill_context += f"  - Agent Context:\n{agent_context}\n"
    
    # Output as additionalContext for skill access
    output = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": skill_context
        }
    }
    
    print(json.dumps(output, indent=2))
    show_hook_result(f"Discovered {len(skills)} skills", success=True, verbosity=verbosity)
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"Error in skill discovery: {e}", file=sys.stderr)
        sys.exit(1)
