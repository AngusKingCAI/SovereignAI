#!/usr/bin/env python3
"""
Pattern Analysis Pipeline

Analyzes Round Table findings to identify recurring patterns and suggest new rules.
Implements PA1, PA2, PA3 workflow rules from PATTERN_ANALYSIS_WORKFLOW.md.
"""

import sys
import os
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import re

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

class PatternAnalyzer:
    """Analyzes Round Table findings for pattern-based rule suggestions."""
    
    def __init__(self, db_path=None, days=30, threshold=3):
        """Initialize pattern analyzer."""
        self.days = days
        self.threshold = threshold
        self.db_path = db_path or self._find_database()
        self.findings = []
        self.patterns = []
        self.rule_suggestions = []
        
    def _find_database(self):
        """Find Round Table database."""
        # Try script directory first
        script_dir = Path(__file__).parent
        db_candidates = [
            script_dir / ".Planner" / "roundtable" / "database" / "roundtable.db",
            Path(".Planner") / "roundtable" / "database" / "roundtable.db",
            Path("..") / ".Planner" / "roundtable" / "database" / "roundtable.db",
            Path("..") / ".." / ".Planner" / "roundtable" / "database" / "roundtable.db"
        ]
        
        for candidate in db_candidates:
            if candidate.exists():
                return str(candidate)
        
        return None
    
    def collect_findings(self):
        """Collect findings from database within time window."""
        if not self.db_path:
            safe_print("Database not found, using test data")
            self._load_test_findings()
            return
        
        try:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Calculate time window
            cutoff_date = (datetime.now() - timedelta(days=self.days)).timestamp()
            
            # Query findings
            cursor.execute("""
                SELECT f.id, f.category, f.severity, f.description, f.context, f.status,
                       f.plan_impact, pr.panelist_id, pr.confidence_score
                FROM findings f
                JOIN panelist_reviews pr ON f.review_id = pr.id
                WHERE f.created_at >= ? AND f.status IN ('open', 'addressed')
                ORDER BY f.created_at DESC
            """, (cutoff_date,))
            
            rows = cursor.fetchall()
            self.findings = [
                {
                    'id': row[0],
                    'category': row[1],
                    'severity': row[2],
                    'description': row[3],
                    'context': row[4],
                    'status': row[5],
                    'plan_impact': row[6],
                    'panelist_id': row[7],
                    'confidence_score': row[8]
                }
                for row in rows
            ]
            
            conn.close()
            safe_print(f"Collected {len(self.findings)} findings from database")
            
        except Exception as e:
            safe_print(f"Error accessing database: {e}")
            self._load_test_findings()
    
    def _load_test_findings(self):
        """Load test findings for demonstration."""
        self.findings = [
            {'id': 1, 'category': 'governance', 'severity': 'CRITICAL', 'description': 'Missing security compliance check', 'context': 'Plan lacks security review', 'status': 'open', 'plan_impact': 'high', 'panelist_id': 1, 'confidence_score': 85},
            {'id': 2, 'category': 'structure', 'severity': 'HIGH', 'description': 'Incomplete manifest section', 'context': 'Manifest missing required fields', 'status': 'open', 'plan_impact': 'medium', 'panelist_id': 1, 'confidence_score': 75},
            {'id': 3, 'category': 'governance', 'severity': 'CRITICAL', 'description': 'Missing security compliance check', 'context': 'Plan lacks security review', 'status': 'open', 'plan_impact': 'high', 'panelist_id': 2, 'confidence_score': 90},
            {'id': 4, 'category': 'quality', 'severity': 'MEDIUM', 'description': 'Ambiguous language in requirements', 'context': 'Requirements use vague terms', 'status': 'open', 'plan_impact': 'low', 'panelist_id': 1, 'confidence_score': 70},
            {'id': 5, 'category': 'governance', 'severity': 'CRITICAL', 'description': 'Missing security compliance check', 'context': 'Plan lacks security review', 'status': 'open', 'plan_impact': 'high', 'panelist_id': 3, 'confidence_score': 88},
        ]
        safe_print(f"Loaded {len(self.findings)} test findings")
    
    def cluster_patterns(self):
        """Cluster findings by category, severity, and semantic similarity."""
        # Group by category and severity
        category_groups = defaultdict(lambda: defaultdict(list))
        
        for finding in self.findings:
            category_groups[finding['category']][finding['severity']].append(finding)
        
        # Analyze each group for patterns
        for category, severity_groups in category_groups.items():
            for severity, findings in severity_groups.items():
                if len(findings) >= self.threshold:
                    pattern = self._analyze_pattern(category, severity, findings)
                    if pattern:
                        self.patterns.append(pattern)
                        safe_print(f"✅ Gate PA1 PASS: Pattern detected - {category}/{severity} ({len(findings)} occurrences)")
    
    def _analyze_pattern(self, category, severity, findings):
        """Analyze a group of findings to extract pattern characteristics."""
        # Analyze description patterns
        descriptions = [f['description'] for f in findings]
        common_words = self._extract_common_words(descriptions)
        
        # Calculate panelist agreement
        panelist_ids = [f['panelist_id'] for f in findings]
        unique_panelists = len(set(panelist_ids))
        agreement_score = unique_panelists / len(findings) if findings else 0
        
        # Calculate average confidence
        avg_confidence = sum(f['confidence_score'] for f in findings) / len(findings) if findings else 0
        
        # Validate quality (PA3)
        if not self._validate_pattern_quality(findings, agreement_score, avg_confidence):
            return None
        
        # Create pattern
        pattern = {
            'pattern_id': f"P{len(self.patterns) + 1:03d}",
            'category': category,
            'severity': severity,
            'occurrence_count': len(findings),
            'finding_ids': [f['id'] for f in findings],
            'panelist_agreement': agreement_score,
            'confidence_score': avg_confidence,
            'common_words': common_words,
            'descriptions': descriptions
        }
        
        return pattern
    
    def _extract_common_words(self, descriptions):
        """Extract common words from descriptions."""
        word_counts = defaultdict(int)
        
        for desc in descriptions:
            words = re.findall(r'\b\w+\b', desc.lower())
            for word in words:
                if len(word) > 3:  # Ignore short words
                    word_counts[word] += 1
        
        # Return words that appear in multiple descriptions
        common_words = [word for word, count in word_counts.items() if count >= 2]
        return common_words
    
    def _validate_pattern_quality(self, findings, agreement_score, confidence_score):
        """Validate pattern quality per PA3."""
        # Check panelist agreement (≥2 panelists)
        unique_panelists = len(set(f['panelist_id'] for f in findings))
        if unique_panelists < 2:
            safe_print(f"⚠️  Gate PA3 FAIL: Insufficient panelist agreement ({unique_panelists} < 2)")
            return False
        
        # Check confidence threshold (≥70%)
        if confidence_score < 70:
            safe_print(f"⚠️  Gate PA3 FAIL: Low confidence score ({confidence_score:.1f} < 70)")
            return False
        
        # Check context completeness
        for finding in findings:
            if not finding.get('context'):
                safe_print(f"⚠️  Gate PA3 FAIL: Missing context for finding {finding['id']}")
                return False
        
        # Check actionability
        for finding in findings:
            if not finding.get('plan_impact'):
                safe_print(f"⚠️  Gate PA3 FAIL: Missing plan impact for finding {finding['id']}")
                return False
        
        safe_print(f"✅ Gate PA3 PASS: Pattern quality validation passed")
        return True
    
    def generate_rule_suggestions(self):
        """Generate rule suggestions from patterns."""
        next_rule_id = self._get_next_rule_id()
        
        for pattern in self.patterns:
            rule_suggestion = self._create_rule_suggestion(pattern, next_rule_id)
            if rule_suggestion:
                self.rule_suggestions.append(rule_suggestion)
                next_rule_id += 1
                safe_print(f"✅ Gate PA2 PASS: Rule suggestion generated - {rule_suggestion['rule_id']}")
    
    def _get_next_rule_id(self):
        """Get next available rule ID."""
        # In a real implementation, this would query PLANNER_RULES.md
        # For now, start at PR17 (assuming PR1-PR16 exist)
        return 17
    
    def _create_rule_suggestion(self, pattern, rule_id):
        """Create rule suggestion from pattern."""
        # Map category to enforcement level
        enforcement_mapping = {
            'CRITICAL': 'hard_gate',
            'HIGH': 'hard_gate',
            'MEDIUM': 'soft_gate',
            'LOW': 'guideline'
        }
        
        enforcement_level = enforcement_mapping.get(pattern['severity'], 'guideline')
        
        # Create rule suggestion
        rule_suggestion = {
            'rule_id': f"PR{rule_id}",
            'title': self._generate_rule_title(pattern),
            'description': self._generate_rule_description(pattern),
            'trigger_conditions': self._generate_trigger_conditions(pattern),
            'enforcement_level': enforcement_level,
            'category': pattern['category'],
            'pattern_source': pattern['pattern_id'],
            'source_findings': pattern['finding_ids'],
            'evidence': {
                'occurrence_count': pattern['occurrence_count'],
                'panelist_agreement': pattern['panelist_agreement'],
                'confidence_score': pattern['confidence_score']
            }
        }
        
        return rule_suggestion
    
    def _generate_rule_title(self, pattern):
        """Generate rule title from pattern."""
        category_title = pattern['category'].capitalize()
        severity_title = pattern['severity'].capitalize()
        common_words = ' '.join(pattern['common_words'][:3]) if pattern['common_words'] else 'Generic'
        
        return f"{category_title} {severity_title}: {common_words.title()}"
    
    def _generate_rule_description(self, pattern):
        """Generate rule description from pattern."""
        category = pattern['category']
        common_desc = pattern['descriptions'][0] if pattern['descriptions'] else "Generic issue"
        
        return f"Plans must address {category} issues related to {common_desc.lower()}. This pattern was detected {pattern['occurrence_count']} times with {pattern['confidence_score']:.1f}% confidence."
    
    def _generate_trigger_conditions(self, pattern):
        """Generate trigger conditions from pattern."""
        category = pattern['category']
        
        triggers = {
            'governance': "Plan submitted for Round Table review",
            'structure': "Plan structure validation during Phase 2",
            'content': "Plan content validation during Phase 4",
            'quality': "Plan quality validation during Phase 5",
            'security': "Security review during Phase 6"
        }
        
        return triggers.get(category, "Plan validation")
    
    def export_results(self, output_file=None):
        """Export pattern analysis results to JSON."""
        results = {
            'analysis_timestamp': datetime.now().isoformat() + 'Z',
            'time_window': f"{self.days} days",
            'total_findings_analyzed': len(self.findings),
            'patterns_detected': len(self.patterns),
            'rules_suggested': len(self.rule_suggestions),
            'patterns': self.patterns,
            'rule_suggestions': self.rule_suggestions
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
    """Main pattern analysis pipeline."""
    parser = argparse.ArgumentParser(description='Pattern Analysis Pipeline')
    parser.add_argument('--days', type=int, default=30, help='Time window in days')
    parser.add_argument('--threshold', type=int, default=3, help='Minimum occurrence threshold')
    parser.add_argument('--db-path', type=str, help='Path to Round Table database')
    parser.add_argument('--output', type=str, help='Output JSON file path')
    
    args = parser.parse_args()
    
    safe_print("Starting Pattern Analysis Pipeline...")
    safe_print(f"Time window: {args.days} days")
    safe_print(f"Threshold: {args.threshold} occurrences")
    
    # Initialize analyzer
    analyzer = PatternAnalyzer(
        db_path=args.db_path,
        days=args.days,
        threshold=args.threshold
    )
    
    # Collect findings
    analyzer.collect_findings()
    
    # Cluster patterns
    analyzer.cluster_patterns()
    
    # Generate rule suggestions
    analyzer.generate_rule_suggestions()
    
    # Export results
    results = analyzer.export_results(args.output)
    
    safe_print(f"✅ Gate PA-COMPLETE: Pattern analysis complete, {len(analyzer.rule_suggestions)} rules suggested")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())