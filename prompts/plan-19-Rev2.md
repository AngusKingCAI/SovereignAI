Depends on: Plan 18
Vision principles: P3 (no provider lock-in), P4 (local-first), P5 (wire as you go)
Open questions resolved: none (P4 minimum viable local — 2 adapters per session-context decision 12)

## S0 — Opening
- S0.1: Run /open (verify tag prompt-18 on origin)
- S0.2: Read AGENTS.md in full
- S0.2.5: Re-read AGENTS.md if S0.3 adds rules
- S0.3: Add OR70 (every adapter manifest declares `routing_priority` int — RoutingEngine routes ascending, lower = higher priority), commit before coding

## S1 — llama.cpp adapter scaffold
- S1.1: Create adapters/external/llama_cpp_adapter/ package: __init__.py empty.
- S1.2: Create adapters/external/llama_cpp_adapter/manifest.toml — component_id="llama_cpp_adapter", version="0.1.0", capabilities=["model.inference"], routing_priority=20.
- S1.3: Create adapters/external/llama_cpp_adapter/adapter.py — LlamaCppAdapter. Constructor args: trace, hardware_probe, model_path_resolver (Callable[[str], Path]). ≤15 args (AR5). Lazy import: `import llama_cpp` ONLY inside health_check()/load_model()/generate(), never at module top level. __init__ performs no I/O.
- S1.4: load_model(model_id: str) -> None: resolve path via model_path_resolver, verify first 4 bytes == b'GGUF' and version field == 3. Compute VRAM budget: `gpus = hardware_probe.sample().gpus; if not gpus: n_gpu_layers = 0; trace WARN "No GPU — CPU mode"; else: vram_budget_mb = gpus[0].vram_total_mb; denom = max(1, model.vram_required_mb // 35); n_gpu_layers = min(model.num_layers, vram_budget_mb * model.num_layers // max(1, model.vram_required_mb))`. Use high-level `llama_cpp.Llama(model_path=str(path), n_gpu_layers=n_gpu_layers)`. Emit trace on load start/complete/failure.
- S1.5: generate(prompt: str, max_tokens: int, temperature: float) -> str: wrap `self._llm.create_completion(...)` in try/except. On any exception: emit trace ERROR, raise `AdapterUnavailableError(detail=str(exc))`. Return generated text.
- S1.6: health_check() -> AdapterHealth: probe `import llama_cpp` in try/except. If import fails: return AdapterHealth(healthy=False, detail="llama-cpp-python not installed"). If n_gpu_layers > 0 requested: additionally probe `llama_cpp.llama_supports_gpu_offload()` if available; if False: return AdapterHealth(healthy=False, detail="GPU offload not supported in this build").
- S1.7: Add txt/requirements.txt: `llama-cpp-python>=0.2.50`. Add DEBT.md entry: "llama-cpp-python 0.2.50 — test with real binary before v1.0".
- S1.8: Edit adapters/external/ollama_adapter/manifest.toml (exists from Plan 7) — add `routing_priority = 10` field.
- S1.9: Run /verify on each. Add tests/test_llama_cpp_adapter.py with llama_cpp mocked. Cover: load_model with no GPU (n_gpu_layers=0); load_model with small model (denominator guard); generate failure raises AdapterUnavailableError; health_check import failure; health_check GPU-offload failure.

## S2 — RoutingEngine failover
- S2.1: Edit sovereignai/shared/routing_engine.py — route(): (a) get adapters via capability_graph.adapters_by_capability(capability) sorted by routing_priority ascending; (b) filter out adapters where health_check().healthy is False (emit trace WARN "adapter {id} unhealthy — skipping"); (c) for each remaining adapter: try call; on any exception, wrap in AdapterUnavailableError if not already; on AdapterUnavailableError, emit failover trace (old_adapter_id, new_adapter_id, capability) and try next; (d) if all exhausted: raise NoHealthyAdapterError. Single-adapter case: list of length 1 → try it → return result or propagate error (no silent fallback).
- S2.2: Edit sovereignai/shared/capability_graph.py — register() stores routing_priority from manifest. Add method `adapters_by_capability(capability: str) -> list[ComponentMetadata]` sorted by routing_priority ascending. Update manifest_parser.py to parse routing_priority field.
- S2.3: Edit sovereignai/shared/types.py — add `AdapterUnavailableError` exception, `NoHealthyAdapterError` exception, `ComponentMetadata` dataclass (component_id, version, capabilities, routing_priority), `AdapterHealth` dataclass (healthy: bool, detail: str).
- S2.4: Run /verify on each. Extend tests/test_routing_engine.py: (a) failover test (Ollama raises AdapterUnavailableError, llama.cpp succeeds, verify failover trace); (b) single-adapter returns its result; (c) single-adapter raises → error propagates (no silent fallback); (d) all unhealthy → NoHealthyAdapterError; (e) health_check filter skips unhealthy adapter.

## S3 — First-run experience
- S3.1: Edit sovereignai/main.py build_container() — after manifest loading, query CapabilityGraph for healthy model.inference adapters. If none: emit WARN trace "No inference adapter healthy — install Ollama or llama.cpp". Do NOT raise. Guard with `if not _test_mode` (existing pattern).
- S3.2: Edit web/main.py — add `GET /api/first-run-check` returning FirstRunStatusDTO (healthy_adapters: list[str], instructions: str).
- S3.3: WILL edit UI: web/templates/index.html — Models panel empty-state distinguishes "no models in DB" vs "no healthy adapter". web/static/app.js — loadModelsPanel() fetches /api/first-run-check, shows adapter-install prompt if healthy_adapters empty. web/schemas.py — add FirstRunStatusDTO.
- S3.4: Run /verify after each. Add tests/test_first_run_adapter_check.py covering: GET returns 200; empty healthy_adapters when both fail health_check; non-empty when at least one healthy; WARN trace emitted when none healthy.

## S4 — P4 compliance verification (mechanical)
- S4.1: Create scripts/ar_checks/check_p4_compliance.py — mechanical scan: (a) count adapters in adapters/external/ with manifest declaring capability "model.inference"; if <2, check DEBT.md for justification entry — if none, FAIL; (b) verify RoutingEngine tests cover failover + single-adapter + all-unhealthy; (c) AST scan: find Raise nodes in main.py whose exception type is AdapterNotFoundError/ServiceNotFoundError/etc. and which are NOT inside `if not _test_mode` block — forbidden. Exit≠0 on violation.
- S4.2: Edit .devin/workflows/close.md step 8 — add check_p4_compliance.py to AR checks list.
- S4.3: Run /verify. Add tests/test_p4_compliance.py.

## S5 — Vision compliance scorecard
- S5.1: In documents/plan-19-report.md (written at /close step 14.5), add "Vision Compliance Scorecard" section listing P1-P14 status (Active/Deferred/Violated) with evidence (file path or test name, NOT rule numbers — cite by content/filename to avoid numbering drift). Each Active principle must cite a passing test or implemented file. Deferred principles must cite DEBT.md entry.

## Closing
- Run /close (full suite, coverage ≥90% per OR43, all AR checks including check_p4_compliance.py, browser smoke test on first-run UX with screenshots to logs/screenshots/prompt-19/, spec_match.py, commit, tag prompt-19, push).
