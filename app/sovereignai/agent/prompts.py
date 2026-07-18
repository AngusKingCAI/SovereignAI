from __future__ import annotations

from typing import Any


def build_react_prompt(
    task_description: str,
    tools: list[dict[str, Any]],
    context: str | None = None,
    memory_context: str | None = None,
) -> str:
    """Build ReAct loop prompt with system prompt, tools, and optional context sections."""
    system_prompt = """You are a reasoning agent that uses a THOUGHT-ACTION-OBSERVATION loop.

For each step:
1. THOUGHT: Reason about what to do next
2. ACTION: Choose a tool to execute (or provide FinalAnswer)
3. OBSERVATION: Review the tool result

Tool definitions:
"""

    # Add tool definitions as compact schema summaries
    for tool in tools:
        tool_name = tool.get("name", "unknown")
        tool_desc = tool.get("description", "No description")
        tool_params = tool.get("parameters", {})
        system_prompt += f"\n{tool_name}: {tool_desc}\n"
        if tool_params:
            system_prompt += f"  Parameters: {tool_params}\n"

    # Add optional context sections
    if context:
        system_prompt += f"\n[Symbol Context]\n{context}\n"

    if memory_context:
        system_prompt += f"\n[Graph Context]\n{memory_context}\n"

    # Add task description
    system_prompt += f"\nTask: {task_description}\n"

    return system_prompt
