Depends on: prompt-6
Vision principles: P5 (wire as you go), P4 (minimum viable local capability), P2 (pluggable)
Open questions resolved: Q13 deferred (learning loops remain deferred)

---

## S0 — Opening

S0.1 — Run `/open`. Verify prompt-6 tag exists on origin. Confirm working copy is clean and on `main`.

S0.2 — Read `AGENTS.md` in full.

S0.3 — Add new rules:
- **OR50**: Every adapter MUST declare a `health_check()` method. The `LifecycleManager` calls this method on adapter registration. If the health check fails, the adapter is registered with `DEGRADED` status in the capability graph — it is NOT skipped. This lets the UI show "Ollama: unavailable" rather than hiding it. Source: Plan 7.
- **OR51**: Skills placed in `skills/user/` are user-authored and trusted by default per P14. They do NOT require a provenance manifest or cryptographic signature. Skills in `skills/external/` DO require provenance manifests. The manifest parser distinguishes by directory path. Source: P14.

Commit: `docs: add OR50-OR51 for prompt-7`

---

## Plan Body

### S1 — Add runtime dependencies

Append to `txt/requirements.txt`:
```
ollama>=0.3.0
httpx>=0.27.0
psutil>=5.9.0
```

Run `.venv/Scripts/pip.exe install -e .[dev]`.
Run `.venv/Scripts/pip-audit.exe --strict --requirement txt/requirements.txt`.

### S2 — Create sovereignai/orchestrator/orchestrator.py

Create `sovereignai/orchestrator/orchestrator.py`:

**Purpose**: Minimal Orchestrator (CEO) for v1. Receives natural language text from the user (via web UI), determines which skill to invoke, submits the task, and returns the result.

**v1 simplification**: The Orchestrator does NOT use an LLM for routing in this plan. It uses keyword matching:
- Messages containing "search" or "look up" → route to `websearch` skill.
- Messages containing "chat" or "talk to" or no keyword match → route to `ollama` adapter (text_generation).
- All other messages → return "I don't know how to handle that yet."

**Constructor** (≤15 args per AR5):
```python
def __init__(
    self,
    capability_api: CapabilityAPI,
    routing_engine: RoutingEngine,
    task_state_machine: TaskStateMachine,
    trace: TraceEmitter,
) -> None:
```

**Methods**:
- `handle_message(message: str) -> str`: Parse message, route to skill/adapter, poll task state until COMPLETE or FAILED, return result or error.
- `_route_to_skill(message: str) -> ComponentId`: Keyword-based routing.
- `_wait_for_task(task_id: UUID) -> Task`: Poll task state machine with 100ms sleep, timeout 30s.

**Trace emission**: Emit INFO on message received, DEBUG on routing decision, ERROR on failure.

### S3 — Create skills/user/websearch_skill/

Create directory `skills/user/websearch_skill/` with:

1. **`manifest.toml`**:
```toml
[component]
id = "websearch_skill"
name = "Web Search"
version = "0.1.0"
author = "user"

[[capabilities]]
category = "skill"
name = "web_search"
description = "Search the web for information using DuckDuckGo"
input_schema = "{ "query": "string" }"
output_schema = "{ "results": ["string"] }"
priority = 100
```

2. **`skill.py`**:
```python
"""Search the web using DuckDuckGo's HTML interface.

This skill accepts a search query string and returns a list of
result snippets. It uses only the Python standard library to avoid
adding runtime dependencies per the minimal-deps philosophy.
"""
```

Implementation details:
- Use `urllib.request` to fetch `https://html.duckduckgo.com/html/?q={query}`.
- Parse HTML with `html.parser` from stdlib (no BeautifulSoup — avoid deps).
- Extract result titles and snippets from `.result__title` and `.result__snippet` classes.
- Return list of dicts: `[{"title": "...", "snippet": "...", "url": "..."}]`.
- Handle network errors gracefully: return empty list + error message in trace.
- No external dependencies. Stdlib only.

### S4 — Create adapters/external/ollama_adapter/

Create directory `adapters/external/ollama_adapter/` with:

1. **`manifest.toml`**:
```toml
[component]
id = "ollama_adapter"
name = "Ollama Local Models"
version = "0.1.0"
author = "user"

[[capabilities]]
category = "adapter"
name = "text_generation"
description = "Generate text using local models via Ollama"
input_schema = "{ "prompt": "string", "model": "string" }"
output_schema = "{ "text": "string" }"
priority = 100

[[capabilities]]
category = "adapter"
name = "chat_completion"
description = "Chat completion using local models via Ollama"
input_schema = "{ "messages": [{"role":"string","content":"string"}], "model": "string" }"
output_schema = "{ "message": {"role":"string","content":"string"} }"
priority = 100
```

2. **`adapter.py`**:
```python
"""Connect to Ollama local model server for text generation.

This adapter wraps the official Ollama Python client to provide
capability-based model inference. It registers with the capability
graph on startup and reports DEGRADED status if Ollama is not running.
"""
```

Implementation details:
- Constructor: accepts `trace: TraceEmitter`.
- `health_check() -> bool`: Try to list models via `ollama.list()`. Return True if successful.
- `generate(prompt: str, model: str = "llama3.2") -> str`: Call `ollama.generate()`, return text.
- `chat(messages: list[dict], model: str = "llama3.2") -> dict`: Call `ollama.chat()`, return message dict.
- On init: if health_check fails, emit WARN trace but still register.

### S5 — Create sovereignai/shared/hardware_probe.py

Create `sovereignai/shared/hardware_probe.py`:

```python
"""Detect system hardware resources for the Hardware panel.

This module probes CPU, RAM, GPU, and VRAM availability using
platform-appropriate methods. On Windows it uses WMI via subprocess
and the psutil library for CPU and RAM metrics.
"""
```

Implementation:
- `HardwareInfo` dataclass: cpu_count, cpu_freq_mhz, ram_total_mb, ram_available_mb, gpu_name, gpu_vram_mb, timestamp.
- `probe() -> HardwareInfo`: 
  - CPU/RAM via `psutil`.
  - GPU via `subprocess.run(["wmic", "path", "win32_VideoController", "get", "Name,AdapterRAM"])` on Windows.
  - If `wmic` fails or GPU not found: gpu_name="None detected", gpu_vram_mb=0.
  - If `psutil` fails: all values = 0, emit ERROR trace.
- `probe()` is called on demand (not a background thread) — the Hardware panel calls it when opened.

### S6 — Update sovereignai/main.py composition root

Register new components in `build_container()`:
```python
# 10. HardwareProbe — depends on TraceEmitter
from sovereignai.shared.hardware_probe import HardwareProbe
hardware = HardwareProbe(trace=trace)
container.register_singleton(HardwareProbe, hardware)

# 11. Orchestrator — depends on CapabilityAPI + RoutingEngine + TaskStateMachine + TraceEmitter
from sovereignai.orchestrator.orchestrator import Orchestrator
orchestrator = Orchestrator(
    capability_api=container.retrieve(CapabilityAPI),
    routing_engine=container.retrieve(RoutingEngine),
    task_state_machine=container.retrieve(TaskStateMachine),
    trace=trace,
)
container.register_singleton(Orchestrator, orchestrator)
```

Load skill and adapter manifests:
- Scan `skills/user/` and `adapters/external/` for `manifest.toml` files.
- Parse each manifest via `ManifestParser`.
- Register each component in `CapabilityGraph`.
- For adapters: call `health_check()` and set status accordingly.

### S7 — Update web/main.py with Orchestrator endpoint

Add to `web/main.py`:
```python
@app.post("/api/orchestrate")
async def orchestrate(request: Request):
    """Submit a natural language message to the Orchestrator."""
    data = await request.json()
    message = data.get("message", "")
    orchestrator = container.retrieve(Orchestrator)
    result = orchestrator.handle_message(message)
    return {"result": result}
```

### S8 — Tests

- `tests/test_orchestrator.py`: Test keyword routing (search → websearch, chat → ollama, unknown → fallback), test trace emission, test timeout handling.
- `tests/test_websearch_skill.py`: Mock `urllib.request.urlopen` with sample DuckDuckGo HTML, test parsing, test empty results, test network error graceful handling.
- `tests/test_ollama_adapter.py`: Mock `ollama.list()` (success and failure), mock `ollama.generate()`, test health_check, test DEGRADED registration.
- `tests/test_hardware_probe.py`: Mock `psutil` and `subprocess.run`, test all fields populated, test graceful degradation when probes fail.

---

## STOP Conditions

- If Orchestrator constructor exceeds 15 arguments, STOP — split into config dataclass or helper objects per AR5.
- If Ollama adapter fails to degrade gracefully when Ollama is not installed, STOP.
- If web search skill adds any non-stdlib import, STOP — it must use `urllib` only.
- If any test fails, STOP.

---

## Files WILL Create

- `sovereignai/orchestrator/orchestrator.py`
- `sovereignai/orchestrator/__init__.py`
- `skills/user/websearch_skill/manifest.toml`
- `skills/user/websearch_skill/skill.py`
- `adapters/external/ollama_adapter/manifest.toml`
- `adapters/external/ollama_adapter/adapter.py`
- `sovereignai/shared/hardware_probe.py`
- `tests/test_orchestrator.py`
- `tests/test_websearch_skill.py`
- `tests/test_ollama_adapter.py`
- `tests/test_hardware_probe.py`

## Files WILL Edit

- `txt/requirements.txt` (append 3 lines)
- `sovereignai/main.py` (extend build_container)
- `web/main.py` (add /api/orchestrate endpoint)

## Files WILL NOT Edit

- Any file in `sovereignai/shared/` except `hardware_probe.py` (new file, not editing existing core)
- `AGENTS.md` (except S0.3)

---

## Closing

Run `/close`. Tag: `prompt-7`.
