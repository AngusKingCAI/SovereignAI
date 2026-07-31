#!/usr/bin/env python3
"""
Rule-agnostic PostToolUse hook to detect rule violations by dynamically parsing agent rules.

This script:
1. Reads current agent's rules file from .devin/rules/{agent}.md
2. Parses rules to extract file-based violation patterns
3. Dynamically creates violation checks based on rule content
4. Returns violations for user decision via additionalContext
"""

import json
import sys
import re
from pathlib import Path
from typing import Dict, List, Callable


class RuleParser:
    """Parse agent rules files to extract checkable violation patterns."""
    
    def __init__(self, rules_file_path: str):
        self.rules_file_path = Path(rules_file_path)
        self.rules_content = self._read_rules_file()
        self.violation_patterns = self._extract_violation_patterns()
    
    def _read_rules_file(self) -> str:
        """Read the agent rules file."""
        if not self.rules_file_path.exists():
            return ""
        with open(self.rules_file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _extract_violation_patterns(self) -> List[Dict]:
        """Extract file-based violation patterns from rules content."""
        patterns = []
        
        # Pattern matching for file-based violations
        violation_patterns = [
            # Simple rule patterns matching the simplified rules
            (r"No index\.md", "index_files",
             self._check_index_files),
            
            (r"No files in App/", "app_directory",
             self._check_app_directory),
            
            (r"Docs/ → Docs/Category/", "docs_categorization",
             self._check_categorization),
            
            (r"Scripts/ → Scripts/Category/", "scripts_categorization",
             self._check_script_placement),
            
            # BP and FC violations (content-based detection)
            (r"BP research", "bp_violation",
             self._check_bp_violation),
            
            (r"FC research", "fc_violation",
             self._check_fc_violation),
        ]
        
        for pattern, violation_type, check_func in violation_patterns:
            if re.search(pattern, self.rules_content, re.IGNORECASE):
                patterns.append({
                    "type": violation_type,
                    "pattern": pattern,
                    "check_func": check_func
                })
        
        return patterns
    
    def _check_index_files(self, file_path: str, tool_input: dict = None) -> Dict:
        """Check for index.md violations."""
        file_path_obj = Path(file_path)
        file_name = file_path_obj.name.lower()
        
        if "index.md" in file_name:
            allowed_locations = ["logs/", "logs/.archived/"]
            file_str = str(file_path_obj).lower()
            
            if not any(loc in file_str for loc in allowed_locations):
                return {
                    "type": "SSOT Violation",
                    "rule": "Never create index.md files",
                    "file": file_path,
                    "description": "index.md files violate SSOT principles. Use STRUCTURE.md as the single source of truth."
                }
        return None
    
    def _check_app_directory(self, file_path: str, tool_input: dict = None) -> Dict:
        """Check for App/ directory violations."""
        if "App/" in file_path or "/App/" in file_path:
            return {
                "type": "Architectural Boundaries Violation",
                "rule": "Never reference or modify App/ directory",
                "file": file_path,
                "description": "App/ directory is for application code only. Architect agent should not modify files in App/ to prevent scope creep into implementation."
            }
        return None
    
    def _check_documentation_files(self, file_path: str, tool_input: dict = None) -> Dict:
        """Check for documentation file violations."""
        file_path_obj = Path(file_path)
        file_name = file_path_obj.name.lower()
        
        doc_files = ["readme.md", "changelog.md", "contributing.md", "license.md"]
        if any(doc in file_name for doc in doc_files):
            return {
                "type": "Documentation Violation",
                "rule": "Never create documentation files unless specifically requested",
                "file": file_path,
                "description": "Documentation files should only be created when specifically requested by the user."
            }
        return None
    
    def _check_categorization(self, file_path: str, tool_input: dict = None) -> Dict:
        """Check for file categorization violations with infrastructure exemptions."""
        file_path_obj = Path(file_path)
        path_parts = file_path_obj.parts
        
        # Infrastructure exemptions (like session state, cache directories)
        exempt_infrastructure_dirs = [".cache", ".session_state", ".git", "__pycache__"]
        exempt_final_dirs = [".devin/rules", ".devin/skills"]  # Directories that are final destinations
        exempt_config_files = ["hooks.v1.json", "config.json", "config.local.json"]  # Config files in .devin/ root
        
        # Check if file is in an exempt infrastructure directory
        file_str = str(file_path_obj)
        if any(exempt_dir in file_str for exempt_dir in exempt_infrastructure_dirs):
            return None
        
        # Check if file is in an exempt final directory
        if any(exempt_dir in file_str for exempt_dir in exempt_final_dirs):
            return None
        
        # Check if file is an exempt config file in .devin/ root
        file_name = file_path_obj.name
        if file_name in exempt_config_files and ".devin" in file_str:
            return None
        
        # Only check Docs/ directory for categorization (be more specific)
        categorization_required_dirs = ["Docs"]
        
        for i, part in enumerate(path_parts):
            if part in categorization_required_dirs:
                # Check if file is placed directly in the categorization directory
                if i + 1 < len(path_parts) and "." in path_parts[i + 1]:
                    return {
                        "type": "File Categorization Violation",
                        "rule": "Docs Categorization: Files in Docs/ must be placed in appropriate subdirectories",
                        "file": file_path,
                        "description": f"Files in Docs/ must be placed in appropriate category subdirectories (Code/, Design Docs/, etc.)."
                    }
        return None
    
    def _check_script_placement(self, file_path: str, tool_input: dict = None) -> Dict:
        """Check for script placement violations with infrastructure exemptions."""
        file_path_obj = Path(file_path)
        path_parts = file_path_obj.parts
        
        # Infrastructure exemptions
        exempt_infrastructure_dirs = [".cache", ".session_state", ".git", "__pycache__"]
        file_str = str(file_path_obj)
        
        # Check if file is in an exempt infrastructure directory
        if any(exempt_dir in file_str for exempt_dir in exempt_infrastructure_dirs):
            return None
        
        # Check if script is directly in Scripts/ without category subdirectory
        if "Scripts" in path_parts:
            scripts_index = path_parts.index("Scripts")
            if scripts_index + 1 < len(path_parts):
                next_part = path_parts[scripts_index + 1]
                # If next part is a file (has extension) instead of a directory
                # and it's not an infrastructure file
                if "." in next_part and not any(exempt_dir in next_part for exempt_dir in exempt_infrastructure_dirs):
                    return {
                        "type": "Script Placement Violation",
                        "rule": "Scripts Categorization: Scripts must be placed in Scripts/<Category>/ matching primary function",
                        "file": file_path,
                        "description": "Scripts must be placed in appropriate category subdirectories under Scripts/."
                    }
        return None
    
    def _check_test_placement(self, file_path: str, tool_input: dict = None) -> Dict:
        """Check for test placement violations."""
        file_path_obj = Path(file_path)
        file_name = file_path_obj.name.lower()
        
        if "test" in file_name and ("App/" in file_path or "/App/" in file_path):
            return {
                "type": "Test Placement Violation",
                "rule": "Place IDE harness tests in Scripts/Harness Tests/ folder only",
                "file": file_path,
                "description": "Test files should be in Scripts/Harness Tests/, not App/ directory."
            }
        return None
    
    def _check_log_placement(self, file_path: str, tool_input: dict = None) -> Dict:
        """Check for log placement violations."""
        file_path_obj = Path(file_path)
        path_parts = file_path_obj.parts
        
        if "Logs" in path_parts:
            logs_index = path_parts.index("Logs")
            # Check if file is directly in Logs/ without agent subdirectory
            if logs_index + 1 < len(path_parts):
                next_part = path_parts[logs_index + 1]
                # If next part is a file (has extension) instead of an agent directory
                if "." in next_part:
                    return {
                        "type": "Log Placement Violation",
                        "rule": "Never create log folders at Logs/ root level without agent context",
                        "file": file_path,
                        "description": "Log files must be placed in agent-specific subdirectories (Logs/{Agent}/)."
                    }
        return None
    
    def _check_yaml_frontmatter(self, file_path: str, tool_input: dict = None) -> Dict:
        """Check for YAML frontmatter violations in governance files."""
        file_path_obj = Path(file_path)
        
        # Check if file is in a governance directory
        governance_dirs = ["Workflow", ".devin", "rules"]
        is_governance_file = any(dir in str(file_path_obj) for dir in governance_dirs)
        
        if is_governance_file and file_path_obj.suffix in [".md", ".yaml", ".yml"]:
            try:
                with open(file_path_obj, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Check if file has YAML frontmatter (starts with ---)
                    if not content.startswith("---"):
                        return {
                            "type": "YAML Frontmatter Violation",
                            "rule": "When creating governance files, add appropriate YAML frontmatter",
                            "file": file_path,
                            "description": "Governance files must include YAML frontmatter with required fields (id, status, owner, updated, purpose)."
                        }
            except Exception:
                pass  # If we can't read the file, skip this check
        return None
    
    def _check_bp_violation(self, file_path: str, tool_input: dict = None) -> Dict:
        """Check for BP violations - content analysis for research indicators."""
        file_path_obj = Path(file_path)
        
        # Check if file exists and analyze content
        if not file_path_obj.exists():
            return None
            
        try:
            with open(file_path_obj, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Content-based indicators that BP research was performed
            bp_indicators = [
                "BP research", "best practice", "industry standard", "web search",
                "research context", "based on research", "according to best practices",
                "industry best practices", "current standards", "established practices"
            ]
            
            # Check if content contains BP research indicators
            has_bp_research = any(indicator.lower() in content.lower() for indicator in bp_indicators)
            
            # Check if content makes technical/architectural claims without research
            # Look for decision-making language without research context
            technical_claim_patterns = [
                r"(should|must|will|shall).+(implement|use|adopt|follow)",
                r"(decision|choice|approach|method).+(without|except)",
                r"(best|optimal|recommended).+(approach|method|solution)"
            ]
            
            import re
            has_technical_claims = any(re.search(pattern, content, re.IGNORECASE) for pattern in technical_claim_patterns)
            
            # If there are technical claims but no BP research indicators, flag violation
            if has_technical_claims and not has_bp_research:
                return {
                    "type": "Best Practice Violation",
                    "rule": "Never implement major architectural decisions or create files/sections without first performing web search (BP?)",
                    "file": file_path,
                    "description": "This section contains technical claims or architectural decisions without evidence of BP research. Add research context using terms like 'BP research' or 'industry standards'."
                }
                
        except Exception:
            pass  # If we can't read the file, skip this check
            
        return None
    
    def _check_fc_violation(self, file_path: str, tool_input: dict = None) -> Dict:
        """Check for FC violations - content analysis for fact-checking indicators."""
        file_path_obj = Path(file_path)
        
        # Check if file exists and analyze content
        if not file_path_obj.exists():
            return None
            
        try:
            with open(file_path_obj, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Content-based indicators that FC research was performed
            fc_indicators = [
                "FC research", "fact check", "verified", "confirmed", "validated",
                "fact-checked", "verified against", "confirmed by", "validated using",
                "according to", "based on data", "evidence shows", "data indicates"
            ]
            
            # Check if content contains FC research indicators
            has_fc_research = any(indicator.lower() in content.lower() for indicator in fc_indicators)
            
            # Check if content makes factual claims without verification
            # Look for assertion language without fact-checking context
            factual_claim_patterns = [
                r"(shows|demonstrates|proves|indicates|reveals).+(improvement|increase|decrease|better|worse)",
                r"(performance|speed|efficiency|reliability).+(improved|increased|decreased|enhanced)",
                r"(benchmark|comparison|analysis).+(shows|demonstrates|indicates)",
                r"\d+%.+(improvement|increase|decrease|faster|slower)"
            ]
            
            import re
            has_factual_claims = any(re.search(pattern, content, re.IGNORECASE) for pattern in factual_claim_patterns)
            
            # If there are factual claims but no FC research indicators, flag violation
            if has_factual_claims and not has_fc_research:
                return {
                    "type": "Fact Check Violation",
                    "rule": "Never proceed with statements, claims, or technical assertions without first performing fact checking (FC?)",
                    "file": file_path,
                    "description": "This section contains factual claims or performance assertions without evidence of fact checking. Add verification context using terms like 'FC research' or 'verified'."
                }
                
        except Exception:
            pass  # If we can't read the file, skip this check
            
        return None
    
    def _check_whole_file_creation(self, file_path: str, tool_input: dict = None) -> Dict:
        """Check for whole file creation violations."""
        if tool_input is None:
            return None
            
        # Check if this is a write operation (new file creation)
        # For write operations, check if the content is substantial (whole file)
        file_content = tool_input.get("content", "")
        
        # If content is long and comprehensive, it's likely a whole file creation
        if len(file_content) > 500:  # Threshold for "whole file" vs "section"
            return {
                "type": "Whole File Creation Violation",
                "rule": "Never create whole files - always create section by section",
                "file": file_path,
                "description": "File content appears to be a complete file rather than a section. Create files section by section to enable incremental BP/FC validation."
            }
        return None
    
    def _check_whole_file_modification(self, file_path: str, tool_input: dict = None) -> Dict:
        """Check for whole file modification violations."""
        if tool_input is None:
            return None
            
        # Check if this is an edit operation
        # For edit operations, check if it's editing the entire file
        old_string = tool_input.get("old_string", "")
        new_string = tool_input.get("new_string", "")
        
        # If editing large portions, it's likely whole file modification
        if len(old_string) > 500 and len(new_string) > 500:
            return {
                "type": "Whole File Modification Violation",
                "rule": "Never modify whole files - always modify section by section",
                "file": file_path,
                "description": "Edit operation appears to modify the entire file rather than a section. Modify files section by section to enable incremental BP/FC validation."
            }
        return None
    
    def check_violations(self, file_path: str, tool_input: dict = None) -> List[Dict]:
        """Check file against all extracted violation patterns."""
        violations = []
        
        for pattern_info in self.violation_patterns:
            check_func = pattern_info["check_func"]
            # Pass tool_input to check functions that need it
            violation = check_func(file_path, tool_input)
            if violation:
                violations.append(violation)
        
        return violations


def get_current_agent() -> str:
    """Get current agent from session state."""
    session_state_file = Path("Scripts/Logging/.session_state/session_state.json")
    
    if session_state_file.exists():
        try:
            with open(session_state_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
                return session_data.get("agent", "architect").lower()
        except Exception:
            pass
    
    return "architect"  # Default to architect


def main():
    """Main hook logic."""
    try:
        # Read event data from stdin
        if not sys.stdin.isatty():
            input_data = json.load(sys.stdin)
        else:
            # No stdin data available (running manually)
            print(json.dumps({}))
            return
        
        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})
        file_path = tool_input.get("file_path", "")
        
        # Only check write/edit operations
        if tool_name not in ["write", "edit"]:
            print(json.dumps({}))
            return
        
        file_path = tool_input.get("file_path", "")
        if not file_path:
            print(json.dumps({}))
            return
        
        # Get current agent and load rules
        current_agent = get_current_agent()
        rules_file = Path(f".devin/rules/{current_agent}.md")
        
        if not rules_file.exists():
            print(json.dumps({}))
            return
        
        # Parse rules and check violations
        rule_parser = RuleParser(str(rules_file))
        violations = rule_parser.check_violations(file_path, tool_input)
        
        if violations:
            # Format violation message for additionalContext
            violation_messages = []
            for violation in violations:
                # Determine appropriate response options based on violation type
                violation_type = violation['type']
                
                if violation_type in ["Best Practice Violation", "Fact Check Violation"]:
                    # BP/FC violations need remediation options
                    options = "[Do BP/FC Check & Remake file] or [Allow violation]?"
                elif violation_type in ["Whole File Creation Violation", "Whole File Modification Violation"]:
                    # Section-level violations need different options
                    options = "[Delete and recreate section by section] or [Allow violation]?"
                else:
                    # Placement violations use standard cleanup options
                    options = "[Allow violation] or [Deny and cleanup]?"
                
                violation_messages.append(
                    f"RULE VIOLATION DETECTED: {violation['type']}\n"
                    f"Rule: {violation['rule']}\n"
                    f"File: {violation['file']}\n"
                    f"Description: {violation['description']}\n"
                    f"Please ask user: {options}"
                )
            
            context_text = "\n\n".join(violation_messages)
            
            # Return additionalContext for next turn
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": context_text
                }
            }
            
            print(json.dumps(output))
        else:
            # No violations, return empty/allow
            print(json.dumps({}))
            
    except Exception as e:
        # Log error but don't block
        error_output = {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse", 
                "additionalContext": f"Rule violation detector error: {str(e)}"
            }
        }
        print(json.dumps(error_output))
        sys.exit(0)  # Don't block on errors


if __name__ == "__main__":
    main()
