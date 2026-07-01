import subprocess
import sys
from pathlib import Path


def test_check_tracing_synthetic_violator():
    violator = Path("sovereignai/test_violator.py")
    violator.write_text("""
def bad_function():
    with open("test.txt", "w") as f:
        f.write("test")
""")
    
    result = subprocess.run(
        [sys.executable, "scripts/ar_checks/check_tracing.py"],
        capture_output=True,
        text=True,
        cwd=Path.cwd()
    )
    
    violator.unlink()
    assert result.returncode != 0
    assert "bad_function" in result.stdout


def test_check_tracing_clean_function():
    clean = Path("sovereignai/test_clean.py")
    clean.write_text("""
class TraceEmitter:
    def emit(self):
        pass

def good_function():
    trace = TraceEmitter()
    trace.emit()
""")
    
    result = subprocess.run(
        [sys.executable, "scripts/ar_checks/check_tracing.py"],
        capture_output=True,
        text=True,
        cwd=Path.cwd()
    )
    
    clean.unlink()
    assert result.returncode == 0


def test_check_tracing_allowlist():
    allowlisted = Path("sovereignai/test_allowlisted.py")
    allowlisted.write_text("""
def allowlisted_func():
    with open("test.txt", "w") as f:
        f.write("test")
""")
    
    allowlist_path = Path("scripts/ar_checks/check_tracing_allowlist.txt")
    original = allowlist_path.read_text() if allowlist_path.exists() else ""
    allowlist_path.write_text(original + "\ntest_allowlisted.py:allowlisted_func")
    
    result = subprocess.run(
        [sys.executable, "scripts/ar_checks/check_tracing.py"],
        capture_output=True,
        text=True,
        cwd=Path.cwd()
    )
    
    allowlist_path.write_text(original)
    allowlisted.unlink()
    assert result.returncode == 0


def test_check_tracing_missing_allowlist():
    allowlist_path = Path("scripts/ar_checks/check_tracing_allowlist.txt")
    original = allowlist_path.read_text() if allowlist_path.exists() else ""
    allowlist_path.unlink()
    
    temp_violator = Path("sovereignai/test_temp_violator.py")
    temp_violator.write_text("""
def temp_func():
    with open("test.txt", "w") as f:
        f.write("test")
""")
    
    result = subprocess.run(
        [sys.executable, "scripts/ar_checks/check_tracing.py"],
        capture_output=True,
        text=True,
        cwd=Path.cwd()
    )
    
    temp_violator.unlink()
    if original:
        allowlist_path.write_text(original)
    assert result.returncode != 0


def test_check_placeholders_violator():
    violator = Path("sovereignai/test_placeholder_violator.py")
    violator.write_text("""
def bad_function():
    pass  # placeholder
""")
    
    result = subprocess.run(
        [sys.executable, "scripts/ar_checks/check_placeholders.py"],
        capture_output=True,
        text=True,
        cwd=Path.cwd()
    )
    
    violator.unlink()
    assert result.returncode != 0


def test_check_placeholders_clean():
    clean = Path("sovereignai/test_placeholder_clean.py")
    clean.write_text("""
def good_function():
    return 42
""")
    
    result = subprocess.run(
        [sys.executable, "scripts/ar_checks/check_placeholders.py"],
        capture_output=True,
        text=True,
        cwd=Path.cwd()
    )
    
    clean.unlink()
    assert result.returncode == 0


def test_check_placeholders_todo_allowed_in_tests():
    test_file = Path("tests/test_placeholder_todo.py")
    test_file.write_text("""
def test_something():
    TODO: implement this
    pass
""")
    
    result = subprocess.run(
        [sys.executable, "scripts/ar_checks/check_placeholders.py"],
        capture_output=True,
        text=True,
        cwd=Path.cwd()
    )
    
    test_file.unlink()
    assert result.returncode == 0


def test_spec_match_missing_in_diff():
    result = subprocess.run(
        [sys.executable, "scripts/ar_checks/spec_match.py", "prompts/plan-16-Rev9.md"],
        capture_output=True,
        text=True,
        cwd=Path.cwd()
    )
    assert result.returncode != 0
    assert "Missing in diff" in result.stdout
