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
- **OR53**: The `MessageDispatcher` (v1) queries the `CapabilityGraph` for registered skills and routes to the first matching capability by priority order. It does NOT perform intent parsing, disambiguation, or structured prompt construction — those are CEO-shaped work deferred to a future plan. Source: Plan 7 Rev 2.

Commit: `docs: add OR50-OR51, OR53 for prompt-7`

---

## Plan Body

### S1 — Add runtime dependencies

Append to `txt/requirements.txt`:
```
ollama>=0.3.0
```

Run `.venv/Scripts/pip.exe install -e .[dev]`.
Run `.venv/Scripts/pip-audit.exe --strict --requirement txt/requirements.txt`.

Note: `httpx` is pulled transitively by `ollama` but is NOT added directly. The web search skill uses stdlib `urllib` only.

### S2 — Create sovereignai/orchestrator/dispatcher.py

Create `sovereignai/orchestrator/dispatcher.py`:

**Purpose**: MessageDispatcher for v1. Receives natural language text from the user (via web UI), queries the CapabilityGraph for matching skills, submits the task, and returns a Task object. The caller polls the TaskStateMachine for completion.

**v1 simplification**: The dispatcher does NOT use an LLM for routing. It queries the CapabilityGraph for all registered skills, filters by capability name matching a simple regex on the message, and routes to the highest-priority match. If no match, it routes to the Ollama adapter (text_generation) as a catch-all.

**Constructor** (≤15 args per AR5):
```python
def __init__(
    self,
    capability_api: CapabilityAPI,
    capability_graph: CapabilityGraph,
    task_state_machine: TaskStateMachine,
    trace: TraceEmitter,
) -> None:
```

**Methods**:
- `async def dispatch(message: str) -> Task`: Parse message, query CapabilityGraph for matching skills, submit task via CapabilityAPI, return Task object immediately. The caller polls TaskStateMachine for state updates.
- `_find_matching_skill(message: str) -> ComponentId`: Query CapabilityGraph for skills, filter by simple regex match on capability name, return highest-priority match. If no match, return Ollama adapter ID.

**Trace emission**: Emit INFO on message received, DEBUG on routing decision, ERROR on failure.

**No blocking**: `dispatch()` is async and returns immediately after task submission. No sleep/poll loop.

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

Known risk: DuckDuckGo HTML interface may return 403, CAPTCHAs,
or change DOM structure without notice. This is a v1 limitation
documented in DEBT.md.
"""
```

Implementation details:
- Use `urllib.request` to fetch `https://html.duckduckgo.com/html/?q={query}`.
- Set `User-Agent: SovereignAI/0.1.0` header to identify requests.
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

### S5 — Create web/hardware_probe.py

Create `web/hardware_probe.py` (NOT in `sovereignai/shared/` — this is a UI panel concern, not core infrastructure):

```python
"""Detect system hardware resources for the Hardware panel.

This module probes CPU, RAM, GPU, and VRAM availability using
platform-appropriate methods. It runs in the web layer, not the core.
"""
```

Implementation:
- `HardwareInfo` dataclass: cpu_count, cpu_freq_mhz, ram_total_mb, ram_available_mb, gpu_name, gpu_vram_mb, timestamp.
- `probe() -> HardwareInfo`:
  - CPU count: `os.cpu_count()` (stdlib).
  - CPU frequency: `os.cpu_freq()` if available (Python 3.13+), else None.
  - RAM: `ctypes.windll.kernel32.GlobalMemoryStatusEx` on Windows; `os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')` on POSIX.
  - GPU/VRAM: `subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"])` with fallback to "No NVIDIA GPU detected".
  - All blocking calls wrapped in `asyncio.to_thread()` when called from async context.
- If any probe fails: set field to None (not 0), emit ERROR trace. UI renders "—" for None values.

### S6 — Update sovereignai/main.py composition root

Register new components in `build_container()`:
```python
# 10. MessageDispatcher — depends on CapabilityAPI + CapabilityGraph + TaskStateMachine + TraceEmitter
from sovereignai.orchestrator.dispatcher import MessageDispatcher
dispatcher = MessageDispatcher(
    capability_api=container.retrieve(CapabilityAPI),
    capability_graph=container.retrieve(CapabilityGraph),
    task_state_machine=container.retrieve(TaskStateMachine),
    trace=trace,
)
container.register_singleton(MessageDispatcher, dispatcher)
```

Load skill and adapter manifests:
- Scan `skills/user/` and `adapters/external/` for `manifest.toml` files.
- Parse each manifest via `ManifestParser`.
- Register each component in `CapabilityGraph`.
- For adapters: call `health_check()` and set status accordingly.

### S7 — Update web/main.py with MessageDispatcher endpoint

Add to `web/main.py`:
```python
@app.post("/api/dispatch")
async def dispatch(request: Request):
    """Submit a natural language message to the MessageDispatcher."""
    data = await request.json()
    message = data.get("message", "")
    dispatcher = container.retrieve(MessageDispatcher)
    task = await dispatcher.dispatch(message)
    return TaskResponseDTO(
        task_id=str(task.id),
        state=task.state.value,
        result=task.result,
        error=task.error,
    )
```

Add hardware endpoint:
```python
@app.get("/api/hardware")
async def get_hardware():
    """Return current hardware probe results."""
    from web.hardware_probe import HardwareProbe
    probe = HardwareProbe()
    info = await probe.probe_async()  # asyncio.to_thread wrapper
    return {
        "cpu_count": info.cpu_count,
        "cpu_freq_mhz": info.cpu_freq_mhz,
        "ram_total_mb": info.ram_total_mb,
        "ram_available_mb": info.ram_available_mb,
        "gpu_name": info.gpu_name,
        "gpu_vram_mb": info.gpu_vram_mb,
    }
```

### S8 — Tests

- `tests/test_dispatcher.py`: Test dispatch to websearch skill, dispatch to ollama adapter, dispatch with no match (fallback to ollama), test trace emission, test async return (no blocking).
- `tests/test_websearch_skill.py`: Mock `urllib.request.urlopen` with sample DuckDuckGo HTML, test parsing, test empty results, test network error graceful handling, test User-Agent header present.
- `tests/test_ollama_adapter.py`: Mock `ollama.list()` (success and failure), mock `ollama.generate()`, test health_check, test DEGRADED registration.
- `tests/test_hardware_probe.py`: Mock `os.cpu_count()`, `ctypes`, `subprocess.run`, test all fields populated, test graceful degradation when probes fail, test None (not 0) on failure.

---

## STOP Conditions

- If MessageDispatcher constructor exceeds 15 arguments, STOP — split or use config dataclass.
- If Ollama adapter fails to degrade gracefully when Ollama is not installed, STOP.
- If web search skill adds any non-stdlib import, STOP — it must use `urllib` only.
- If hardware probe is placed in `sovereignai/shared/`, STOP — it belongs in `web/`.
- If any test fails, STOP.

---

## Files WILL Create

- `sovereignai/orchestrator/dispatcher.py`
- `sovereignai/orchestrator/__init__.py`
- `skills/user/websearch_skill/manifest.toml`
- `skills/user/websearch_skill/skill.py`
- `adapters/external/ollama_adapter/manifest.toml`
- `adapters/external/ollama_adapter/adapter.py`
- `web/hardware_probe.py`
- `tests/test_dispatcher.py`
- `tests/test_websearch_skill.py`
- `tests/test_ollama_adapter.py`
- `tests/test_hardware_probe.py`

## Files WILL Edit

- `txt/requirements.txt` (append 1 line: `ollama>=0.3.0`)
- `sovereignai/main.py` (extend build_container)
- `web/main.py` (add /api/dispatch and /api/hardware endpoints)

## Files WILL NOT Edit

- Any file in `sovereignai/shared/` (core is sacred per P1)
- `AGENTS.md` (except S0.3)

---

## Closing

Run `/close`. Tag: `prompt-7`.
