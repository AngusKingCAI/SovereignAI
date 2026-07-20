#!/usr/bin/env python3
"""Syntax verification for multiple file types. Consolidates verify/SKILL.md Step 1 checks."""

import ast
import json
import sys
from html.parser import HTMLParser
from pathlib import Path

try:
    import tomllib
except ImportError:
    tomllib = None

try:
    import yaml
except ImportError:
    yaml = None

try:
    import tinycss2
except ImportError:
    tinycss2 = None


def check_python(file_path: Path) -> tuple[bool, str]:
    """Check Python syntax."""
    try:
        with open(file_path, encoding='utf-8') as f:
            ast.parse(f.read())
        return True, "OK"
    except SyntaxError as e:
        return False, f"{e.lineno}: {e.msg}"


def check_json(file_path: Path) -> tuple[bool, str]:
    """Check JSON syntax."""
    try:
        with open(file_path, encoding='utf-8') as f:
            json.load(f)
        return True, "OK"
    except json.JSONDecodeError as e:
        return False, f"{e.lineno}: {e.msg}"


def check_toml(file_path: Path) -> tuple[bool, str]:
    """Check TOML syntax."""
    try:
        import tomllib
        with open(file_path, 'rb') as f:
            tomllib.load(f)
        return True, "OK"
    except ImportError:
        return False, "tomllib not available (Python <3.11)"
    except Exception as e:
        return False, f"{e}"


def check_yaml(file_path: Path) -> tuple[bool, str]:
    """Check YAML syntax."""
    if yaml is None:
        return False, "PyYAML not installed"
    try:
        with open(file_path, encoding='utf-8') as f:
            yaml.safe_load(f)
        return True, "OK"
    except yaml.YAMLError as e:
        return False, f"{e}"


def check_html(file_path: Path) -> tuple[bool, str]:
    """Check HTML syntax."""
    try:
        with open(file_path, encoding='utf-8') as f:
            HTMLParser().feed(f.read())
        return True, "OK"
    except Exception as e:
        return False, f"{e}"


def check_css(file_path: Path) -> tuple[bool, str]:
    """Check CSS syntax."""
    if tinycss2 is None:
        return False, "tinycss2 not installed"
    try:
        with open(file_path, encoding='utf-8') as f:
            list(tinycss2.parse_stylesheet(f.read()))
        return True, "OK"
    except Exception as e:
        return False, f"{e}"


def check_javascript(file_path: Path) -> tuple[bool, str]:
    """Check JavaScript syntax via node."""
    import subprocess
    try:
        result = subprocess.run(
            ['node', '--check', str(file_path)],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return True, "OK"
        return False, f"Node error: {result.stderr.strip()}"
    except FileNotFoundError:
        return False, "Node not found in PATH"
    except subprocess.TimeoutExpired:
        return False, "Node check timed out"
    except Exception as e:
        return False, f"Node error: {e}"


FILE_CHECKERS = {
    '.py': check_python,
    '.json': check_json,
    '.toml': check_toml,
    '.yaml': check_yaml,
    '.yml': check_yaml,
    '.html': check_html,
    '.htm': check_html,
    '.css': check_css,
    '.js': check_javascript,
}


def main():
    if len(sys.argv) != 2:
        print("Usage: verify_syntax.py <file_path>", file=sys.stderr)
        sys.exit(1)

    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"FAIL: {file_path}: File not found", file=sys.stderr)
        sys.exit(1)

    suffix = file_path.suffix.lower()

    # Skip markdown
    if suffix in ['.md', '.markdown']:
        print(f"{file_path}: OK (Markdown - skipped)")
        sys.exit(0)

    checker = FILE_CHECKERS.get(suffix)
    if not checker:
        print(f"{file_path}: OK (Unknown file type - skipped)")
        sys.exit(0)

    success, message = checker(file_path)
    if success:
        print(f"{file_path}: OK")
        sys.exit(0)
    else:
        print(f"FAIL: {file_path}: {message}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
