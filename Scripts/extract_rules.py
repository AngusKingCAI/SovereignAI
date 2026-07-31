#!/usr/bin/env python3
"""
Extract Architect rules from session logs.
Processes all JSONL files in Logs/Architect/Session/ and generates NEVER/ALWAYS rules.
"""

import json
import re
from pathlib import Path
from collections import defaultdict

def load_existing_rules():
    """Load existing rules from architect.md to check for duplicates."""
    architect_path = Path("C:/SovereignAI/.devin/rules/architect.md")
    if not architect_path.exists():
        return set()
    
    with open(architect_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract NEVER and ALWAYS rules
    never_rules = set(re.findall(r'NEVER (.+?)\.', content))
    always_rules = set(re.findall(r'ALWAYS (.+?)\.', content))
    
    return {'NEVER': never_rules, 'ALWAYS': always_rules}

def analyze_log_file(file_path, existing_rules):
    """Analyze a single log file and extract new rules."""
    new_rules = {'NEVER': [], 'ALWAYS': []}
    duplicates_skipped = {'NEVER': 0, 'ALWAYS': 0}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                
                # Look for user prompts that indicate violations
                if entry.get('event') == 'user_prompt':
                    prompt = entry.get('prompt')
                    if prompt and isinstance(prompt, str):
                        prompt_lower = prompt.lower()
                        
                        # Extract potential rules from user corrections
                        if 'never' in prompt_lower or 'don\'t' in prompt_lower or 'should not' in prompt_lower:
                            # Extract NEVER rules
                            never_matches = re.findall(r'(?:never|don\'t|should not) (.+?)(?:\.|,| but|$)', prompt_lower, re.IGNORECASE)
                            for match in never_matches:
                                rule_text = match.strip()
                                if rule_text and rule_text not in existing_rules['NEVER']:
                                    new_rules['NEVER'].append(rule_text)
                                else:
                                    duplicates_skipped['NEVER'] += 1
                        
                        if 'always' in prompt_lower or 'should' in prompt_lower or 'must' in prompt_lower:
                            # Extract ALWAYS rules
                            always_matches = re.findall(r'(?:always|should|must) (.+?)(?:\.|,| but|$)', prompt_lower, re.IGNORECASE)
                            for match in always_matches:
                                rule_text = match.strip()
                                if rule_text and rule_text not in existing_rules['ALWAYS']:
                                    new_rules['ALWAYS'].append(rule_text)
                                else:
                                    duplicates_skipped['ALWAYS'] += 1
                
                # Look for error messages that indicate violations
                if entry.get('event') == 'tool_action':
                    success = entry.get('success')
                    if success == 'False' or success is False:
                        error_info = entry.get('error') or ''
                        if error_info and isinstance(error_info, str):
                            error_info_lower = error_info.lower()
                            if 'unable to access' in error_info_lower or 'no such file' in error_info_lower:
                                rule = 'verify file paths exist before operations'
                                if rule not in existing_rules['NEVER']:
                                    new_rules['NEVER'].append(rule)
                                else:
                                    duplicates_skipped['NEVER'] += 1
                
            except json.JSONDecodeError:
                continue
    
    return new_rules, duplicates_skipped

def categorize_rule(rule_text):
    """Categorize a rule into the appropriate section."""
    rule_lower = rule_text.lower()
    
    if any(keyword in rule_lower for keyword in ['path', 'file', 'directory', 'folder', 'structure']):
        return 'Infrastructure Governance'
    elif any(keyword in rule_lower for keyword in ['template', 'workflow', 'command', 'reference']):
        return 'Development Standards'
    elif any(keyword in rule_lower for keyword in ['user', 'clarification', 'question', 'answer']):
        return 'Agent Coordination'
    elif any(keyword in rule_lower for keyword in ['validate', 'check', 'verify', 'ensure']):
        return 'System Integrity'
    else:
        return 'Architectural Boundaries'

def main():
    log_dir = Path("C:/SovereignAI/Logs/Architect/Session")
    architect_path = Path("C:/SovereignAI/.devin/rules/architect.md")
    
    # Get all JSONL files
    log_files = sorted(log_dir.glob("*.jsonl"))
    print(f"Found {len(log_files)} log files to process")
    
    # Load existing rules
    existing_rules = load_existing_rules()
    print(f"Loaded existing rules: {len(existing_rules['NEVER'])} NEVER, {len(existing_rules['ALWAYS'])} ALWAYS")
    
    # Initialize rule collection by section
    rules_by_section = defaultdict(lambda: {'NEVER': [], 'ALWAYS': []})
    total_new_rules = 0
    total_duplicates = 0
    
    # Process each file
    for i, log_file in enumerate(log_files, 1):
        print(f"\nProcessing file {i}/{len(log_files)}: {log_file.name}")
        
        new_rules, duplicates = analyze_log_file(log_file, existing_rules)
        
        # Categorize and collect new rules
        for rule_type in ['NEVER', 'ALWAYS']:
            for rule_text in new_rules[rule_type]:
                section = categorize_rule(rule_text)
                if rule_text not in [r for r in rules_by_section[section][rule_type]]:
                    rules_by_section[section][rule_type].append(rule_text)
                    total_new_rules += 1
                    print(f"  ADDED: {rule_type} {rule_text}.")
                    existing_rules[rule_type].add(rule_text)
                else:
                    total_duplicates += 1
                    print(f"  SKIP: Duplicate rule found: {rule_text}")
        
        print(f"  New rules added: {len(new_rules['NEVER']) + len(new_rules['ALWAYS'])}")
        print(f"  Duplicates skipped: {duplicates['NEVER'] + duplicates['ALWAYS']}")
        print(f"Progress: {i} files processed, {total_new_rules} rules total, {total_duplicates} duplicates removed")
    
    # Write updated architect.md
    print(f"\nWriting updated rules to {architect_path}")
    
    with open(architect_path, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    # Rebuild the file with new rules
    sections_order = ['Architectural Boundaries', 'Development Standards', 'Infrastructure Governance', 'Agent Coordination', 'System Integrity']
    
    new_content = """---
id: architect-rules
status: active
owner: architect-agent
updated: 2026-07-31
purpose: Rules derived from all Architect sessions
---

# Architect Agent Rules

"""
    
    for section in sections_order:
        new_content += f"## {section}\n\n"
        
        if rules_by_section[section]['NEVER']:
            for rule in rules_by_section[section]['NEVER']:
                new_content += f"NEVER {rule}.\n"
            new_content += "\n"
        
        if rules_by_section[section]['ALWAYS']:
            for rule in rules_by_section[section]['ALWAYS']:
                new_content += f"ALWAYS {rule}.\n"
            new_content += "\n"
    
    with open(architect_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    # Final summary
    print("\n" + "="*50)
    print("FINAL SUMMARY:")
    print(f"- Files processed: {len(log_files)}")
    print(f"- Total rules generated: {total_new_rules}")
    print(f"- Duplicates removed: {total_duplicates}")
    print("- Rules by section:")
    for section in sections_order:
        never_count = len(rules_by_section[section]['NEVER'])
        always_count = len(rules_by_section[section]['ALWAYS'])
        print(f"  - {section}: {never_count + always_count} ({never_count} NEVER, {always_count} ALWAYS)")
    
    # Validation
    total_rules = sum(len(rules_by_section[s]['NEVER']) + len(rules_by_section[s]['ALWAYS']) for s in sections_order)
    validation = "PASS" if total_rules >= 10 and all(len(rules_by_section[s]['NEVER']) + len(rules_by_section[s]['ALWAYS']) > 0 for s in sections_order) else "FAIL"
    print(f"- VALIDATION: {validation}")
    print("="*50)

if __name__ == "__main__":
    main()