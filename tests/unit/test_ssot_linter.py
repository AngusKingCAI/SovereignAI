# tests/unit/test_ssot_linter.py
import subprocess
import pytest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
LINTER = PROJECT_ROOT / "scripts" / "validation" / "lint_ssot_duplicates.py"

def test_ssot_linter_flags_duplicates(tmp_path, monkeypatch):
    """The SSOT linter must flag two cards with identical rule statements."""
    # Create two cards with the same statement
    cards_dir = tmp_path / "governance" / "policy-cards" / "shared"
    cards_dir.mkdir(parents=True)
    duplicate_statement = "Every file must have valid frontmatter"
    (cards_dir / "card1.yaml").write_text(f"""
id: SHARED-001
version: "1.0.0"
tier: compliance
severity: blocking
agent: all
domain: frontmatter
rule:
  statement: "{duplicate_statement}"
  rationale: "test"
enforceable_via: validator
check:
  type: require_field
  params: {{fields: [id]}}
test_cases:
  - name: pass
    input: "valid.md"
    expected: pass
  - name: fail
    input: "invalid.md"
    expected: fail
""")
    (cards_dir / "card2.yaml").write_text(f"""
id: SHARED-002
version: "1.0.0"
tier: compliance
severity: blocking
agent: all
domain: frontmatter
rule:
  statement: "{duplicate_statement}"
  rationale: "test duplicate"
enforceable_via: validator
check:
  type: require_field
  params: {{fields: [id]}}
test_cases:
  - name: pass
    input: "valid.md"
    expected: pass
  - name: fail
    input: "invalid.md"
    expected: fail
""")
    
    # Run linter from temp directory
    result = subprocess.run(
        ["python", str(LINTER)],
        capture_output=True,
        text=True,
        cwd=str(tmp_path),
    )
    assert result.returncode == 1, "Linter must exit 1 on duplicates"
    assert "SSOT violation" in result.stdout

def test_ssot_linter_passes_unique_statements():
    """The SSOT linter must pass when all statements are unique."""
    result = subprocess.run(
        ["python", str(LINTER)],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
    )
    # On the real repo, all statements should be unique
    assert result.returncode == 0, f"Linter failed on real repo: {result.stdout}"
