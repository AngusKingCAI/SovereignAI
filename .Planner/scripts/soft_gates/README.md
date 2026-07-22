# Soft Gate Validation Scripts

**Purpose**: Non-blocking validation scripts for Planner Round Table soft gates per AGENTS.md G6.

## Implementation Principle

**BP-Based Design**:
- **Non-Blocking Implementation**: Soft gates implemented as Python scripts that always return exit code 0
- **Warning Output**: Scripts output warnings when violated with rationale requirements
- **User Decision**: Soft gates provide recommendations but allow user override with proper documentation
- **Monitoring**: Track soft gate violations for pattern analysis and potential hard gate conversion

## Gate Scripts

### Round Table Soft Gates (Phase 6)
- `sg1_score_below_70.py` - Warn if Round Table score <70, require documented rationale
- `sg2_score_70_89.py` - Warn if Round Table score 70-89, require documented rationale
- `sg3_panelist_majority.py` - Warn if panelist majority not achieved, require documented rationale

## Usage Pattern

```bash
# Run soft gate (non-blocking, always returns 0)
python .Planner/scripts/soft_gates/sg1_score_below_70.py

# Soft gate always returns 0 (non-blocking) but outputs warnings
echo "Soft gate check completed (warnings do not block execution)"
```

## Script Format

Each soft gate script follows this template (non-blocking):

```python
#!/usr/bin/env python3
"""
Soft Gate SG-{ID}: {Gate description}

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
        print(f"✅ Gate SG-{ID} PASS: {gate description}")
        sys.exit(0)  # Always return 0 (non-blocking)
    else:
        print(f"⚠️  Gate SG-{ID} WARN: {gate description} - Soft gate violation (non-blocking)")
        print(f"📝 Rationale Required: Document justification for proceeding")
        sys.exit(0)  # Always return 0 (non-blocking)

if __name__ == "__main__":
    main()
```

## Compliance

Post compliance line after each gate check:
`✅ Gate Enforcement PASS: Soft gate {SG-ID} validated via validation script (non-blocking)`
