"""
Tool Name Normalization for Governor.py v1.5

This module provides tool name normalization to map Devin CLI tool names
to canonical names used in Governor's rule system. This allows rules to
reference tools consistently regardless of how Devin CLI names them.

Key Functions:
- normalize_tool_name(): Map Devin tool names to canonical names
- get_canonical_tool_map(): Get the current tool mapping
- add_alias(): Add custom tool name aliases
- detect_phase_from_tool(): Infer phase from tool usage (test/git detection)

This implements the tool normalization specified in v1.5 spec §2.3.
"""

from typing import Dict, Optional, Set
import os

# YAML import with stdlib fallback
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

# Canonical tool mapping from Devin CLI names to Governor canonical names
CANONICAL_TOOL_MAP = {
    "Read": "read",
    "Write": "file_write",
    "Edit": "file_edit",
    "Bash": "exec",
    "WebSearch": "web_search",
    "PermissionRequest": "permission_request",
    "Stop": "stop",
}

# Custom aliases (can be configured)
CUSTOM_ALIASES: Dict[str, str] = {}

# Phase patterns for tool-based phase inference
# Maps canonical tool names to phases where they are commonly used
PHASE_PATTERNS = {
    "read": ["INIT", "RESEARCH", "PLAN", "EXECUTE", "VALIDATE", "COMMIT"],
    "web_search": ["INIT", "RESEARCH", "PLAN"],
    "file_write": ["EXECUTE", "COMMIT"],
    "file_edit": ["EXECUTE", "COMMIT"],
    "exec": ["EXECUTE", "VALIDATE"],
}


def normalize_tool_name(tool_name: str) -> str:
    """
    Normalize a Devin CLI tool name to canonical name.
    
    This function maps the exact tool names that Devin CLI uses to the
    canonical names that Governor uses internally. This allows rules to be
    written with consistent tool references.
    
    Args:
        tool_name: Tool name from Devin CLI (e.g., "Read", "Write", "Bash")
        
    Returns:
        Canonical tool name (e.g., "read", "file_write", "exec")
        
    Example:
        >>> normalize_tool_name("Read")
        'read'
        >>> normalize_tool_name("Bash")
        'exec'
        >>> normalize_tool_name("Unknown")
        'unknown'
    """
    # Check canonical map first
    if tool_name in CANONICAL_TOOL_MAP:
        return CANONICAL_TOOL_MAP[tool_name]
    
    # Check custom aliases
    if tool_name in CUSTOM_ALIASES:
        return CUSTOM_ALIASES[tool_name]
    
    # Return tool name as-is if not found (allows for future tool names)
    return tool_name.lower()


def get_canonical_tool_map() -> Dict[str, str]:
    """
    Get the current canonical tool mapping including custom aliases.
    
    Returns:
        Dictionary mapping all known tool names to canonical names
    """
    combined_map = CANONICAL_TOOL_MAP.copy()
    combined_map.update(CUSTOM_ALIASES)
    return combined_map


def add_alias(alias: str, canonical_name: str) -> None:
    """
    Add a custom tool name alias.
    
    Args:
        alias: Alias name
        canonical_name: Canonical tool name to map to
        
    Raises:
        ValueError: If canonical_name is not in canonical map
    """
    if canonical_name not in CANONICAL_TOOL_MAP.values():
        raise ValueError(f"Unknown canonical tool name: {canonical_name}")
    
    CUSTOM_ALIASES[alias] = canonical_name


def load_phase_patterns(config_file: Optional[str] = None) -> Dict[str, list]:
    """
    Load phase patterns from configuration file.
    
    Args:
        config_file: Path to phase_patterns.yaml file
        
    Returns:
        Dictionary mapping canonical tool names to phase lists
    """
    if config_file and os.path.exists(config_file) and HAS_YAML:
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
                return config.get("phase_patterns", PHASE_PATTERNS)
        except (yaml.YAMLError, IOError):
            pass
    
    return PHASE_PATTERNS


def detect_phase_from_tool(tool_name: str, config_file: Optional[str] = None) -> Optional[str]:
    """
    Infer the current phase based on tool usage.
    
    This function uses phase patterns to infer which phase the agent is likely
    in based on the tools being used. For example, if the agent is using
    web_search, it's likely in the RESEARCH phase.
    
    Args:
        tool_name: Tool name being used
        config_file: Optional path to phase_patterns.yaml
        
    Returns:
        Most likely phase, or None if cannot determine
        
    Example:
        >>> detect_phase_from_tool("web_search")
        'RESEARCH'
        >>> detect_phase_from_tool("file_write")
        'EXECUTE'
    """
    canonical_name = normalize_tool_name(tool_name)
    patterns = load_phase_patterns(config_file)
    
    if canonical_name in patterns:
        phases = patterns[canonical_name]
        # Return the most specific phase (prefer later phases)
        if "EXECUTE" in phases:
            return "EXECUTE"
        if "VALIDATE" in phases:
            return "VALIDATE"
        if "COMMIT" in phases:
            return "COMMIT"
        if "PLAN" in phases:
            return "PLAN"
        if "RESEARCH" in phases:
            return "RESEARCH"
        if "INIT" in phases:
            return "INIT"
    
    return None


def get_tools_for_phase(phase: str, config_file: Optional[str] = None) -> Set[str]:
    """
    Get all tools that are allowed in a specific phase.
    
    Args:
        phase: Phase name
        config_file: Optional path to phase_patterns.yaml
        
    Returns:
        Set of canonical tool names allowed in the phase
    """
    patterns = load_phase_patterns(config_file)
    tools_for_phase = set()
    
    for tool, phases in patterns.items():
        if phase in phases:
            tools_for_phase.add(tool)
    
    return tools_for_phase


def is_tool_allowed_in_phase(tool_name: str, phase: str, config_file: Optional[str] = None) -> bool:
    """
    Check if a tool is allowed in a specific phase.
    
    Args:
        tool_name: Tool name to check
        phase: Phase to check against
        config_file: Optional path to phase_patterns.yaml
        
    Returns:
        True if tool is allowed in the phase, False otherwise
    """
    canonical_name = normalize_tool_name(tool_name)
    tools_for_phase = get_tools_for_phase(phase, config_file)
    return canonical_name in tools_for_phase
