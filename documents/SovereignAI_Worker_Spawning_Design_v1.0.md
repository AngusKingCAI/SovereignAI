# SovereignAI -- Worker Spawning Design Document v1.0

**Status**: Draft -- approved for implementation  
**Date**: 2026-07-03  
**Author**: Architect  
**Depends on**: `principles.md`, `AGENTS.md`, `DECISIONS.md`, `AI_HANDOFF.md`, `SovereignAI_Skill_Agent_System_Design_v1.0.md`

---

## 1. Context

**Gap**: #9 -- Worker Spawning  
**Problem**: The codebase needs async task execution with worker pool management, but the existing adapters (OllamaAdapter, TestWorker) are synchronous.  
**Scope**: How workers get created, executed, and managed without rewriting the core sync infrastructure.

---

## 2. Factual Audit

**Verified from live repo** (`adapters/external/ollama_adapter/adapter.py`):
```python
import threading  # sync client, not asyncio

def generate(self, prompt: str, ...) -> str:  # SYNC
    thread = threading.Thread(target=_generate, daemon=True)
    thread.start()
    thread.join(timeout=timeout_seconds)
```

**Verified from live repo** (`sovereignai/workers/test_worker.py`):
```python
def process_task(self, task_id: str) -> str:  # SYNC
    result = adapter.generate(prompt_text)  # sync call to sync adapter
```

**Verified from live repo** (`sovereignai/shared/event_bus.py`):
```python
class EventBus:
    def publish(self, event: Event) -> None:
        with self._lock:  # threading.Lock, not asyncio
            ...
```

**Conclusion**: Zero async in adapters, workers, trace emitter, event bus, capability graph, memory backends, librarian, task state machine. All sync. The async boundary exists only at the web layer (FastAPI).

---

## 3. Design Decision

**DD-21.0.1**: Worker spawning model (Proposed, P4/P5/P13/AR7-aligned): Thread pool (ThreadPoolExecutor, max 4 workers). Sync workers call sync adapters via `worker.process_task(task)`. WorkerPool.submit(task_id, worker, task) -> Future runs in thread, returns immediately. AR7 circuit breaker per worker (>50 errors in 10s = unload, no auto-restart). WorkerPool.shutdown() drains in-flight via executor.shutdown(wait=True, cancel_futures=True).

---

## 4. Architecture

### 4.1 Async/Sync Boundary

```
Web layer (async)          Core (sync)
-----------------          -----------
FastAPI endpoints    ->     Orchestrator (async dispatch)
SSE streaming        ->     EventBus (sync API, async internal per DD-20.10.7)
async dispatch()     ->     WorkerPool.submit() (sync)
                       ->     sync workers (thread pool)
                       ->     sync adapters (Ollama, llama.cpp)
                       ->     sync memory backends
```

The async boundary stays at the web layer (existing pattern). No adapter rewrites.

### 4.2 WorkerPool

```python
from concurrent.futures import ThreadPoolExecutor, Future
from threading import Lock

class WorkerPool:
    def __init__(self, max_workers: int = 4, trace: TraceEmitter) -> None:
        self._trace = trace
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._active: dict[str, Future] = {}
        self._lock = Lock()
        self._error_counts: dict[str, list[float]] = {}  # AR7 breaker

    def submit(self, task_id: str, worker: Worker, task: Task) -> Future:
        with self._lock:
            future = self._executor.submit(self._run_with_breaker, task_id, worker, task)
            self._active[task_id] = future
            future.add_done_callback(lambda f: self._cleanup(task_id))
        self._trace.emit(component="worker_pool", level=TraceLevel.INFO, ...)
        return future

    def _run_with_breaker(self, task_id: str, worker: Worker, task: Task) -> str:
        try:
            return worker.process_task(task)
        except Exception as exc:
            self._record_error(worker.worker_id)
            raise

    def shutdown(self) -> None:
        self._executor.shutdown(wait=True, cancel_futures=True)

    def cancel(self, task_id: str) -> bool:
        with self._lock:
            future = self._active.get(task_id)
            return future.cancel() if future else False
```

### 4.3 AR7 Circuit Breaker

```python
def _record_error(self, worker_id: str) -> None:
    now = time.time()
    self._error_counts.setdefault(worker_id, []).append(now)
    # Purge errors outside 10s window
    self._error_counts[worker_id] = [
        t for t in self._error_counts[worker_id] if now - t < 10
    ]
    if len(self._error_counts[worker_id]) > 50:
        self._unload_worker(worker_id)

def _unload_worker(self, worker_id: str) -> None:
    self._trace.emit(
        component="worker_pool",
        level=TraceLevel.ERROR,
        event="worker.unloaded",
        worker=worker_id,
        reason="circuit_breaker",
        error_count=50,
        window_s=10
    )
    # No auto-restart per AR7
```

---

## 5. Why Not Asyncio (B)

**Premise failure**: "All worker code is already async" is factually false.

**Required rewrites if B chosen**:
- OllamaAdapter: `ollama` client is sync. Need `asyncio.to_thread()` wrapper OR aiohttp direct REST calls.
- LlamaCppAdapter: `llama-cpp-python` is sync. Same problem.
- TestWorker: `process_task()` calls `adapter.generate()` -- sync.
- EventBus: `threading.Lock` -> `asyncio.Lock`.
- Memory backends: SQLite operations -> `aiosqlite`.

**Scope**: Rewrite ~40% of core. P5 violation: speculative rewrite for cancellation benefit v1 doesn't need.

**Comparison**:

| Criterion | A (thread pool) | B (asyncio) |
|-----------|----------------|-------------|
| Existing adapters work? | Yes (sync, called from threads) | No (must rewrite to async) |
| Existing TestWorker works? | Yes | No (must rewrite to async) |
| EventBus compatible? | Yes (sync publish API) | Requires async publish API |
| Delta from existing code | Small (add WorkerPool class) | Large (rewrite adapters + workers + boundary) |
| P5 (no speculative contracts) | Yes | No (speculative async rewrite) |
| GIL concern for I/O work | None (I/O releases GIL) | N/A |
| Cancellation | Future.cancel() (limited) | Task.cancel() (cleaner) |

Cancellation advantage of B is real but minor for v1. Worker count is 4, not 4000. Thread pool shutdown is adequate.

---

## 6. Why Not Process Pool (C)

- **P4 (Windows)**: Process spawn is slow on Windows.
- **Serialization overhead**: Every task argument and result must be pickled.
- **No GIL bottleneck**: SovereignAI workload is I/O-bound (LLM HTTP calls), not CPU-bound.

---

## 7. Why Not Hybrid Async+Thread (D)

- Adds complexity without benefit.
- Codebase already has clean async/sync boundary at web layer.
- D would add a second async/sync boundary inside the core.

---

## 8. Rejected Alternatives

### 8.1 B -- Asyncio
- **Why rejected**: Factually incompatible with existing sync codebase. Requires rewriting adapters, workers, EventBus, memory backends. P5 violation.
- **Consequence**: ~40% core rewrite. Coroutine coloring problem metastasizes through entire system.

### 8.2 C -- Process Pool
- **Why rejected**: P4 concern (Windows process spawn slow). Serialization overhead. No CPU-bound workload to justify.
- **Consequence**: Slower task startup. Complex state passing.

### 8.3 D -- Hybrid Async+Thread
- **Why rejected**: Adds second async/sync boundary. No concrete benefit over existing pattern.
- **Consequence**: Unnecessary complexity.

---

## 9. Rationale

| Principle | How A Honors It |
|-----------|----------------|
| P5 (no speculative contracts) | Uses existing sync adapters as-is. No rewrite. |
| P4 (local-first, Windows) | ThreadPoolExecutor works well on Windows. |
| P13 (strong and robust) | AR7 breaker per worker. Graceful shutdown. |
| P9 (observability) | Every submit/complete/error emits trace. |

---

## 10. Extension Points

| Extension | Trigger | Interface |
|-----------|---------|-----------|
| Async workers | Streaming LLM responses | Supersede with B or D |
| High-concurrency web | Many concurrent requests | Supersede with B |
| CPU-bound workloads | Embeddings, AST parsing at scale | Supersede with D |

**Supersede path**: If streaming LLM responses, high-concurrency web serving, or CPU-bound workloads arrive, supersede with B or D. Document trigger condition in superseding DD.

---

## 11. Data Structures

```python
@dataclass(frozen=True)
class Task:
    task_id: str
    task_type: str
    payload: dict[str, Any]

class Worker(Protocol):
    worker_id: str
    def process_task(self, task: Task) -> str: ...
```

---

## 12. Open Questions

| ID | Question | Status |
|----|----------|--------|
| Q-21.0.1 | Should WorkerPool support priority queues (high-priority tasks first)? | Deferred |
| Q-21.0.2 | Should workers be pre-warmed (started before tasks arrive)? | Deferred |
| Q-21.0.3 | Should WorkerPool metrics be exposed (queue depth, active workers)? | Deferred |

---

## 13. Implementation Plan

**Plan 21.0** (Worker Spawning -- new plan, slots before 21.1):
- S1: WorkerPool class with ThreadPoolExecutor
- S2: AR7 circuit breaker integration
- S3: Task/Future tracking and cancellation
- S4: Graceful shutdown
- S5: Tests for concurrency, breaker, cancellation

---

*End of document.*
