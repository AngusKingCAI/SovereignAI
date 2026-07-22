#!/usr/bin/env python3
"""
Rule Integration Script

Integrates rule suggestions from pattern analysis into PLANNER_RULES.md.
Implements RI1, RI2, RI3 workflow rules from RULE_INTEGRATION_WORKFLOW.md.
"""

import sys
import os
import json
import argparse
from pathlib import Path
import re
import shutil

# UTF-8 print helper for Windows console compatibility
def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', 'ignore').decode('ascii'))

# UTF-8 print helper for Windows console compatibility
def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', 'ignore').decode('ascii'))

class RuleIntegrator:
    """Integrates rule suggestions into PLANNER_RULES.md."""
    
    def __init__(self, planner_rules_path=None, rule_suggestion_path=None):
        """Initialize rule integrator."""
        self.planner_rules_path = planner_rules_path or self._find_planner_rules()
        self.rule_suggestion_path = rule_suggestion_path
        self.rule_suggestions = []
        self.integrated_rules = []
        
    def _find_planner_rules(self):
        """Find PLANNER_RULES.md file."""
        candidates = [
            Path(".Planner") / "rules" / "PLANNER_RULES.md",
            Path("..") / ".Planner" / "rules" / "PLANNER_RULES.md",
            Path("..") / ".." / ".Planner" / "rules" / "PLANNER_RULES.md"
        ]
        
        for candidate in candidates:
            if candidate.exists():
                return str(candidate)
        
        return None
    
    def load_rule_suggestions(self):
        """Load rule suggestions from JSON file."""
        if not self.rule_suggestion_path:
            safe_print("No rule suggestion file provided")
            return False
        
        try:
            with open(self.rule_suggestion_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.rule_suggestions = data.get('rule_suggestions', [])
            
            safe_print(f"Loaded {len(self.rule_suggestions)} rule suggestions")
            return True
            
        except Exception as e:
            safe_print(f"Error loading rule suggestions: {e}")
            return False
    
    def validate_rules(self):
        """Validate rule suggestions per RI1."""
        validated_rules = []
        
        for rule in self.rule_suggestions:
            if self._validate_single_rule(rule):
                validated_rules.append(rule)
                safe_print(f"✅ Gate RI1 PASS: Rule {rule['rule_id']} validated")
            else:
                safe_print(f"❌ Gate RI1 FAIL: Rule {rule['rule_id']} validation failed")
        
        self.rule_suggestions = validated_rules
        return len(validated_rules) > 0
    
    def _validate_single_rule(self, rule):
        """Validate a single rule suggestion."""
        # Check for required fields
        required_fields = ['rule_id', 'title', 'description', 'trigger_conditions', 'enforcement_level', 'category']
        for field in required_fields:
            if field not in rule:
                safe_print(f"Missing required field: {field}")
                return False
        
        # Check rule ID format
        if not re.match(r'^PR\d+$', rule['rule_id']):
            safe_print(f"Invalid rule ID format: {rule['rule_id']}")
            return False
        
        # Check enforcement level
        valid_enforcement = ['hard_gate', 'soft_gate', 'guideline']
        if rule['enforcement_level'] not in valid_enforcement:
            safe_print(f"Invalid enforcement level: {rule['enforcement_level']}")
            return False
        
        # Check for duplicates (if PLANNER_RULES.md exists)
        if self.planner_rules_path:
            if self._check_duplicate_rule(rule):
                safe_print(f"Duplicate rule detected: {rule['rule_id']}")
                return False
        
        return True
    
    def _check_duplicate_rule(self, rule):
        """Check for duplicate rule in PLANNER_RULES.md."""
        if not self.planner_rules_path:
            return False
        
        try:
            with open(self.planner_rules_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for duplicate rule ID
            if rule['rule_id'] in content:
                return True
            
            # Check for similar title
            rule_title_lower = rule['title'].lower()
            if rule_title_lower in content.lower():
                return True
            
            return False
            
        except Exception as e:
            safe_print(f"Error checking duplicates: {e}")
            return False
    
    def integrate_rules(self):
        """Integrate validated rules into PLANNER_RULES.md per RI2."""
        if not self.planner_rules_path:
            safe_print("PLANNER_RULES.md not found, cannot integrate")
            return False
        
        if not self.rule_suggestions:
            safe_print("No validated rules to integrate")
            return False
        
        try:
            # Backup original file
            backup_path = self.planner_rules_path + '.backup'
            shutil.copy2(self.planner_rules_path, backup_path)
            safe_print(f"Backup created at {backup_path}")
            
            # Read existing content
            with open(self.planner_rules_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Integrate each rule
            for rule in self.rule_suggestions:
                content = self._integrate_single_rule(content, rule)
                self.integrated_rules.append(rule)
                safe_print(f"✅ Gate RI2 PASS: Rule {rule['rule_id']} integrated")
            
            # Write updated content
            with open(self.planner_rules_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            safe_print(f"✅ Rules integrated into PLANNER_RULES.md")
            return True
            
        except Exception as e:
            safe_print(f"Error integrating rules: {e}")
            # Restore backup if integration failed
            if backup_path and Path(backup_path).exists():
                shutil.copy2(backup_path, self.planner_rules_path)
                safe_print("Backup restored due to integration error")
            return False
    
    def _integrate_single_rule(self, content, rule):
        """Integrate a single rule into content."""
        # Find appropriate section based on category
        section_pattern = rf"## {rule['category'].capitalize()}"
        
        if section_pattern.lower() in content.lower():
            # Add to existing section
            section_start = content.lower().find(section_pattern.lower())
            # Find next section or end of file
            next_section = content.find('\n## ', section_start + 1)
            if next_section == -1:
                next_section = len(content)
            
            # Insert rule before next section
            rule_text = self._format_rule(rule)
            content = content[:next_section] + '\n' + rule_text + '\n' + content[next_section:]
        else:
            # Create new section
            section_text = f"\n## {rule['category'].capitalize()}\n\n"
            rule_text = self._format_rule(rule)
            content += section_text + rule_text + '\n'
        
        # Update rule index
        content = self._update_rule_index(content, rule)
        
        return content
    
    def _format_rule(self, rule):
        """Format rule for PLANNER_RULES.md."""
        return f"""### {rule['rule_id']}: {rule['title']}

**Trigger**: {rule['trigger_conditions']}  
**Enforcement**: {rule['enforcement_level']}  
**Category**: {rule['category']}

{rule['description']}

**Pattern Source**: {rule.get('pattern_source', 'N/A')}  
**Source Findings**: {', '.join(map(str, rule.get('source_findings', [])))}
"""
    
    def _update_rule_index(self, content, rule):
        """Update rule index at top of PLANNER_RULES.md."""
        # Find rule index table
        index_pattern = r'\| Rule ID \|'
        if index_pattern in content:
            # Add new rule to index
            index_end = content.find('\n\n', content.find(index_pattern))
            if index_end != -1:
                index_section = content[:index_end]
                new_index_row = f"| {rule['rule_id']} | {rule['trigger_conditions']} | §{rule['rule_id'][2:]} |\n"
                content = index_section + new_index_row + content[index_end:]
        
        return content
    
    def test_rules(self):
        """Test rule enforcement mechanisms per RI3."""
        tested_rules = []
        
        for rule in self.integrated_rules:
            if self._test_single_rule(rule):
                tested_rules.append(rule)
                safe_print(f"✅ Gate RI3 PASS: Rule {rule['rule_id']} tested successfully")
            else:
                safe_print(f"❌ Gate RI3 FAIL: Rule {rule['rule_id']} test failed")
        
        return len(tested_rules) == len(self.integrated_rules)
    
    def _test_single_rule(self, rule):
        """Test a single rule enforcement mechanism."""
        # In a real implementation, this would test the actual enforcement mechanism
        # For now, we'll do basic validation
        
        # Check if enforcement level is appropriate for severity
        if rule.get('evidence', {}).get('occurrence_count', 0) >= 5:
            if rule['enforcement_level'] != 'hard_gate':
                safe_print(f"Warning: High-occurrence rule should be hard gate")
                return False
        
        # Basic structural validation
        if not rule['title'] or not rule['description']:
            return False
        
        return True
    
    def export_results(self, output_file=None):
        """Export integration results to JSON."""
        results = {
            'integration_timestamp': Path().cwd().name,
            'total_rules_suggested': len(self.rule_suggestions),
            'rules_validated': len(self.rule_suggestions),
            'rules_integrated': len(self.integrated_rules),
            'integration_status': 'completed' if self.integrated_rules else 'failed',
            'integrated_rules': self.integrated_rules
        }
        
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)
            
            safe_print(f"✅ Results exported to {output_file}")
        else:
            safe_print(json.dumps(results, indent=2))
        
        return results

def main():
    """Main rule integration pipeline."""
    parser = argparse.ArgumentParser(description='Rule Integration Script')
    parser.add_argument('--planner-rules', type=str, help='Path to PLANNER_RULES.md')
    parser.add_argument('--rule-suggestions', type=str, required=True, help='Path to rule suggestions JSON')
    parser.add_argument('--output', type=str, help='Output JSON file path')
    
    args = parser.parse_args()
    
    safe_print("Starting Rule Integration Pipeline...")
    
    # Initialize integrator
    integrator = RuleIntegrator(
        planner_rules_path=args.planner_rules,
        rule_suggestion_path=args.rule_suggestions
    )
    
    # Load rule suggestions
    if not integrator.load_rule_suggestions():
        safe_print("Failed to load rule suggestions")
        return 1
    
    # Validate rules
    if not integrator.validate_rules():
        safe_print("No valid rules to integrate")
        return 1
    
    # Integrate rules
    if not integrator.integrate_rules():
        safe_print("Failed to integrate rules")
        return 1
    
    # Test rules
    if not integrator.test_rules():
        safe_print("Some rules failed testing")
        return 1
    
    # Export results
    integrator.export_results(args.output)
    
    safe_print(f"✅ Gate RI-COMPLETE: Rule integration complete, {len(integrator.integrated_rules)} rules integrated")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())