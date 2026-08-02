# SovereignAI -- LLM Function Calling Design Document v1.0

**Status**: Draft -- approved for implementation  
**Date**: 2026-07-03  
**Author**: Architect  
**Depends on**: `../PRINCIPLES.md`, `../AGENTS.md`, `../DECISIONS.md`, `../AI_HANDOFF.md`, `SovereignAI_Skill_Agent_System_Design_v1.0.md`

---

## 1. Context

**Gap**: #4 -- LLM Function Calling  
**Problem**: The ReAct meta-skill needs the LLM to emit parseable tool calls. The design doc (v1.0) specified "hybrid tool parser (JSON primary, XML fallback)" but research revealed Qwen2.5-Coder needs `<tools>` tags, not JSON.  
**Scope**: How the ReAct loop gets parseable tool calls from local models without violating P3 (no provider lock-in).

---

## 2. Design Decision

**DD-21.3.1**: Tool call generation (Proposed, P2/P3/P5-aligned): Single-call structured output. LLM emits THOUGHT (free text) + ACTION (JSON) in one response. ToolCallParser extracts JSON, validates tool exists in capability graph, validates arguments via tool's input_model (Pydantic). On validation failure: retry with error feedback (max 3 attempts). After max retries: return typed ToolCallError, which becomes an observation in the ReAct loop per Section 5's "errors are observations, not failures" pattern.

---

## 3. Mechanism

### 3.1 Single-Call Flow

```python
# Step 1: LLM generates THOUGHT + ACTION in single response
response = llm.generate(prompt=session.build_prompt(task))

# Step 2: Parser extracts JSON
json_str = parser._extract_action_json(response)
raw = json.loads(json_str)
tool_name = raw["tool_calls"][0]["name"]
arguments = raw["tool_calls"][0]["arguments"]

# Step 3: Validate against capability graph
tool_schema = capability_graph.get_tool_schema(tool_name)
validated = tool_schema.input_model.model_validate(arguments)

# Step 4: Return typed ToolCall
return ToolCall(
    skill_id=tool_schema.skill_id,
    capability=tool_name,
    arguments=validated,
    call_id=str(uuid4()),
)
```

### 3.2 Retry Flow

```python
for attempt in range(MAX_RETRIES):
    try:
        return self._parse_single(response, available_tools)
    except (json.JSONDecodeError, KeyError, ValidationError, ToolNotFoundError) as exc:
        if attempt < MAX_RETRIES - 1:
            response = self._llm.generate(
                self._build_retry_prompt(response, exc, available_tools)
            )
        else:
            return ToolCallError(
                error_type=type(exc).__name__,
                message=str(exc)[:200],
                raw_response=response[:500],
                attempt_count=attempt + 1,
            )
```

### 3.3 Retry Prompt

```
Your previous response failed validation: {error}.
Please output valid JSON matching this schema: {schema}.

Available tools:
{tool_descriptions}

Response format:
THOUGHT: <your reasoning>
ACTION: {"tool_calls": [{"name": "...", "arguments": {...}}]}
```

---

## 4. Adapter Interface

**Unchanged**: `generate(prompt) -> str`

No `generate_with_tools()`, no `generate_structured()`. Any adapter that can generate text works -- P3 compliant.

```python
class LLMAdapter(Protocol):
    def generate(self, prompt: str, **kwargs) -> str:
        ...
```

---

## 5. Data Structures

```python
@dataclass(frozen=True)
class ToolCall:
    skill_id: str
    capability: str
    arguments: BaseModel  # validated against tool's input_model
    call_id: str

@dataclass(frozen=True)
class ToolCallError:
    error_type: str
    message: str
    raw_response: str  # for debugging
    attempt_count: int
```

---

## 6. Validation Chain

1. **JSON extraction**: Extract from `<tool_call>` tags or code blocks. Catch `JSONDecodeError`.
2. **Tool existence**: Check tool name in capability graph. Catch `ToolNotFoundError`.
3. **Schema validation**: `tool_schema.input_model.model_validate(arguments)`. Catch `ValidationError`.
4. **Return**: `ToolCall` on success, `ToolCallError` on max retries.

---

## 7. Rejected Alternatives

### 7.1 A -- Native Function Calling (Ollama tools parameter)
- **Why rejected**: P3 violation. Ollama-specific `tools` parameter. Delete Ollama adapter, keep only llama.cpp -> ReAct breaks.
- **Consequence**: System requires Ollama adapter to function.

### 7.2 B -- Two-Step Structured Output
- **Why rejected**: P3-soft violation. Bakes model-capability assumption into architecture. Two calls = permanent latency tax even when single-call suffices. Departs from existing design doc Section 5/6.
- **Consequence**: Architecture assumes models can't handle single-call structured output. Wasted latency forever.

### 7.3 C -- Hybrid (Native + Fallback)
- **Why rejected**: P5 violation. Two code paths, speculative fallback infrastructure.
- **Consequence**: Runtime complexity. Two parsers, two prompt templates, two error handling paths.

### 7.4 D -- Prompt-Only (No Validation)
- **Why rejected**: AR6-adjacent. No type safety at LLM boundary. Brittle custom parser.
- **Consequence**: Silent failures when model emits malformed tool calls.

---

## 8. Rationale

| Principle | How E Honors It |
|-----------|----------------|
| P3 (no provider lock-in) | `generate(prompt) -> str` is universal. Any adapter works. |
| P5 (no speculative contracts) | One strategy with retry. No fallback infrastructure. |
| P13 (strong and robust) | Retry handles failure. Typed error after max retries. |
| P9 (observability) | Every validation failure emits trace. Attempt count logged. |

---

## 9. Extension Points

| Extension | Trigger | Interface |
|-----------|---------|-----------|
| Parallel tool calls | Model supports multiple tools per response | `tool_calls: list[ToolCall]` instead of single |
| Streaming tool calls | Token-by-token generation | Parse partial JSON as it arrives |
| Tool call verification | Security Guard audit | `security_guard.audit(tool_call)` before execution |

---

## 10. Open Questions

| ID | Question | Status |
|----|----------|--------|
| Q-21.3.1 | Should tool call parser support parallel tool calls? | Deferred |
| Q-21.3.2 | Should streaming generation parse partial JSON? | Deferred |
| Q-21.3.3 | Should Security Guard audit every tool call? | Deferred |

---

## 11. Implementation Plan

**Plan 21.3** (ReAct Meta-Skill) incorporates this design:
- S1: ToolCallParser class with validation chain
- S2: Retry logic with error feedback
- S3: Integration with ReAct loop
- S4: Tests for validation, retry, error cases

---

*End of document.*
