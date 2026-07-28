#!/usr/bin/env python3
"""
File Discovery Validation Script

Validates comprehensive directory traversal to ensure no files are missed
during scanning workflows. Pre-flight check for code scanning operations.

BP Research: 2026 code scanner file discovery validation best practices
- Establish baseline of expected directory structure
- Cross-check discovered files against expected structure
- Fail-fast if directory structure doesn't match expected baseline
"""

import os
import sys
from pathlib import Path
from typing import List, Set, Dict
import json


class FileDiscoveryValidator:
    """Validates comprehensive file discovery for code scanning workflows."""

    def __init__(self, target_directory: str, exclude_patterns: List[str] = None):
        """
        Initialize validator with target directory.

        Args:
            target_directory: Root directory to validate (e.g., "C:/SovereignAI/App")
            exclude_patterns: List of directory patterns to exclude from validation (e.g., [".git/objects/*"])
        """
        self.target_directory = Path(target_directory)
        self.exclude_patterns = exclude_patterns or [".git/objects/*"]
        self.expected_directories = set()
        self.discovered_files = set()
        self.discovered_directories = set()
        self.validation_results = {
            "target_directory": str(self.target_directory),
            "expected_directories": [],
            "discovered_directories": [],
            "missing_directories": [],
            "total_files_discovered": 0,
            "validation_passed": False,
            "errors": []
        }

    def _filter_excluded_directories(self, directories: Set[str]) -> Set[str]:
        """
        Filter out directories matching exclude patterns.

        Args:
            directories: Set of directory paths to filter

        Returns:
            Filtered set of directories excluding matched patterns
        """
        filtered = set()
        for directory in directories:
            exclude = False
            for pattern in self.exclude_patterns:
                # Normalize path separators for pattern matching
                normalized_dir = directory.replace("\\", "/")
                normalized_pattern = pattern.replace("\\", "/")
                
                # Simple pattern matching - check if pattern appears in path
                if normalized_pattern.replace("*", "") in normalized_dir:
                    exclude = True
                    break
            if not exclude:
                filtered.add(directory)
        return filtered

    def set_expected_directories(self, directories: List[str]):
        """
        Set expected directory structure based on known App/ directory layout.

        Args:
            directories: List of expected directory paths relative to target
        """
        # Normalize paths for cross-platform comparison
        normalized_dirs = [str(Path(d).resolve()) for d in directories]
        self.expected_directories = set(normalized_dirs)
        self.validation_results["expected_directories"] = sorted(normalized_dirs)

    def discover_actual_structure(self) -> bool:
        """
        Discover actual directory structure using Python pathlib for cross-platform compatibility.

        Returns:
            True if discovery successful, False otherwise
        """
        try:
            # Use pathlib for cross-platform directory discovery
            self.discovered_directories = set()
            self.discovered_files = set()

            # Discover all directories recursively
            for dirpath in self.target_directory.rglob('*'):
                if dirpath.is_dir():
                    # Normalize path for cross-platform comparison
                    self.discovered_directories.add(str(dirpath.resolve()))
                elif dirpath.is_file():
                    self.discovered_files.add(str(dirpath.resolve()))

            # Add the root directory itself
            self.discovered_directories.add(str(self.target_directory.resolve()))

            self.validation_results["total_files_discovered"] = len(self.discovered_files)
            self.validation_results["discovered_directories"] = sorted(self.discovered_directories)

            return True

        except Exception as e:
            self.validation_results["errors"].append(f"Discovery error: {e}")
            return False

    def validate_completeness(self) -> bool:
        """
        Validate that all expected directories are present in discovered structure.

        Returns:
            True if validation passes, False otherwise
        """
        if not self.expected_directories:
            # If no expected directories set, auto-discover from actual structure
            # This creates a baseline for future validations
            self.expected_directories = self.discovered_directories
            self.validation_results["expected_directories"] = sorted(self.discovered_directories)
            self.validation_results["errors"].append(
                "No expected directories set - using discovered structure as baseline"
            )
            return True

        # Filter out excluded directories from both sets
        filtered_expected = self._filter_excluded_directories(self.expected_directories)
        filtered_discovered = self._filter_excluded_directories(self.discovered_directories)

        # Check for missing directories
        missing_dirs = filtered_expected - filtered_discovered
        self.validation_results["missing_directories"] = sorted(missing_dirs)

        if missing_dirs:
            self.validation_results["validation_passed"] = False
            self.validation_results["errors"].append(
                f"Missing {len(missing_dirs)} expected directories"
            )
            return False

        self.validation_results["validation_passed"] = True
        return True

    def generate_report(self) -> str:
        """
        Generate human-readable validation report.

        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 60)
        report.append("FILE DISCOVERY VALIDATION REPORT")
        report.append("=" * 60)
        report.append(f"Target Directory: {self.target_directory}")
        report.append(f"Total Files Discovered: {self.validation_results['total_files_discovered']}")
        report.append(f"Expected Directories: {len(self.validation_results['expected_directories'])}")
        report.append(f"Discovered Directories: {len(self.validation_results['discovered_directories'])}")
        report.append(f"Missing Directories: {len(self.validation_results['missing_directories'])}")
        report.append(f"Validation Status: {'PASSED' if self.validation_results['validation_passed'] else 'FAILED'}")
        report.append("")

        if self.validation_results["missing_directories"]:
            report.append("MISSING DIRECTORIES:")
            for missing_dir in self.validation_results["missing_directories"]:
                report.append(f"  - {missing_dir}")
            report.append("")

        if self.validation_results["errors"]:
            report.append("ERRORS:")
            for error in self.validation_results["errors"]:
                report.append(f"  - {error}")
            report.append("")

        if self.validation_results["validation_passed"]:
            report.append("VALIDATION PASSED - Directory structure is complete")
        else:
            report.append("VALIDATION FAILED - Missing directories detected")

        report.append("=" * 60)
        return "\n".join(report)

    def save_baseline(self, output_file: str):
        """
        Save current discovered structure as baseline for future validations.

        Args:
            output_file: Path to save baseline JSON file
        """
        baseline = {
            "target_directory": str(self.target_directory.resolve()),
            "expected_directories": sorted(self.discovered_directories),
            "total_files_baseline": self.validation_results["total_files_discovered"],
            "created_timestamp": self.validation_results.get("timestamp", "unknown")
        }

        with open(output_file, 'w') as f:
            json.dump(baseline, f, indent=2)

    def load_baseline(self, baseline_file: str) -> bool:
        """
        Load expected directory structure from baseline file.

        Args:
            baseline_file: Path to baseline JSON file

        Returns:
            True if baseline loaded successfully, False otherwise
        """
        try:
            with open(baseline_file, 'r') as f:
                baseline = json.load(f)

            # Normalize paths for cross-platform comparison
            baseline_target = str(Path(baseline["target_directory"]).resolve())
            current_target = str(self.target_directory.resolve())

            if baseline_target != current_target:
                self.validation_results["errors"].append(
                    f"Baseline target directory mismatch: {baseline_target} vs {current_target}"
                )
                return False

            # Normalize expected directories
            normalized_dirs = [str(Path(d).resolve()) for d in baseline["expected_directories"]]
            self.expected_directories = set(normalized_dirs)
            self.validation_results["expected_directories"] = normalized_dirs
            return True

        except Exception as e:
            self.validation_results["errors"].append(f"Failed to load baseline: {e}")
            return False


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate file discovery for comprehensive directory coverage"
    )
    parser.add_argument(
        "target_directory",
        help="Target directory to validate (e.g., C:/SovereignAI/App)"
    )
    parser.add_argument(
        "--baseline",
        help="Path to baseline JSON file for expected structure",
        default=None
    )
    parser.add_argument(
        "--create-baseline",
        help="Create baseline file from current structure",
        default=None
    )
    parser.add_argument(
        "--expected-dirs",
        help="Comma-separated list of expected directories",
        default=None
    )
    parser.add_argument(
        "--exclude",
        help="Comma-separated list of directory patterns to exclude (e.g., .git/objects/*)",
        default=".git/objects/*"
    )

    args = parser.parse_args()

    # Parse exclude patterns
    exclude_patterns = [p.strip() for p in args.exclude.split(',')] if args.exclude else None

    # Initialize validator with exclude patterns
    validator = FileDiscoveryValidator(args.target_directory, exclude_patterns)

    # Load baseline if provided
    if args.baseline:
        if not validator.load_baseline(args.baseline):
            print(f"Failed to load baseline: {args.baseline}")
            sys.exit(1)

    # Set expected directories if provided
    if args.expected_dirs:
        expected_dirs = [d.strip() for d in args.expected_dirs.split(',')]
        validator.set_expected_directories(expected_dirs)

    # Discover actual structure
    if not validator.discover_actual_structure():
        print("Failed to discover directory structure")
        sys.exit(1)

    # Create baseline if requested
    if args.create_baseline:
        validator.save_baseline(args.create_baseline)
        print(f"Baseline created: {args.create_baseline}")
        sys.exit(0)

    # Validate completeness
    if not validator.validate_completeness():
        print(validator.generate_report())
        sys.exit(1)

    # Print success report
    print(validator.generate_report())
    sys.exit(0)


if __name__ == "__main__":
    main()