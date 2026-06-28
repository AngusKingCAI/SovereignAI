# /verify Workflow

Run after every file edit during plan execution.

## Steps

1. Syntax check the edited file (use absolute venv path per OR46):
   - Python: `.venv/Scripts/python.exe -c "import ast; ast.parse(open('<file>.py').read())"`
   - JSON: `.venv/Scripts/python.exe -c "import json; json.load(open('<file>'))"`
   - YAML: `.venv/Scripts/python.exe -c "import yaml; yaml.safe_load(open('<file>'))"` (requires PyYAML — install via `.venv/Scripts/pip.exe install pyyaml` if missing)
   - TOML: `.venv/Scripts/python.exe -c "import tomllib; tomllib.load(open('<file>', 'rb'))"`
   - Markdown: skip
   
   If syntax error, STOP. Fix before proceeding.

2. Run ruff on the edited file (use absolute venv path per OR46):
   ```
   .venv/Scripts/ruff.exe check <file>
   ```
   If auto-fixable, apply `.venv/Scripts/ruff.exe check --fix <file>` and re-verify. If not auto-fixable, STOP.

3. Report:
   ```
   <file>: OK
   ```
   Or:
   ```
   <file>: FAIL — <error>
   ```
