"""Agent detection from prompt content."""

from __future__ import annotations

import re


# Agent prefix patterns - these are the response format prefixes used by each agent
AGENT_PATTERNS = {
    r"\[🏗️ ARCHITECT AGENT\]": "Architect",
    r"\[🔍 REVIEWER AGENT\]": "Reviewer", 
    r"\[📋 PLANNER AGENT\]": "Planner",
    r"\[⚡ EXECUTOR AGENT\]": "Executor",
    r"\[🔬 RESEARCHER AGENT\]": "Researcher",
}


def detect_agent_from_prompt(prompt: str) -> str:
    """Detect agent from prompt content using agent prefix patterns.
    
    Args:
        prompt: The user prompt or message content
        
    Returns:
        Detected agent name, or "Architect" as default if no pattern matches
    """
    # First check for agent prefix patterns
    for pattern, agent in AGENT_PATTERNS.items():
        if re.search(pattern, prompt):
            return agent
    
    # Check for agent mentions without prefix (more flexible detection)
    if re.search(r"reviewer\s*agent", prompt, re.IGNORECASE):
        return "Reviewer"
    elif re.search(r"planner\s*agent", prompt, re.IGNORECASE):
        return "Planner"
    elif re.search(r"executor\s*agent", prompt, re.IGNORECASE):
        return "Executor"
    elif re.search(r"researcher\s*agent", prompt, re.IGNORECASE):
        return "Researcher"
    elif re.search(r"architect\s*agent", prompt, re.IGNORECASE):
        return "Architect"
    
    # Check for simple agent name mentions
    if re.search(r"\breviewer\b", prompt, re.IGNORECASE):
        return "Reviewer"
    elif re.search(r"\bplanner\b", prompt, re.IGNORECASE):
        return "Planner"
    elif re.search(r"\bexecutor\b", prompt, re.IGNORECASE):
        return "Executor"
    elif re.search(r"\bresearcher\b", prompt, re.IGNORECASE):
        return "Researcher"
    elif re.search(r"\barchitect\b", prompt, re.IGNORECASE):
        return "Architect"
    
    # Default to Architect if no agent pattern detected
    return "Architect"
