#!/usr/bin/env python3
"""
Round Table JSON Export Automation

Handles JSON export for git persistence per JSON_EXPORT_FORMAT.md.
Exports findings and rules to timestamped JSON files with git integration.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

# Set UTF-8 encoding for Windows console compatibility
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add database directory to path for import
sys.path.insert(0, str(Path(__file__).parent.parent / "database"))
from database_manager import RoundTableDatabase

class JSONExporter:
    """JSON exporter for Round Table findings and rules."""
    
    def __init__(self, export_dir: str = None):
        """Initialize export directory."""
        if export_dir is None:
            export_dir = Path(".Planner/roundtable/export")
        else:
            export_dir = Path(export_dir)
        
        self.export_dir = export_dir
        self.export_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (self.export_dir / "findings").mkdir(exist_ok=True)
        (self.export_dir / "rules").mkdir(exist_ok=True)
        (self.export_dir / "audit").mkdir(exist_ok=True)
    
    def export_findings(self, batch_id: str = None) -> str:
        """Export findings to JSON file."""
        db = RoundTableDatabase()
        
        # Get findings data
        findings_data = db.export_findings_json(batch_id)
        
        # Generate filename
        timestamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
        if batch_id:
            filename = f"findings_batch_{batch_id}_{timestamp}.json"
        else:
            filename = f"findings_all_{timestamp}.json"
        
        filepath = self.export_dir / "findings" / filename
        
        # Write JSON file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(findings_data, f, indent=2)
        
        safe_print(f"✅ Exported findings to {filepath}")
        return str(filepath)
    
    def export_rules(self) -> str:
        """Export rules to JSON file."""
        db = RoundTableDatabase()
        
        # Get rules data
        rules_data = db.export_rules_json()
        
        # Generate filename
        timestamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
        filename = f"roundtable_rules_{timestamp}.json"
        
        filepath = self.export_dir / "rules" / filename
        
        # Write JSON file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(rules_data, f, indent=2)
        
        safe_print(f"✅ Exported rules to {filepath}")
        return str(filepath)
    
    def export_audit_log(self, limit: int = 1000) -> str:
        """Export audit log to JSON file."""
        db = RoundTableDatabase()
        
        # Get audit events
        audit_events = db.get_audit_events(limit=limit)
        
        # Build export data
        export_data = {
            "export_metadata": {
                "export_timestamp": datetime.utcnow().isoformat() + "Z",
                "export_version": "1.0",
                "total_events": len(audit_events)
            },
            "events": audit_events
        }
        
        # Generate filename
        timestamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
        filename = f"audit_log_{timestamp}.json"
        
        filepath = self.export_dir / "audit" / filename
        
        # Write JSON file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2)
        
        safe_print(f"✅ Exported audit log to {filepath}")
        return str(filepath)
    
    def git_commit_findings(self, batch_id: str, filepath: str):
        """Commit findings export to git with structured message."""
        db = RoundTableDatabase()
        findings_data = db.export_findings_json(batch_id)
        
        commit_message = f"""RoundTable: Export findings for batch {batch_id}

Export timestamp: {findings_data['export_metadata']['export_timestamp']}
Total findings: {findings_data['export_metadata']['total_findings']}

Summary:
- CRITICAL: {findings_data['summary']['by_severity'].get('CRITICAL', 0)}
- HIGH: {findings_data['summary']['by_severity'].get('HIGH', 0)}
- MEDIUM: {findings_data['summary']['by_severity'].get('MEDIUM', 0)}
- LOW: {findings_data['summary']['by_severity'].get('LOW', 0)}

Generated with Devin RoundTable workflow"""
        
        self._git_commit(filepath, commit_message)
    
    def git_commit_rules(self, filepath: str):
        """Commit rules export to git with structured message."""
        db = RoundTableDatabase()
        rules_data = db.export_rules_json()
        
        commit_message = f"""RoundTable: Export rules with pattern analysis

Export timestamp: {rules_data['export_metadata']['export_timestamp']}
Total rules: {rules_data['export_metadata']['total_rules']}
Active rules: {rules_data['export_metadata']['active_rules']}

Summary:
- By category: {rules_data['summary']['by_category']}
- By enforcement: {rules_data['summary']['by_enforcement']}

Generated with Devin RoundTable workflow"""
        
        self._git_commit(filepath, commit_message)
    
    def git_commit_audit(self, filepath: str):
        """Commit audit log export to git with structured message."""
        commit_message = f"""RoundTable: Export audit log

Export timestamp: {datetime.utcnow().isoformat() + "Z"}
Total events: Exported in file

Generated with Devin RoundTable workflow"""
        
        self._git_commit(filepath, commit_message)
    
    def _git_commit(self, filepath: str, commit_message: str):
        """Internal git commit method (local commit only, does not push per Gate A10)."""
        try:
            # Add file to git
            subprocess.run(['git', 'add', filepath], check=True, capture_output=True)
            
            # Commit with message (local commit only - no push per Gate A10)
            subprocess.run(['git', 'commit', '-m', commit_message], check=True, capture_output=True)
            
            safe_print(f"✅ Committed {filepath} to git (local commit, not pushed per Gate A10)")
        except subprocess.CalledProcessError as e:
            safe_print(f"⚠️  Git commit failed: {e}")
            safe_print(f"   File staged but not committed: {filepath}")
    
    def export_full_batch(self, batch_id: str, commit_to_git: bool = True):
        """Export all data for a batch (findings, rules, audit) and optionally commit to git."""
        safe_print(f"Exporting full batch {batch_id}...")
        
        # Export findings
        findings_file = self.export_findings(batch_id)
        
        # Export rules
        rules_file = self.export_rules()
        
        # Export audit log
        audit_file = self.export_audit_log()
        
        if commit_to_git:
            safe_print("Committing to git...")
            self.git_commit_findings(batch_id, findings_file)
            self.git_commit_rules(rules_file)
            self.git_commit_audit(audit_file)
        
        safe_print(f"✅ Full batch {batch_id} export complete")

def main():
    """Test JSON export operations."""
    exporter = JSONExporter()
    
    # Test export operations
    safe_print("Testing JSON export operations...")
    
    # Export findings
    findings_file = exporter.export_findings("test-batch-1")
    
    # Export rules
    rules_file = exporter.export_rules()
    
    # Export audit log
    audit_file = exporter.export_audit_log()
    
    safe_print(f"✅ JSON export test complete")
    safe_print(f"   Findings: {findings_file}")
    safe_print(f"   Rules: {rules_file}")
    safe_print(f"   Audit: {audit_file}")

if __name__ == "__main__":
    main()