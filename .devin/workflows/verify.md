# /verify Workflow

Run after every file edit during plan execution.

## Steps

1. Syntax check the edited file:
   - Python: `python -c "import ast; ast.parse(open('<file>.py').read())"`
   - JSON: `python -c "import json; json.load(open('<file>'))"`
   - YAML: `python -c "import yaml; yaml.safe_load(open('<file>'))"`
   - TOML: `python -c "import tomllib; tomllib.load(open('<file>', 'rb'))"`
   - Markdown: skip
   
   If syntax error, STOP. Fix before proceeding.

2. Run ruff on the edited file:
   ```
   ruff check <file>
   ```
   If auto-fixable, apply `ruff check --fix <file>` and re-verify. If not auto-fixable, STOP.

3. Report:
   ```
   <file>: OK
   ```
   Or:
   ```
   <file>: FAIL — <error>
   ```
