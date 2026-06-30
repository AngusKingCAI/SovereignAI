# /verify Workflow

Run after every file edit during plan execution.

## Steps

1. Syntax check edited file:
   - Python: `.venv/Scripts/python.exe -c "import ast; ast.parse(open('<file>').read())"`
   - JavaScript: `node --check <file>`
   - HTML: `.venv/Scripts/python.exe -c "from html.parser import HTMLParser; HTMLParser().feed(open('<file>').read())"`
   - CSS: `.venv/Scripts/python.exe -c "import tinycss2; list(tinycss2.parse_stylesheet(open('<file>').read()))"`
   - JSON: `.venv/Scripts/python.exe -c "import json; json.load(open('<file>'))"`
   - YAML: `.venv/Scripts/python.exe -c "import yaml; yaml.safe_load(open('<file>'))"`
   - TOML: `.venv/Scripts/python.exe -c "import tomllib; tomllib.load(open('<file>', 'rb'))"`
   - Markdown: skip
   
   STOP on syntax error. Fix before proceeding.

2. Ruff on edited file (Python only): `.venv/Scripts/ruff.exe check <file>` — if auto-fixable: `ruff check --fix <file>` and re-verify. If not: STOP.

3. Report: `<file>: OK` or `<file>: FAIL — <error>`
