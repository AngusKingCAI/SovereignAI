# SovereignAI -- Hardware Panel SSE Streaming Design Document v1.0

**Status**: Draft -- approved for implementation  
**Date**: 2026-07-03  
**Author**: Architect  
**Depends on**: `../PRINCIPLES.md`, `../AGENTS.md`, `../DECISIONS.md`, `../AI_HANDOFF.md`, `SovereignAI_Skill_Agent_System_Design_v1.0.md`

---

## 1. Context

**Gap**: #14 -- Hardware Panel SSE Streaming  
**Problem**: The TUI panels call `sample_hardware()` on refresh, not streaming. The web layer needs live hardware stats.  
**Scope**: How live hardware stats reach the UI without violating existing architecture.

---

## 2. Existing Infrastructure

**Verified from live repo** (`sovereignai/shared/capability_api.py`):
```python
async def stream_hardware(self) -> AsyncGenerator[HardwareSnapshot, None]:
    ...  # Already exists
```

**AR24 precedent**: "Logs panel must consume /api/traces SSE only -- no direct TraceEmitter import from web/."

---

## 3. Design Decision

**DD-21.5.1**: Hardware panel SSE streaming (Proposed, P8/AR13/AR24-aligned): Web layer ships `/api/hardware/stream` SSE endpoint wrapping existing `CapabilityAPI.stream_hardware()` async generator. No reimplementation -- web layer is a thin proxy that formats `HardwareSnapshot` as SSE data: lines. Connection management via `request.is_disconnected()`. Auth via HTTP session cookie per AR13 (same as existing `/api/traces/stream` per AR24).

---

## 4. Endpoint

```python
@app.get("/api/hardware/stream")
async def hardware_stream(request: Request):
    async def event_generator():
        async for snapshot in capability_api.stream_hardware():
            if await request.is_disconnected():
                break
            yield f"data: {snapshot.model_dump_json()}

"
    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

**Key points**:
- Uses **existing** `stream_hardware()` -- no reimplementation
- `request.is_disconnected()` prevents zombie generators
- `stream_hardware()` controls frequency; web layer is transparent proxy
- Single source of truth for rate

---

## 5. Why Not EventBus (B)

**DD-20.10.8 violation**: "All events persist to episodic memory via Librarian."

Hardware stats at 1Hz = 86,400 events/day. At ~200 bytes/event = ~17MB/day = ~6GB/year of episodic memory consumed by telemetry that's only useful for 60 seconds.

**Telemetry categorization**:

| Data type | Transport | Storage | Scope | Example |
|-----------|-----------|---------|-------|---------|
| Business event | EventBus -> Librarian | Episodic (SQLite) | Cross-run | coding.task.created |
| Trace event | TraceEmitter -> FileTraceSubscriber | sailogs/ (JSONL) | Single-run | adapter.generate.start |
| Telemetry | CapabilityAPI.stream_*() | sailogs/ (if traced) | Real-time only | HardwareSnapshot |

Putting telemetry on EventBus conflates rows 1 and 3. Hardware stats belong in row 3 -- real-time streaming via CapabilityAPI, optionally traced to sailogs/, never persisted to episodic memory.

**AR24 violation**: Web layer shouldn't subscribe to core event buses; it should consume via API endpoints.

---

## 6. Why Not Polling Only (C)

- Works for localhost but inconsistent with AR24 precedent (traces use SSE).
- Future relay/phone access (P6 deferred) would require rework.

---

## 7. TUI Behavior

**Continues polling** `sample_hardware()` via Textual `set_interval`. No SSE client in TUI -- framework mismatch.

**P8-compliant**: Both web and TUI connect to the same CapabilityAPI. Different methods for different frameworks:
- Web: `stream_hardware()` (async generator -> SSE)
- TUI: `sample_hardware()` (sync snapshot -> periodic refresh)

**P9 caveat**: TUI must surface `sample_hardware()` errors visibly. Stale-data-as-if-current is silent failure (P9 violation).

---

## 8. Frequency Configuration

```python
# capability_api.py
async def stream_hardware(self, interval_seconds: float = 1.0) -> AsyncGenerator[HardwareSnapshot, None]:
    ...
```

Web endpoint accepts query param: `/api/hardware/stream?interval=2.0`
TUI polling interval set via `set_interval` per panel.

---

## 9. Rejected Alternatives

### 9.1 B -- EventBus -> Web Proxy
- **Why rejected**: DD-20.10.8 violation (6GB/year episodic bloat). AR24 violation (web subscribes to core bus).
- **Consequence**: Telemetry persisted as business events.

### 9.2 C -- Polling Only
- **Why rejected**: Inconsistent with AR24 precedent. Future relay access requires rework.
- **Consequence**: Inconsistent architecture.

### 9.3 Reimplementing stream_hardware() in Web Layer
- **Why rejected**: P5 violation. `stream_hardware()` already exists.
- **Consequence**: Duplicate code, drift risk.

---

## 10. Rationale

| Principle | How A Honors It |
|-----------|----------------|
| P8 (UIs separate) | Web layer consumes via API endpoint. TUI polls same API. |
| AR13 (SSE auth) | Cookie auth already implemented. |
| AR24 (SSE precedent) | Follows `/api/traces/stream` pattern. |
| P5 (no reimplementation) | Wraps existing `stream_hardware()`. |

---

## 11. Data Structures

```python
@dataclass(frozen=True)
class HardwareSnapshot:
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    gpu_utilization: float | None
    vram_used_mb: int | None
    vram_total_mb: int | None
    disk_usage_percent: float
```

---

## 12. Extension Points

| Extension | Trigger | Interface |
|-----------|---------|-----------|
| Thermal data | GPU temperature monitoring | Add fields to HardwareSnapshot |
| Process-level stats | Per-process resource tracking | `stream_processes()` separate stream |
| Historical trends | Long-term analysis | Sample to sailogs/ periodically |

---

## 13. Open Questions

| ID | Question | Status |
|----|----------|--------|
| Q-21.5.1 | Should hardware telemetry ever be sampled to episodic memory for trend analysis? | Deferred |
| Q-21.5.2 | Should thermal data be included in HardwareSnapshot? | Deferred |
| Q-21.5.3 | Should web endpoint support filtering (CPU only, GPU only)? | Deferred |

---

## 14. Implementation Plan

**Plan 21.5.1** (Hardware SSE Streaming):
- S1: Add `/api/hardware/stream` endpoint to web/main.py
- S2: Add `request.is_disconnected()` check
- S3: Add `?interval=` query param support
- S4: Verify AR13 cookie auth applied
- S5: Tests for SSE format, disconnection, auth

**No core changes** -- `stream_hardware()` already exists.

---

*End of document.*
