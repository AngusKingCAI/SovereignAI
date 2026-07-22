#!/usr/bin/env python3
"""
Gate Runner for Planner Phases

Runs all hard gates (blocking) and soft gates (non-blocking) for a specific phase.
Returns exit code 0 (all hard gates pass) or 1 (any hard gate fails).
Soft gates always return 0 but output warnings when violated.
"""

import sys
import subprocess
import argparse
from pathlib import Path

# UTF-8 print helper for Windows console compatibility
def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        # Fallback for console encoding issues
        print(text.encode('ascii', 'ignore').decode('ascii'))

# Hard gate mappings for each phase (blocking)
# Note: Phase 0 is deliberately un-gated (optional batch optimization phase)
PHASE_HARD_GATES = {
    1: ["hg1_requirements_complete.py", "hg2_scope_defined.py", "hg3_dependencies_feasible.py"],
    2: ["hg14_plan_structure_pr6.py"],
    3: ["hg15_path_verification_pr2.py"],
    4: ["hg4_sections_complete.py", "hg5_language_clear.py", "hg6_landmines_screened.py"],
    5: ["hg7_compliance_lines_present.py", "hg8_paths_valid.py", "hg9_manifest_complete.py"],
    6: ["hg10_critical_findings_addressed.py", "hg11_high_findings_addressed.py", "hg12_no_blocking_landmines.py", "hg13_manifest_present.py"]
}

# Soft gate mappings for each phase (non-blocking)
PHASE_SOFT_GATES = {
    6: ["sg1_score_below_70.py", "sg2_score_70_89.py", "sg3_panelist_majority.py"]
}

def run_gate(gate_script, scripts_dir, gate_type="hard", soft_gates_dir=None):
    """Run a single gate script and return whether it passed."""
    # Use appropriate directory based on gate type
    if gate_type == "soft" and soft_gates_dir:
        script_path = soft_gates_dir / gate_script
    else:
        script_path = scripts_dir / gate_script
        
    if not script_path.exists():
        safe_print(f"Gate script not found: {gate_script} - skipping")
        return True  # Don't fail if script doesn't exist yet
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=30
        )
        
        # Print script output
        if result.stdout:
            safe_print(result.stdout.strip())
        
        if gate_type == "hard":
            # Hard gates: exit code 0 = pass, 1 = fail (blocking)
            if result.returncode == 0:
                return True
            else:
                safe_print(f"{gate_script}: FAIL (blocking)")
                if result.stderr:
                    safe_print(f"   Error: {result.stderr}")
                return False
        else:
            # Soft gates: always return 0 (non-blocking), but check for warnings
            if result.returncode == 0:
                return True  # Soft gates always return 0
            else:
                safe_print(f"{gate_script}: Unexpected non-zero exit code (soft gates should always return 0)")
                return True  # Don't block on soft gate errors
    except subprocess.TimeoutExpired:
        safe_print(f"{gate_script}: TIMEOUT")
        return False if gate_type == "hard" else True
    except Exception as e:
        safe_print(f"{gate_script}: ERROR - {e}")
        return False if gate_type == "hard" else True

def run_phase_gates(phase, scripts_dir, soft_gates_dir=None):
    """Run all hard gates (blocking) and soft gates (non-blocking) for a specific phase."""
    if phase not in PHASE_HARD_GATES:
        if phase == 0:
            safe_print(f"Phase 0 is deliberately un-gated (optional batch optimization phase)")
            return True
        safe_print(f"Invalid phase: {phase}")
        return False
    
    # Run hard gates first (blocking)
    hard_gates = PHASE_HARD_GATES[phase]
    safe_print(f"Running {len(hard_gates)} hard gates for Phase {phase}...")
    
    all_hard_passed = True
    for gate_script in hard_gates:
        if not run_gate(gate_script, scripts_dir, gate_type="hard"):
            all_hard_passed = False
    
    if not all_hard_passed:
        safe_print(f"Phase {phase} hard gates failed - blocking execution")
        return False
    
    safe_print(f"All Phase {phase} hard gates passed")
    
    # Run soft gates (non-blocking)
    if phase in PHASE_SOFT_GATES:
        soft_gates = PHASE_SOFT_GATES[phase]
        safe_print(f"Running {len(soft_gates)} soft gates for Phase {phase} (non-blocking)...")
        
        for gate_script in soft_gates:
            run_gate(gate_script, scripts_dir, gate_type="soft", soft_gates_dir=soft_gates_dir)
        
        safe_print(f"Phase {phase} soft gates completed (warnings do not block execution)")
    
    return True

def main():
    parser = argparse.ArgumentParser(description="Run gates for a specific phase (hard gates blocking, soft gates non-blocking)")
    parser.add_argument("--phase", type=int, required=True, help="Phase number (1, 2, 3, 4, 5, or 6). Note: Phase 0 is deliberately un-gated (optional batch optimization phase).")
    parser.add_argument("--scripts-dir", type=str, default=".Planner/scripts/hard_gates", help="Directory containing hard gate scripts")
    parser.add_argument("--soft-gates-dir", type=str, default=".Planner/scripts/soft_gates", help="Directory containing soft gate scripts")
    
    args = parser.parse_args()
    scripts_dir = Path(args.scripts_dir)
    soft_gates_dir = Path(args.soft_gates_dir) if args.soft_gates_dir else None
    
    if run_phase_gates(args.phase, scripts_dir, soft_gates_dir):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()