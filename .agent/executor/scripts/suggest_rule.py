#!/usr/bin/env python3
"""Executor rule suggestion tool.

Run this when encountering a recurring error pattern not covered by existing rules.
Generates structured rule suggestions for Architect review.
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path


def generate_suggestion(
    rule_type: str,
    trigger: str,
    frequency: str,
    rule_text: str,
    detection_method: str,
    affected_files: list[str],
    suggestions_dir: Path,
) -> Path:
    """Generate a structured rule suggestion file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"suggestion_{rule_type.lower()}_{timestamp}.md"
    output_path = suggestions_dir / filename

    suggestion_content = f"""# Rule Suggestion — {rule_type}

**Generated**: {timestamp}
**Type**: {rule_type}
**Status**: PENDING_REVIEW

---

## Trigger

{trigger}

---

## Frequency

{frequency}

---

## Proposed Rule

{rule_text}

---

## Detection Method

{detection_method}

---

## Affected Files

{chr(10).join(f"- {file}" for file in affected_files)}

---

## Implementation Notes

*Add any additional context for the Architect here.*

---

## Lifecycle

This suggestion will be reviewed by the Architect during the next Round Table
or dedicated rule review. Implementation follows DEBT.md workflow per
.agent/shared/RULE_LIFECYCLE.md.
Possible outcomes:
- **ACCEPT**: Rule assigned ID, check script written, integrated into workflow
- **REJECT**: Reason documented, suggestion archived
- **DEFER**: Added to DEBT.md with target plan
"""

    output_path.write_text(suggestion_content, encoding="utf-8")
    return output_path


def main() -> int:
    """Main entry point for rule suggestion tool."""
    parser = argparse.ArgumentParser(
        description="Generate structured rule suggestions for Architect review"
    )
    parser.add_argument(
        "--type",
        required=True,
        choices=["OR", "AR", "Landmine"],
        help="Type of rule to suggest"
    )
    parser.add_argument(
        "--trigger",
        required=True,
        help="What caused this suggestion (error pattern, failure, etc.)"
    )
    parser.add_argument(
        "--frequency",
        required=True,
        help="How often this pattern occurred (e.g., '3 times in last 2 plans')"
    )
    parser.add_argument(
        "--rule",
        required=True,
        help="Proposed rule text"
    )
    parser.add_argument(
        "--detection",
        required=True,
        help="How to detect this programmatically (script logic, grep pattern, etc.)"
    )
    parser.add_argument(
        "--files",
        nargs="+",
        required=True,
        help="Affected files (space-separated list)"
    )
    parser.add_argument(
        "--suggestions-dir",
        type=Path,
        default=Path(__file__).parent.parent / "suggestions",
        help="Directory to write suggestion files (default: .agent/executor/suggestions/)"
    )

    args = parser.parse_args()

    # Ensure suggestions directory exists
    args.suggestions_dir.mkdir(parents=True, exist_ok=True)

    # Generate suggestion
    output_path = generate_suggestion(
        rule_type=args.type,
        trigger=args.trigger,
        frequency=args.frequency,
        rule_text=args.rule,
        detection_method=args.detection,
        affected_files=args.files,
        suggestions_dir=args.suggestions_dir,
    )

    print(f"Rule suggestion written to: {output_path}")
    print("Awaiting Architect review during next Round Table or dedicated rule review.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
