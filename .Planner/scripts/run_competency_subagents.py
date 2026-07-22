#!/usr/bin/env python3
"""
Competency Subagent Runner

Provides configuration and validation for the Phase 5.5 competency self-check.
This is a MANUAL step - the Planner must invoke each subagent using the run_subagent tool.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Subagent configuration for Devin CLI
SUBAGENTS = {
    "technical-architecture": {
        "directory": "technical-architecture",
        "competency": "COMP-001",
        "criteria": ["CRIT-001", "CRIT-002", "CRIT-003"]
    },
    "domain-relevance": {
        "directory": "domain-relevance",
        "competency": "COMP-002", 
        "criteria": ["CRIT-004", "CRIT-005", "CRIT-006"]
    },
    "communication-quality": {
        "directory": "communication-quality",
        "competency": "COMP-003",
        "criteria": ["CRIT-007", "CRIT-008"]
    },
    "cross-team-impact": {
        "directory": "cross-team-impact",
        "competency": "COMP-004",
        "criteria": ["CRIT-009", "CRIT-010"]
    },
    "governance-compliance": {
        "directory": "governance-compliance",
        "competency": "COMP-005",
        "criteria": ["CRIT-011", "CRIT-012", "CRIT-013"]
    }
}

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_competency_subagents.py <plan_file_path>")
        sys.exit(1)
    
    plan_file = sys.argv[1]
    plan_path = Path(plan_file)
    
    if not plan_path.exists():
        print(f"Error: Plan file not found: {plan_file}")
        sys.exit(1)
    
    print("=" * 60)
    print("Phase 5.5: Competency Self-Check (MANUAL STEP)")
    print("=" * 60)
    print(f"Plan: {plan_file}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Subagents: {len(SUBAGENTS)}")
    print("=" * 60)
    
    print("\nSubagent Configuration:")
    for name, config in SUBAGENTS.items():
        print(f"  {name}:")
        print(f"    Directory: .devin/agents/{config['directory']}")
        print(f"    Competency: {config['competency']}")
        print(f"    Criteria: {', '.join(config['criteria'])}")
    
    print("\n" + "=" * 60)
    print("MANUAL INSTRUCTIONS FOR PLANNER")
    print("=" * 60)
    print("This is a MANUAL step - you must invoke each subagent individually.")
    print("Use the run_subagent tool for each competency:")
    print("\n1. Technical Architecture:")
    print(f"   run_subagent(profile='technical-architecture', task='Evaluate {plan_file} against COMP-001 criteria and return JSON evaluation')")
    print("\n2. Domain Relevance:")
    print(f"   run_subagent(profile='domain-relevance', task='Evaluate {plan_file} against COMP-002 criteria and return JSON evaluation')")
    print("\n3. Communication Quality:")
    print(f"   run_subagent(profile='communication-quality', task='Evaluate {plan_file} against COMP-003 criteria and return JSON evaluation')")
    print("\n4. Cross-Team Impact:")
    print(f"   run_subagent(profile='cross-team-impact', task='Evaluate {plan_file} against COMP-004 criteria and return JSON evaluation')")
    print("\n5. Governance Compliance:")
    print(f"   run_subagent(profile='governance-compliance', task='Evaluate {plan_file} against COMP-005 criteria and return JSON evaluation')")
    
    print("\n" + "=" * 60)
    print("COMPLIANCE REQUIREMENTS")
    print("=" * 60)
    print("After running all 5 subagents:")
    print("1. Collect all JSON evaluations")
    print("2. Fix all CRITICAL/HIGH findings")
    print("3. Defer MEDIUM/LOW strategic issues to Round Table")
    print("4. Post compliance: ✅ Gate PLAN-5.5 PASS: Competency self-check complete, {N} findings fixed, {N} findings deferred to Round Table")
    
    print("\n[WARNING] Phase 5.5 requires manual subagent invocation.")
    print("[INFO] All subagents use SWE-1.6 model (desktop IDE built-in)")
    print("[INFO] Each subagent has specialized prompts for their competency domain")
    
    sys.exit(0)

if __name__ == "__main__":
    main()