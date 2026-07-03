# SovereignAI -- Skill & Agent System Design Document v1.0

**Status**: Draft -- approved for implementation  
**Date**: 2026-07-03  
**Author**: Architect (Round Table bypass per User preference)  
**Depends on**: `principles.md`, `AGENTS.md`, `DECISIONS.md`, `AI_HANDOFF.md`

---

## 1. Architecture Overview

```
+-------------------------------------------------------------+
|                         Owner (User)                          |
+----------------------+----------------------------------------+
                       | chat / task request
+----------------------v----------------------------------------+
|                      Orchestrator                              |
|         (routes tasks to departments, no ReAct)                |
+----------------------+----------------------------------------+
                       | department task
+----------------------v----------------------------------------+
|                   Department Manager                           |
|         (plans work, assigns workers, no ReAct)                |
+----------------------+----------------------------------------+
                       | worker assignment
+----------------------v----------------------------------------+
|                      Worker (ReAct Loop)                       |
|  +---------+    +----------+    +---------+    +----------+ |
|  | THOUGHT |--->|  ACTION  |--->| EXECUTE |--->| OBSERVE  | |
|  | (LLM)   |    | (Parser) |    | (Skill) |    | (Result) | |
|  +---------+    +----------+    +---------+    +----------+ |
|       ^-----------------------------------------------------+ |
|       | (loop until done or max iterations)                    |
+----------------------+----------------------------------------+
                       | tool calls
+----------------------v----------------------------------------+
|                    SkillRunner (in-process)                    |
|  +-------------+  +-------------+  +---------------------+  |
|  | file_read   |  | file_write  |  | file_search         |  |
|  | file_search |  | web_search  |  | web_fetch           |  |
|  +-------------+  +-------------+  +---------------------+  |
+-------------------------------------------------------------+
                       |
+----------------------v----------------------------------------+
|              CapabilityGraph (manifest-driven)                 |
|         (discovers skills, routes calls, validates)            |
+-------------------------------------------------------------+
```

---

## 2. Design Decisions

| # | Decision | Rationale |
|---|----------|-----------|
| 1 | **Hybrid manifest** (manifest + code) | Core reads manifest only. Code loaded at execution time. Preserves P1 boundary. |
| 2 | **Pydantic schemas** with auto-generated summary | Type-safe validation. Compact LLM context. Single source of truth. |
| 3 | **In-process execution** default | Fastest path. Extensible via ISkillRunner interface. |
| 4 | **Hybrid tool parser** (JSON primary, XML fallback) | Native function calling for capable models. Fallback for smaller models. |
| 5 | **Session-scoped state** | Natural fit for ReAct loops. Librarian as universal memory gateway. |
| 6 | **Structured error handling** | Resilient loops. Errors are observations, not failures. |
| 7 | **ReAct as meta-skill** | Any model, any department can invoke it. No core bloat. |
| 8 | **Manifest format** locked | TOML with execution config, capabilities, dependencies, memory. |
| 9 | **Initial skills**: file_read, file_write, file_search, web_search, web_fetch | Safe, useful, no sandbox needed yet. Complex skills from MCP later. |
| 10 | **Hybrid registration** (auto-discover + explicit config) | Drop-in convenience + owner control + UI enable/disable. |
| 11 | **Structured prompts** at Worker level | THOUGHT/ACTION/OBSERVATION. Manager can inspect reasoning. |
| 12 | **Token-budget history** | Precise context control. Never exceeds window. Librarian retrieval later. |

---

## 3. Core Interfaces

### 3.1 ISkillRunner (Protocol)

```python
from typing import Protocol, Any
from uuid import UUID

class ISkillRunner(Protocol):
    def execute(self, skill_id: str, capability: str, args: dict, session: SkillSession) -> Any: ...
    def health_check(self, skill_id: str) -> bool: ...
    def shutdown(self, skill_id: str) -> None: ...
```

### 3.2 SkillSession

```python
from dataclasses import dataclass, field
from uuid import UUID
from typing import Any

@dataclass
class SkillSession:
    task_id: UUID
    _state: dict[str, Any] = field(default_factory=dict)
    _history: list[Turn] = field(default_factory=list)
    _token_budget: int = 6000

    def get(self, key: str) -> Any: ...
    def set(self, key: str, value: Any) -> None: ...
    def add_turn(self, thought: str, action: ToolCall, observation: Observation) -> None: ...
    def format_history(self, max_tokens: int | None = None) -> str: ...
    def token_count(self) -> int: ...
```

### 3.3 ToolCall / Observation

```python
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class ToolCall:
    skill_id: str
    capability: str
    arguments: dict[str, Any]
    call_id: str

@dataclass(frozen=True)
class Observation:
    call_id: str
    success: bool
    result: Any
    error: ToolErrorObservation | None = None

@dataclass(frozen=True)
class ToolErrorObservation:
    error_type: str
    message: str
    suggestion: str | None = None
```

---

## 4. Manifest Format

```toml
[skill]
id = "file_edit"
name = "File Editor"
version = "1.0.0"
author = "sovereignai"
description = "Read, write, and edit files with diff-based operations"

[execution]
default_runner = "in_process"
sandbox = "none"
timeout_seconds = 30
max_memory_mb = 512

[[capabilities]]
name = "file_read"
description = "Read file contents"
input_model = "sovereignai.skills.file_edit:ReadInput"
output_model = "sovereignai.skills.file_edit:ReadOutput"
input_summary = '{path: string, offset?: int, limit?: int?}'
output_summary = '{content: string, size: int}'
error_handling = "structured"
max_retries = 0

[[capabilities]]
name = "file_write"
description = "Write file contents"
input_model = "sovereignai.skills.file_edit:WriteInput"
output_model = "sovereignai.skills.file_edit:WriteOutput"
input_summary = '{path: string, content: string}'
output_summary = '{bytes_written: int}'
error_handling = "structured"

[[dependencies]]
skill_id = "file_read"
capability = "file_read"

[memory]
working_memory_keys = ["file_cache"]
episodic_triggers = ["file_modified"]
```

---

## 5. ReAct Loop Skill

```python
# skills/official/react_loop/skill.py
class ReActLoopSkill:
    """Meta-skill: any model, any department can invoke this to run a ReAct loop."""

    @capability("execute_task")
    def execute(self, task: Task, session: SkillSession) -> TaskResult:
        for step in range(self.MAX_ITERATIONS):
            # 1. REASON
            thought = self.llm.generate(prompt=session.build_prompt(task))

            # 2. ACT
            action = self.tool_parser.parse(thought)

            # 3. EXECUTE
            observation = self.skill_runner.execute(
                skill_id=action.skill_id,
                capability=action.capability,
                args=action.arguments,
                session=session
            )

            # 4. OBSERVE
            session.add_turn(thought, action, observation)
            self.trace.emit(component="react_loop", level=TraceLevel.DEBUG, ...)

            # 5. CHECK
            if self._is_complete(observation):
                return TaskResult(success=True, output=observation)

        return TaskResult(success=False, output="Max iterations reached")
```

---

## 6. Prompt Structure (Worker Level)

```
SYSTEM: You are a coding assistant. Complete tasks using tools.

For each step:
1. THINK: Analyze the current state and plan next action
2. ACT: Call a tool using JSON format
3. OBSERVE: Wait for result

Available tools:
{tool_descriptions}

Response format:
THOUGHT: <your reasoning>
ACTION: {"tool_calls": [{"name": "...", "arguments": {...}}]}

---

Task: {task.description}

History:
{session.format_history(max_tokens=6000)}
```

---

## 7. Extension Points

| Extension | Trigger | Interface |
|-----------|---------|-----------|
| Subprocess sandbox | Shell skill added | ISkillRunner implementation |
| Persistent worker | MCP server integration | ISkillRunner implementation |
| Librarian retrieval | History compression needed | SkillSession + Librarian.query() |
| Degradation ladder | Network-dependent skills | Capability.error_handling config |
| Template prompts | Department-specific tuning | PromptTemplate registry |
| Graph memory | Neural map implementation | memory/graph_backend.py |
| Codebase index | Repo indexing needed | skills/official/repo_index/ |

---

## 8. Implementation Plan Queue

| Plan | Scope | Depends On |
|------|-------|------------|
| **21.1** | Skill framework core (manifest parser, SkillRunner, registration) | None |
| **21.2** | Initial skills (file_read, file_write, file_search) | 21.1 |
| **21.3** | ReAct meta-skill (loop, parser, session) | 21.1, 21.2 |
| **21.4** | Web skills (web_search upgrade, web_fetch) | 21.1 |
| **21.5** | UI integration (skill panel, enable/disable) | 21.1 |
| **21.6** | MCP server integration | 21.1, 21.5 |
| **21.7** | Shell execution + sandbox | 21.6 |
| **21.8** | Git operations skill | 21.7 |
| **21.9** | Diff-based editing | 21.8 |

---

## 9. Open Questions (for future Round Table or User decision)

1. **MCP server discovery**: Auto-discover MCP servers on local network, or explicit config only?
2. **Skill marketplace**: Pull skills from GitHub/registry, or local-only?
3. **Multi-model ReAct**: Different models for THINK vs ACT phases (Architect/Editor pattern)?
4. **Tool call verification**: Should the Security Guard audit every tool call before execution?
5. **Session persistence**: Should sessions survive process restart (serialize to SQLite)?

---

*End of document.*
