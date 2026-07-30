#!/usr/bin/env python3
"""
Efficient Report Writer for SovereignAI
Provides efficient file writing for large reports using append operations
"""

import os
import sys
from datetime import datetime
from pathlib import Path


class EfficientReportWriter:
    """Efficient report writer that uses append operations for better performance"""
    
    def __init__(self, report_dir: str, report_name: str):
        self.report_dir = Path(report_dir)
        self.report_name = report_name
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Ensure directory exists
        self.report_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize report file
        self.report_file = self.report_dir / f"{report_name}-{self.timestamp}.md"
        self._initialize_report()
    
    def _initialize_report(self):
        """Initialize the report with header information"""
        try:
            header = f"""# {self.report_name}
**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Report Name**: {self.report_name}
**Timestamp**: {self.timestamp}

## Scan Progress

---
"""
            self.report_file.write_text(header, encoding='utf-8')
        except (IOError, OSError) as e:
            print(f"❌ Failed to initialize report file: {e}", file=sys.stderr)
            raise
    
    def append_file_analysis(self, file_number: int, file_path: str, analysis: dict):
        """Append file analysis to report using append operation"""
        entry = f"""### File {file_number}: {file_path}
**Type**: {analysis.get('type', 'Unknown')}
**Complexity**: {analysis.get('complexity', 'Unknown')}
**Compliance Status**: {analysis.get('compliance_status', 'UNKNOWN')}

**SCAN Results**: 
{analysis.get('scan_results', 'No scan results available')}

**Best Practices Research**: {analysis.get('best_practices_research', 'No research available')}

**Modularity Violations**:
{analysis.get('modularity_violations', 'None identified')}

**Best Practices Issues**:
{analysis.get('best_practices_issues', 'None identified')}

**Specific Changes Needed**:
{analysis.get('specific_changes_needed', 'None identified')}

**Severity**: {analysis.get('severity', 'UNKNOWN')}

**Actionable Recommendations**: 
{analysis.get('actionable_recommendations', 'None provided')}

---
"""
        try:
            with open(self.report_file, 'a', encoding='utf-8') as f:
                f.write(entry)
        except (IOError, OSError) as e:
            print(f"❌ Failed to append file analysis: {e}", file=sys.stderr)
            raise
    
    def append_summary(self, summary: dict):
        """Append summary information to report"""
        summary_entry = f"""## Scan Summary
**Total Files Scanned**: {summary.get('total_files', 0)}
**Files with Issues**: {summary.get('files_with_issues', 0)}
**Critical Issues**: {summary.get('critical_issues', 0)}
**High Issues**: {summary.get('high_issues', 0)}
**Medium Issues**: {summary.get('medium_issues', 0)}
**Low Issues**: {summary.get('low_issues', 0)}

**Systematic Patterns Identified**:
{summary.get('systematic_patterns', 'None identified')}

---
"""
        try:
            with open(self.report_file, 'a', encoding='utf-8') as f:
                f.write(summary_entry)
        except (IOError, OSError) as e:
            print(f"❌ Failed to append summary: {e}", file=sys.stderr)
            raise
    
    def get_report_path(self) -> str:
        """Return the path to the current report file"""
        return str(self.report_file)


def create_writer(report_dir: str, report_name: str) -> EfficientReportWriter:
    """Factory function to create an EfficientReportWriter"""
    return EfficientReportWriter(report_dir, report_name)


if __name__ == "__main__":
    import sys
    
    # Parse command-line arguments
    report_dir = sys.argv[1] if len(sys.argv) > 1 else "Logs/Reviewer/BP/App"
    report_name = sys.argv[2] if len(sys.argv) > 2 else "SCAN-REPORT"
    
    # Create writer with provided arguments
    writer = create_writer(report_dir, report_name)
    
    # Test file analysis
    test_analysis = {
        'type': 'Python file',
        'complexity': 'Medium',
        'compliance_status': 'PASS',
        'scan_results': '- Good: Proper structure\n- Issues: Minor formatting',
        'best_practices_research': 'Follows PEP 8 standards',
        'modularity_violations': 'None',
        'best_practices_issues': 'Minor formatting improvements needed',
        'specific_changes_needed': '1. Fix formatting\n2. Add docstrings',
        'severity': 'LOW',
        'actionable_recommendations': '- Add docstrings\n- Improve formatting'
    }
    
    writer.append_file_analysis(1, "test_file.py", test_analysis)
    print(f"Report created at: {writer.get_report_path()}")