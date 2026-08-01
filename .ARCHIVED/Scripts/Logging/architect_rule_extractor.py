#!/usr/bin/env python3
"""
Architect Rule Extractor - Extract NEVER/ALWAYS rules from Architect session logs
"""
import json
import re
from pathlib import Path
from collections import defaultdict

def extract_rules_from_log(log_file_path):
    """Extract potential NEVER/ALWAYS rules from a log file."""
    rules = {
        'NEVER': set(),
        'ALWAYS': set()
    }
    
    try:
        with open(log_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    
                    # Extract from prompt content
                    if entry.get('event') == 'user_prompt' and entry.get('prompt'):
                        prompt_text = entry['prompt'].lower()
                        
                        # Look for patterns indicating violations or best practices
                        if 'never' in prompt_text or 'always' in prompt_text:
                            # Extract sentences with never/always
                            sentences = re.split(r'[.!?]', prompt_text)
                            for sentence in sentences:
                                sentence = sentence.strip()
                                if 'never' in sentence and len(sentence) > 10:
                                    rules['NEVER'].add(sentence)
                                elif 'always' in sentence and len(sentence) > 10:
                                    rules['ALWAYS'].add(sentence)
                    
                    # Extract from tool actions that might indicate violations
                    if entry.get('event') == 'tool_action':
                        tool_output = str(entry.get('output', '')).lower()
                        if 'error' in tool_output or 'failed' in tool_output:
                            # This might indicate a violation pattern
                            if 'never' in tool_output:
                                never_matches = re.findall(r'never [^.!?]+', tool_output)
                                for match in never_matches:
                                    if len(match) > 10:
                                        rules['NEVER'].add(match)
                            if 'always' in tool_output:
                                always_matches = re.findall(r'always [^.!?]+', tool_output)
                                for match in always_matches:
                                    if len(match) > 10:
                                        rules['ALWAYS'].add(match)
                
                except json.JSONDecodeError:
                    continue
                except Exception:
                    continue
    
    except Exception as e:
        print(f"Error reading {log_file_path}: {e}")
    
    return rules

def categorize_rule(rule_text, rule_type):
    """Categorize a rule into one of the 5 sections."""
    rule_lower = rule_text.lower()
    
    # Keywords for each category
    architectural_keywords = ['architecture', 'design', 'structure', 'system', 'component', 'module', 'interface']
    development_keywords = ['code', 'implement', 'function', 'test', 'write', 'debug', 'refactor']
    infrastructure_keywords = ['infrastructure', 'script', 'config', 'setup', 'deploy', 'environment', 'harness']
    coordination_keywords = ['agent', 'workflow', 'coordinate', 'communicate', 'handoff', 'collaborate']
    integrity_keywords = ['security', 'validation', 'compliance', 'verify', 'check', 'integrity', 'error']
    
    for keyword in architectural_keywords:
        if keyword in rule_lower:
            return 'Architectural Boundaries'
    
    for keyword in development_keywords:
        if keyword in rule_lower:
            return 'Development Standards'
    
    for keyword in infrastructure_keywords:
        if keyword in rule_lower:
            return 'Infrastructure Governance'
    
    for keyword in coordination_keywords:
        if keyword in rule_lower:
            return 'Agent Coordination'
    
    for keyword in integrity_keywords:
        if keyword in rule_lower:
            return 'System Integrity'
    
    # Default to System Integrity if no match
    return 'System Integrity'

def main():
    log_dir = Path('C:/SovereignAI/Logs/Architect/Session')
    architect_rules_path = Path('C:/SovereignAI/.devin/rules/architect.md')
    
    # Get all log files
    log_files = sorted(log_dir.glob('*.jsonl'))
    print(f"Found {len(log_files)} log files to process")
    
    # Read existing rules
    existing_rules = defaultdict(set)
    sections = {
        'Architectural Boundaries': existing_rules['Architectural Boundaries'],
        'Development Standards': existing_rules['Development Standards'],
        'Infrastructure Governance': existing_rules['Infrastructure Governance'],
        'Agent Coordination': existing_rules['Agent Coordination'],
        'System Integrity': existing_rules['System Integrity']
    }
    
    # Process each log file
    total_new_rules = 0
    total_duplicates = 0
    
    for i, log_file in enumerate(log_files, 1):
        print(f"\nProcessing file {i}/{len(log_files)}: {log_file.name}")
        
        # Extract rules from this file
        file_rules = extract_rules_from_log(log_file)
        
        file_new_rules = 0
        file_duplicates = 0
        
        # Process NEVER rules
        for rule in file_rules['NEVER']:
            # Normalize rule text
            normalized_rule = rule.strip().capitalize()
            if not normalized_rule.endswith('.'):
                normalized_rule += '.'
            
            # Check for duplicates
            is_duplicate = False
            for section_rules in existing_rules.values():
                if normalized_rule in section_rules:
                    is_duplicate = True
                    break
            
            if is_duplicate:
                print(f"  SKIP: Duplicate NEVER rule: {normalized_rule[:60]}...")
                file_duplicates += 1
            else:
                # Categorize and add
                section = categorize_rule(normalized_rule, 'NEVER')
                existing_rules[section].add(normalized_rule)
                print(f"  ADDED: NEVER {normalized_rule[:60]}...")
                file_new_rules += 1
        
        # Process ALWAYS rules
        for rule in file_rules['ALWAYS']:
            # Normalize rule text
            normalized_rule = rule.strip().capitalize()
            if not normalized_rule.endswith('.'):
                normalized_rule += '.'
            
            # Check for duplicates
            is_duplicate = False
            for section_rules in existing_rules.values():
                if normalized_rule in section_rules:
                    is_duplicate = True
                    break
            
            if is_duplicate:
                print(f"  SKIP: Duplicate ALWAYS rule: {normalized_rule[:60]}...")
                file_duplicates += 1
            else:
                # Categorize and add
                section = categorize_rule(normalized_rule, 'ALWAYS')
                existing_rules[section].add(normalized_rule)
                print(f"  ADDED: ALWAYS {normalized_rule[:60]}...")
                file_new_rules += 1
        
        print(f"File: {log_file.name}")
        print(f"  New rules added: {file_new_rules}")
        print(f"  Duplicates skipped: {file_duplicates}")
        
        total_new_rules += file_new_rules
        total_duplicates += file_duplicates
        
        print(f"Progress: {i} files processed, {total_new_rules} rules total, {total_duplicates} duplicates removed")
    
    # Write updated architect.md
    print(f"\nWriting updated rules to {architect_rules_path}")
    
    with open(architect_rules_path, 'w', encoding='utf-8') as f:
        f.write("---\n")
        f.write("id: architect-rules\n")
        f.write("status: active\n")
        f.write("owner: architect-agent\n")
        f.write("updated: 2026-07-31\n")
        f.write("purpose: Rules derived from all Architect sessions\n")
        f.write("---\n\n")
        f.write("# Architect Agent Rules\n\n")
        
        for section_name, rules in sections.items():
            f.write(f"## {section_name}\n\n")
            for rule in sorted(rules):
                if rule.startswith('Never'):
                    f.write(f"NEVER {rule[5:].strip()}\n")
                elif rule.startswith('Always'):
                    f.write(f"ALWAYS {rule[6:].strip()}\n")
                else:
                    f.write(f"{rule}\n")
            f.write("\n")
    
    # Final validation
    print("\nFINAL SUMMARY:")
    print(f"- Files processed: {len(log_files)}")
    print(f"- Total rules generated: {total_new_rules}")
    print(f"- Duplicates removed: {total_duplicates}")
    print(f"- Rules by section:")
    for section_name, rules in sections.items():
        print(f"  - {section_name}: {len(rules)}")
    
    # Validation checks
    all_sections_nonempty = all(len(rules) > 0 for rules in sections.values())
    at_least_10_rules = total_new_rules >= 10
    all_proper_format = all(
        (rule.startswith('Never') or rule.startswith('Always')) 
        for rules in sections.values() 
        for rule in rules
    )
    
    validation = "PASS" if (all_sections_nonempty and at_least_10_rules and all_proper_format) else "FAIL"
    print(f"- VALIDATION: {validation}")

if __name__ == "__main__":
    main()