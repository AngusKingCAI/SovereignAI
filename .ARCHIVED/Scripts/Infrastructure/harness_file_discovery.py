#!/usr/bin/env python3
"""
Harness Governance File Discovery Script

Discovers all harness governance files for comprehensive best practice scanning.
This script excludes App/, Logs/, Plans/, Docs/, and .git/ directories to focus
on actual governance files rather than documentation and application code.

BP Research: 2026 governance file discovery best practices
- Focus on governance files: Rules/, Workflow/, Agents/, Scripts/, .devin/
- Exclude documentation: Docs/, Logs/, Plans/
- Exclude application code: App/
- Exclude version control: .git/
- Validate file types: Only scan governance-relevant file types
"""

import os
import sys
from pathlib import Path
from typing import List, Set, Dict
import json


class HarnessFileDiscovery:
    """Discovers harness governance files for best practice scanning."""

    def __init__(self, target_directory: str, exclude_patterns: List[str] = None):
        """
        Initialize file discovery for harness governance.

        Args:
            target_directory: Root directory to scan (e.g., "C:/SovereignAI")
            exclude_patterns: List of directory patterns to exclude
        """
        self.target_directory = Path(target_directory)
        # Default exclude patterns for harness governance scanning
        self.exclude_patterns = exclude_patterns or [
            ".git/*",          # Version control
            "App/*",           # Application code
            "Logs/*",          # Log files and sessions
            "Plans/*",         # Implementation plans
            "Docs/*",          # Documentation
            ".Archived/*",     # Archived logs
            "__pycache__/*",   # Python cache
            "*.pyc",           # Python bytecode
            ".pytest_cache/*", # Test cache
            "*.egg-info/*",    # Python package metadata
            "node_modules/*",  # Node.js dependencies
        ]
        self.discovered_files = set()
        self.discovered_directories = set()
        self.file_stats = {
            "total_files": 0,
            "by_extension": {},
            "by_directory": {},
            "excluded_files": 0
        }

    def _is_excluded(self, path: str) -> bool:
        """
        Check if a path should be excluded from scanning.

        Args:
            path: File or directory path to check

        Returns:
            True if path should be excluded, False otherwise
        """
        normalized_path = path.replace("\\", "/")
        
        for pattern in self.exclude_patterns:
            normalized_pattern = pattern.replace("\\", "/")
            
            if pattern.endswith("*"):
                # Wildcard pattern - check if pattern appears in path
                pattern_prefix = pattern[:-1].replace("\\", "/")
                if f"/{pattern_prefix}/" in normalized_path or normalized_path.startswith(f"{pattern_prefix}/"):
                    return True
            else:
                # Exact pattern match - check if pattern appears in path
                if f"/{normalized_pattern}/" in normalized_path or normalized_path.endswith(f"/{normalized_pattern}"):
                    return True
        
        return False

    def _is_governance_file(self, file_path: Path) -> bool:
        """
        Check if a file is a governance file worth scanning.

        Args:
            file_path: Path to the file

        Returns:
            True if file is governance-relevant, False otherwise
        """
        # Focus on governance-relevant file types
        governance_extensions = {
            '.md',      # Markdown governance files
            '.json',    # Configuration files
            '.yaml',    # YAML configuration
            '.yml',     # YAML configuration
            '.py',      # Python scripts
            '.sh',      # Shell scripts
            '.txt',     # Text files
        }
        
        # Include files without extension (likely governance)
        if not file_path.suffix:
            return True
            
        return file_path.suffix.lower() in governance_extensions

    def discover_governance_files(self) -> bool:
        """
        Discover all governance files in the target directory.

        Returns:
            True if discovery successful, False otherwise
        """
        try:
            self.discovered_files = set()
            self.discovered_directories = set()
            
            # Discover all files recursively with exclusion during discovery
            for item in self.target_directory.rglob('*'):
                if item.is_dir():
                    # Check if directory should be excluded
                    if not self._is_excluded(str(item)):
                        self.discovered_directories.add(str(item.resolve()))
                elif item.is_file():
                    file_path = str(item.resolve())
                    
                    # Check if file's parent directory should be excluded
                    if self._is_excluded(str(item.parent)):
                        self.file_stats["excluded_files"] += 1
                        continue
                    
                    # Check if file itself should be excluded
                    if self._is_excluded(file_path):
                        self.file_stats["excluded_files"] += 1
                        continue
                    
                    # Check if file is governance-relevant
                    if self._is_governance_file(item):
                        self.discovered_files.add(file_path)
                        
                        # Track statistics
                        ext = item.suffix.lower() if item.suffix else 'no_extension'
                        self.file_stats["by_extension"][ext] = self.file_stats["by_extension"].get(ext, 0) + 1
                        
                        # Track by directory
                        parent_dir = str(item.parent)
                        self.file_stats["by_directory"][parent_dir] = self.file_stats["by_directory"].get(parent_dir, 0) + 1

            self.file_stats["total_files"] = len(self.discovered_files)
            return True

        except Exception as e:
            print(f"Discovery error: {e}", file=sys.stderr)
            return False

    def get_sorted_files(self) -> List[str]:
        """
        Get discovered files sorted alphabetically by full path.

        Returns:
            Sorted list of file paths
        """
        return sorted(self.discovered_files)

    def generate_report(self) -> str:
        """
        Generate human-readable discovery report.

        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 60)
        report.append("HARNESS GOVERNANCE FILE DISCOVERY REPORT")
        report.append("=" * 60)
        report.append(f"Target Directory: {self.target_directory}")
        report.append(f"Total Governance Files: {self.file_stats['total_files']}")
        report.append(f"Excluded Files: {self.file_stats['excluded_files']}")
        report.append(f"Total Directories: {len(self.discovered_directories)}")
        report.append("")
        
        report.append("Files by Extension:")
        for ext, count in sorted(self.file_stats["by_extension"].items()):
            report.append(f"  {ext}: {count}")
        report.append("")
        
        report.append("Files by Directory:")
        for directory, count in sorted(self.file_stats["by_directory"].items()):
            report.append(f"  {directory}: {count}")
        report.append("")
        
        report.append("Exclude Patterns:")
        for pattern in self.exclude_patterns:
            report.append(f"  - {pattern}")
        report.append("")
        
        report.append("=" * 60)
        return "\n".join(report)

    def save_file_list(self, output_file: str):
        """
        Save discovered file list to output file.

        Args:
            output_file: Path to save file list
        """
        sorted_files = self.get_sorted_files()
        
        with open(output_file, 'w') as f:
            json.dump({
                "target_directory": str(self.target_directory.resolve()),
                "exclude_patterns": self.exclude_patterns,
                "total_files": len(sorted_files),
                "file_list": sorted_files,
                "statistics": self.file_stats
            }, f, indent=2)


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Discover harness governance files for best practice scanning"
    )
    parser.add_argument(
        "target_directory",
        help="Target directory to scan (e.g., C:/SovereignAI)",
        default="C:/SovereignAI"
    )
    parser.add_argument(
        "--output",
        help="Path to save discovered file list as JSON",
        default=None
    )
    parser.add_argument(
        "--exclude",
        help="Comma-separated list of directory patterns to exclude",
        default=".git/*,App/*,Logs/*,Plans/*,Docs/*,.Archived/*"
    )

    args = parser.parse_args()

    # Parse exclude patterns
    exclude_patterns = [p.strip() for p in args.exclude.split(',')] if args.exclude else None

    # Initialize discovery
    discovery = HarnessFileDiscovery(args.target_directory, exclude_patterns)

    # Discover governance files
    if not discovery.discover_governance_files():
        print("Failed to discover governance files", file=sys.stderr)
        sys.exit(1)

    # Print report
    print(discovery.generate_report())

    # Save file list if requested
    if args.output:
        discovery.save_file_list(args.output)
        print(f"\nFile list saved to: {args.output}")

    sys.exit(0)


if __name__ == "__main__":
    main()