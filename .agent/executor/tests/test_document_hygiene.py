import re
from pathlib import Path


def test_landmines_no_na_stubs_above_headers() -> None:
    """Verify LANDMINES.md has no 'N/A -- no new patterns' stubs above ## L{n} headers."""
    landmines_path = Path("LANDMINES.md")
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
    landmines_path = Path("LANDMINES.md")
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
    landmines_path = Path("LANDMINES.md")
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
    """Verify PLANS.md Completed Prompts table includes recent key prompts."""
    plans_path = Path("PLANS.md")

    plans_content = plans_path.read_text(encoding="utf-8")

    table_prompts = set()
    for match in re.finditer(r"\| prompt-([\d.]+)", plans_content):
        table_prompts.add(match.group(1))

    required_prompts = {"20.8", "20.9", "20.9.1", "20.9.2"}
    missing = required_prompts - table_prompts
    assert not missing, f"Required prompts missing from PLANS.md table: {sorted(missing)}"


def test_plans_baseline_reconciliation_completeness() -> None:
    """Verify PLANS.md Baseline Reconciliation Notes include recent key prompts."""
    plans_path = Path("PLANS.md")

    plans_content = plans_path.read_text(encoding="utf-8")

    baseline_prompts = set()
    for match in re.finditer(r"\*\*Plan ([\d.]+)\*\*:", plans_content):
        baseline_prompts.add(match.group(1))

    required_prompts = {"20.8", "20.9", "20.9.1", "20.9.2"}
    missing = required_prompts - baseline_prompts
    assert not missing, (
        f"Required prompts missing from PLANS.md baseline reconciliation: {sorted(missing)}"
    )
