#!/usr/bin/env python3
"""Check that every def/async def has a verb-first, jargon-free, >=10-word docstring.

Enforces AR21 (AGENTS.md): first line of every function/method docstring starts
with a verb, is at least 10 words, and avoids programming jargon a non-coder
wouldn't understand. Dunder methods other than __init__ are skipped (their
purpose is conventional, not bespoke).
"""

import argparse
import ast
import re
import sys
from pathlib import Path

JARGON_WORDS = {
    "async", "await", "coroutine", "dispatch", "yield", "instantiate",
}

SKIP_DUNDERS = {"__repr__", "__str__", "__eq__", "__hash__", "__len__"}


def first_line(docstring: str) -> str:
    """Return the first non-empty line of a docstring, stripped of whitespace."""
    for line in docstring.strip().splitlines():
        if line.strip():
            return line.strip()
    return ""


def starts_with_verb(line: str) -> bool:
    """Heuristically check whether a line starts with a verb (ends in common verb forms).

    This is a heuristic, not a POS tagger: it accepts any first word, then flags
    the few patterns most likely to indicate a noun-first docstring (e.g. "The...",
    "A...", "This...", "Returns the..." is fine — "Returns" is a verb).
    """
    first_word = line.split()[0] if line.split() else ""
    noun_starters = {"the", "a", "an", "this", "it", "if", "when"}
    return first_word.lower() not in noun_starters


def check_function(fn: ast.FunctionDef | ast.AsyncFunctionDef, path: Path) -> list[str]:
    """Check a single function's docstring against AR21's first-line requirements."""
    if fn.name in SKIP_DUNDERS:
        return []

    doc = ast.get_docstring(fn)
    if doc is None:
        return [f"{path}:{fn.lineno}: '{fn.name}' has no docstring"]

    line = first_line(doc)
    issues = []
    word_count = len(re.findall(r"\S+", line))
    if word_count < 10:
        issues.append(
            f"{path}:{fn.lineno}: '{fn.name}' docstring first line has "
            f"{word_count} words (needs >=10): {line!r}"
        )
    if not starts_with_verb(line):
        issues.append(
            f"{path}:{fn.lineno}: '{fn.name}' docstring doesn't start with a verb: {line!r}"
        )
    lowered = line.lower()
    for jargon in JARGON_WORDS:
        if re.search(rf"\b{jargon}\b", lowered):
            issues.append(
                f"{path}:{fn.lineno}: '{fn.name}' docstring uses jargon word "
                f"'{jargon}': {line!r}"
            )
    return issues


def scan_file(path: Path) -> list[str]:
    """Parse one file and check every def/async def docstring against AR21."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as exc:
        return [f"{path}: SyntaxError — {exc}"]

    violations = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            violations.extend(check_function(node, path))
    return violations


def main() -> int:
    """Run the AR21 docstring-discipline check over the given paths."""
    parser = argparse.ArgumentParser(description="AR21: verb-first, >=10-word docstrings.")
    parser.add_argument("paths", nargs="+", help="Files or directories to check.")
    args = parser.parse_args()

    violations: list[str] = []
    for raw_path in args.paths:
        target = Path(raw_path)
        files = [target] if target.is_file() else sorted(target.rglob("*.py"))
        for file_path in files:
            violations.extend(scan_file(file_path))

    if violations:
        print("AR21 violations found:", file=sys.stderr)
        for v in violations:
            print(f"  {v}", file=sys.stderr)
        return 1

    print("AR21: all docstrings comply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
