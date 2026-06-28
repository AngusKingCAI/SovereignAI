Depends on: prompt-6
Vision principles: P5 (wire as you go), P4 (minimum viable local capability), P2 (pluggable)
Open questions resolved: Q13 deferred (learning loops remain deferred)

---

## Adjudication Log (Rev3 → Rev4)

### Finding 4 — Stale contradictions: urllib/httpx, os.cpu_freq (Qwen #1, #2 — CRITICAL)
**Action**: ACCEPTED. S1 and STOP conditions updated: "httpx" not "urllib". S5 stale `os.cpu_freq()` paragraph removed.

### Finding 3 — Dispatcher has no session token (Kimi C3 — CRITICAL)
**Action**: ACCEPTED. `dispatch()` now accepts `token: str` parameter. `_find_matching_skill()` returns `Optional[ComponentId]` — if None, route to Ollama `chat` skill (restored catch-all, but as explicit named skill).

### Finding 12 — Keyword substring matching too permissive (MiniMax Issue 3 — HIGH)
**Action**: ACCEPTED. Replace substring with word-boundary matching against `intent_keywords` from manifest. Manifests now declare `intent_keywords = ["search", "find", "look up"]`. Matching uses `re.search(rf'\b{keyword}\b', message, re.IGNORECASE)`.

### Finding 13 — Restoring Ollama catch-all as explicit chat skill (multiple panelists — HIGH)
**Action**: ACCEPTED. Ollama adapter registered as a skill with `intent_keywords = ["chat", "talk", "ask", "explain", "help", "what", "how", "why"]`. If no skill matches, route to Ollama chat skill — NOT silent "I don't know". This preserves "always responds" UX.

### Finding 16 — WMIC syntax error (Kimi H5 — MEDIUM)
**Action**: ACCEPTED. `/format:csv` not `--format:csv`.

### Verdict: All CRITICAL/HIGH issues fixed.

---

## Adjudication Log (Rev2 → Rev3)

Per GR4. 6 panelist responses received. The following Rev2 issues were accepted and fixed.

### Finding 4 — MessageDispatcher regex routing too brittle (all 6 panelists — convergent)
**Severity**: CRITICAL
**Action**: ACCEPTED. Regex matching replaced with simple keyword matching: check if any word in the message matches a capability name (case-insensitive substring). Document explicitly that this is a v1 placeholder. Add tests for messages that DON'T contain the exact capability name. Per Finding 18 (MiniMax C1): catch-all to Ollama replaced with explicit "I don't know how to handle that yet." response when no skill matches.

### Finding 8 — `nvidia-smi` only detects NVIDIA (all 6 panelists — convergent)
**Severity**: HIGH
**Action**: ACCEPTED. Hardware probe now uses WMI fallback on Windows (`wmic path win32_VideoController get Name,AdapterRAM`). On macOS: `system_profiler SPDisplaysDataType`. On Linux: `lspci | grep VGA`. Reports "GPU: {name} ({vram}MB)" for any GPU found, "No GPU detected" only if truly none.

### Finding 9 — Web search skill uses `urllib` — fails behind proxies (DeepSeek H3)
**Severity**: HIGH
**Action**: ACCEPTED. Changed from `urllib` to `httpx` (already a transitive dep via `ollama`). `httpx` respects proxy env vars automatically.

### Finding 10 — Web search skill no rate limiting (DeepSeek H7)
**Severity**: HIGH
**Action**: ACCEPTED. Added simple time-based rate limiter (max 1 request per 2 seconds). DuckDuckGo rate limiting documented in DEBT.md.

### Finding 20 — `os.cpu_freq()` requires Python 3.13+ (MiniMax C3, Kimi)
**Severity**: HIGH
**Action**: ACCEPTED. Use `psutil.cpu_freq()` if psutil is available, else None. Do NOT use `os.cpu_freq()` (doesn't exist in Python 3.11). Alternatively, use platform-specific fallback: Linux `/proc/cpuinfo`, Windows WMI, macOS `sysctl`.

### Finding 22 — `innerHTML` XSS risk in Log drawer (MiniMax D5)
**Severity**: MEDIUM
**Action**: ACCEPTED (applies to Plan 8). Plan 7's web search skill results must be rendered with `textContent`, not `innerHTML`, in the UI.

### Verdict
All CRITICAL/HIGH issues fixed. Plan 7 Rev3 is ready for execution.

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

Note: `httpx` is pulled transitively by `ollama` and IS used by the web search skill (per Finding 9, Rev3). It is NOT added directly to `txt/requirements.txt` — it's a transitive dependency.

### S2 — Create sovereignai/orchestrator/dispatcher.py

Create `sovereignai/orchestrator/dispatcher.py`:

**Purpose**: MessageDispatcher for v1. Receives natural language text from the user (via web UI), queries the CapabilityGraph for matching skills, submits the task, and returns a Task object. The caller polls the TaskStateMachine for completion.

**v1 simplification**: The dispatcher does NOT use an LLM for routing. It queries the CapabilityGraph for all registered skills, filters by **word-boundary keyword matching against `intent_keywords` from each skill's manifest** (per Finding 12, Rev4 — NOT substring, NOT regex on capability name). Returns highest-priority match. **Per Finding 13 (Rev4): If no skill matches, route to the Ollama `chat` skill** (registered with `intent_keywords = ["chat", "talk", "ask", "explain", "help", "what", "how", "why"]`) — this preserves the "always responds" UX promise. The catch-all is now an explicit named skill, not a silent fallback.

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
- `async def dispatch(message: str, token: str) -> Task`: **Per Finding 3 (Rev4)**: accepts `token` parameter for `CapabilityAPI.submit_task()`. Parse message, query CapabilityGraph for matching skills via `intent_keywords`, submit task via `CapabilityAPI.submit_task(token, category, capability_name, payload)`, return Task object.
- `_find_matching_skill(message: str) -> Optional[ComponentId]`: Query CapabilityGraph for skills, match using `re.search(rf'\b{keyword}\b', message, re.IGNORECASE)` against each skill's `intent_keywords` from manifest. Return highest-priority match. If no match, return `None` — caller routes to Ollama `chat` skill.

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
- Use `httpx` (per Finding 9 — already a transitive dep via `ollama`, respects proxy env vars) to fetch `https://html.duckduckgo.com/html/?q={query}`.
- Set `User-Agent: SovereignAI/0.1.0` header to identify requests.
- Parse HTML with `html.parser` from stdlib (no BeautifulSoup — avoid deps).
- Extract result titles and snippets from `.result__title` and `.result__snippet` classes.
- Return list of dicts: `[{"title": "...", "snippet": "...", "url": "..."}]`.
- Handle network errors gracefully: return empty list + error message in trace.
- **Per Finding 10**: Rate limiting: max 1 request per 2 seconds. If rate limited, return empty list + WARN trace.
- **Per Finding 10**: Document DuckDuckGo rate limiting risk in DEBT.md.
- No external dependencies beyond `httpx` (which is already transitively installed via `ollama`).

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
  - CPU frequency: **Per Finding 20**: Do NOT use `os.cpu_freq()` (requires Python 3.13+). Use `psutil.cpu_freq()` if available, else `None`.
  - RAM: `ctypes.windll.kernel32.GlobalMemoryStatusEx` on Windows; `os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')` on POSIX.
  - GPU/VRAM: **Per Finding 8**: Multi-platform GPU detection:
    - Windows: `subprocess.run(["wmic", "path", "win32_VideoController", "get", "Name,AdapterRAM", "/format:csv"])` — **Per Finding 16 (Rev4)**: use `/format:csv` not `--format:csv`. Parses ALL GPUs, not just NVIDIA.
    - macOS: `subprocess.run(["system_profiler", "SPDisplaysDataType"])` — parses system_profiler output.
    - Linux: `subprocess.run(["lspci", "-vmm"])` + `lspci -v -s <gpu_addr>` for VRAM.
    - Fallback: if all probes fail, `gpu_name=None`, `gpu_vram_mb=None`. UI renders "No GPU detected".
  - CPU frequency: **Per Finding 20**: Do NOT use `os.cpu_freq()` (requires Python 3.13+). Use `psutil.cpu_freq()` if available, else `None`.
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
    # Per Finding 2 (Rev5): extract session cookie as token for CapabilityAPI.submit_task()
    token = request.cookies.get("session_id", "")
    dispatcher = container.retrieve(MessageDispatcher)
    task = await dispatcher.dispatch(message, token=token)
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
- If web search skill adds any non-stdlib import other than `httpx` (which is a transitive dep via `ollama`), STOP.
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
