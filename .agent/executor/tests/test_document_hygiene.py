import re
from pathlib import Path


def test_landmines_no_na_stubs_above_headers() -> None:
    """Verify LANDMINES.md has no 'N/A -- no new patterns' stubs above ## L{n} headers."""
    landmines_path = Path(".agent/shared/LANDMINES.md")
    content = landmines_path.read_text(encoding="utf-8")
    lines = content.split("\n")

    for i, line in enumerate(lines):
        if re.match(r"^## L\d+", line):
            prev_line = lines[i - 1] if i > 0 else ""
            assert "N/A -- no new patterns" not in prev_line, (
                f"Found 'N/A -- no new patterns' stub above header at line {i + 1}: {line}"
            )


def test_landmines_separator_only_between_entries() -> None:
    """Verify LANDMINES.md has '---' separator only between entries, not before headers."""
    landmines_path = Path(".agent/shared/LANDMINES.md")
    content = landmines_path.read_text(encoding="utf-8")
    lines = content.split("\n")

    for i, line in enumerate(lines):
        if re.match(r"^## L\d+", line):
            prev_line = lines[i - 1] if i > 0 else ""
            assert prev_line != "---", (
                f"Found '---' separator before header at line {i + 1}: {line}"
            )


def test_landmines_header_followed_by_description() -> None:
    """Verify each ## L{n} header is followed by description, not separator."""
    landmines_path = Path(".agent/shared/LANDMINES.md")
    content = landmines_path.read_text(encoding="utf-8")
    lines = content.split("\n")

    for i, line in enumerate(lines):
        if re.match(r"^## L\d+", line):
            next_line = lines[i + 1] if i + 1 < len(lines) else ""
            assert next_line != "---", (
                f"Header at line {i + 1} followed by separator instead of description"
            )
            assert next_line.strip() != "" or (i + 2 < len(lines) and lines[i + 2].strip() != ""), (
                f"Header at line {i + 1} not followed by description (allowing one blank line)"
            )


def test_plans_table_completeness() -> None:
    """Verify PLANS.md exists and has recent plan entries."""
    plans_path = Path(".agent/shared/PLANS.md")
    assert plans_path.exists(), "PLANS.md not found"

    plans_content = plans_path.read_text(encoding="utf-8")
    assert "## Recent History" in plans_content, "Recent History section missing"
    assert "Plan 25.3" in plans_content, "Recent plan not documented"


def test_plans_baseline_reconciliation_completeness() -> None:
    """Verify PLANS.md has baseline section with recent entries."""
    plans_path = Path(".agent/shared/PLANS.md")
    assert plans_path.exists(), "PLANS.md not found"

    plans_content = plans_path.read_text(encoding="utf-8")
    assert "## Current Baseline" in plans_content, "Current Baseline section missing"
    assert "plan-25.3-Rev1" in plans_content, "Recent baseline plan not documented"
