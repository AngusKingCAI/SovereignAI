# Gate Validation Scripts

**Purpose**: Deterministic validation scripts for Planner gates per BP and G6.

## Implementation Principle

**BP-Based Design**:
- **Tool-Level Implementation**: Gates implemented as deterministic predicates: `g(tool_name, args, state) → {allow, reject, warn}`
- **Exit Code Blocking**: Hard gates return exit code 0 (pass) or 1 (fail) - fail status blocks proceeding
- **Soft Gate Warnings**: Soft gates return exit code 0 (non-blocking) but output warnings when violated
- **State Validation**: Scripts read current state (files, git status, etc.) and validate against gate conditions
- **No Model Override**: Hard gates cannot be bypassed by prompt injection, adversarial input, or reasoning chains

## Gate Scripts

### Phase 1 Hard Gates (Plan Creation)
- `hg1_requirements_complete.py` - Validate requirements are complete and unambiguous
- `hg2_scope_defined.py` - Validate scope boundaries are clearly defined
- `hg3_dependencies_feasible.py` - Validate dependencies are technically feasible

### Phase 4 Hard Gates (Quality Verification)
- `hg4_sections_complete.py` - Validate all required sections are present
- `hg5_language_clear.py` - Validate plan language is clear and unambiguous
- `hg6_landmines_screened.py` - Validate blocking landmines are addressed

### Phase 5 Hard Gates (Plan Finalization)
- `hg7_compliance_lines_present.py` - Validate all compliance lines are present
- `hg8_paths_valid.py` - Validate all paths are repo-relative
- `hg9_manifest_complete.py` - Validate Executor Manifest is complete

### Phase 6 Hard Gates (Round Table)
- `hg10_critical_findings_addressed.py` - Validate CRITICAL findings are addressed
- `hg11_high_findings_addressed.py` - Validate HIGH findings are addressed
- `hg12_no_blocking_landmines.py` - Validate no blocking landmines present
- `hg13_manifest_present.py` - Validate Executor Manifest is present

### Phase 6 Soft Gates (Round Table - Non-Blocking)
- Soft gates are now in `.Planner/scripts/soft_gates/` directory
- `sg1_score_below_70.py` - Warn if score <70, require documented rationale
- `sg2_score_70_89.py` - Warn if score 70-89, require documented rationale
- `sg3_panelist_majority.py` - Warn if panelist majority not achieved

## Usage Pattern

```bash
# Run all hard gates for current phase
python .Planner/scripts/hard_gates/run_phase_gates.py --phase 1

# Run specific hard gate
python .Planner/scripts/hard_gates/hg1_requirements_complete.py

# Hard gate runner returns exit code 0 (pass) or 1 (fail)
if [ $? -eq 0 ]; then
    echo "Hard gates passed, proceeding with execution"
else
    echo "Hard gates failed, blocking execution"
    exit 1
fi

# Run soft gate (non-blocking, always returns 0)
python .Planner/scripts/soft_gates/sg1_score_below_70.py

# Soft gate always returns 0 (non-blocking) but outputs warnings
echo "Soft gate check completed (warnings do not block execution)"
```

## Script Format

### Hard Gate Script Template

Each hard gate script follows this template:

```python
#!/usr/bin/env python3
"""
Hard Gate HG-{N}: {Gate description}

Returns exit code 0 (pass) or 1 (fail)
"""

import sys
import os
from pathlib import Path

def check_gate_condition():
    """
    Check the specific gate condition.
    Returns True if gate passes, False otherwise.
    """
    # Implement gate-specific validation logic
    pass

def main():
    if check_gate_condition():
        print(f"✅ Gate HG-{N} PASS: {gate description}")
        sys.exit(0)
    else:
        print(f"❌ Gate HG-{N} FAIL: {gate description}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### Soft Gate Script Template

Each soft gate script follows this template (non-blocking):

```python
#!/usr/bin/env python3
"""
Soft Gate SG-{N}: {Gate description}

Returns exit code 0 (always non-blocking) but outputs warnings when violated
"""

import sys
import os
from pathlib import Path

def check_gate_condition():
    """
    Check the specific gate condition.
    Returns True if gate passes, False if violated (non-blocking).
    """
    # Implement gate-specific validation logic
    pass

def main():
    if check_gate_condition():
        print(f"✅ Gate SG-{N} PASS: {gate description}")
        sys.exit(0)  # Always return 0 (non-blocking)
    else:
        print(f"⚠️  Gate SG-{N} WARN: {gate description} - Soft gate violation (non-blocking)")
        print(f"📝 Rationale Required: Document justification for proceeding")
        sys.exit(0)  # Always return 0 (non-blocking)

if __name__ == "__main__":
    main()
```

## Compliance

Post compliance line after each gate check:
`✅ Gate Enforcement PASS: Hard gate {HG-N} validated via validation script`