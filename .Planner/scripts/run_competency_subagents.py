#!/usr/bin/env python3
"""
Competency Subagent Runner

Runs 5 specialized competency subagents in parallel for plan validation.
Invoked by Planner during Phase 5.5 for internal pre-Round Table validation.
Uses Devin CLI subagent system with custom AGENT.md profiles.
"""

import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

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
    print("Competency Subagent Runner")
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
    print("Phase 5.5: Competency Self-Check")
    print("=" * 60)
    print("[INFO] This script provides configuration for manual subagent invocation")
    print("[INFO] The Planner should use run_subagent tool to invoke each subagent")
    print("[INFO] Subagent profiles are located in .devin/agents/{name}/AGENT.md")
    print("\n[INFO] Example invocation for Planner:")
    print("  run_subagent(profile='technical-architecture', task='Evaluate {plan_file} against COMP-001 criteria')")
    print("  run_subagent(profile='domain-relevance', task='Evaluate {plan_file} against COMP-002 criteria')")
    print("  run_subagent(profile='communication-quality', task='Evaluate {plan_file} against COMP-003 criteria')")
    print("  run_subagent(profile='cross-team-impact', task='Evaluate {plan_file} against COMP-004 criteria')")
    print("  run_subagent(profile='governance-compliance', task='Evaluate {plan_file} against COMP-005 criteria')")
    
    print("\n[INFO] All subagents use SWE-1.6 model (desktop IDE built-in)")
    print("[INFO] Each subagent has specialized prompts for their competency domain")
    print("[INFO] Planner should collect JSON evaluations and fix CRITICAL/HIGH findings")
    
    sys.exit(0)

if __name__ == "__main__":
    main()