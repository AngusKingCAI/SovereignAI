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
- S1.2: Create adapters/external/llama_cpp_adapter/manifest.toml — component_id="llama_cpp_adapter", version="0.1.0", capabilities=["model.inference"], routing_priority=20 (Ollama adapter manifest gets routing_priority=10 in same step — verify and edit if missing).
- S1.3: Create adapters/external/llama_cpp_adapter/adapter.py — LlamaCppAdapter. Constructor args: trace, hardware_probe, model_path_resolver (Callable[[str], Path]). ≤15 args (AR5). No globals (AR4). No context bags (AR6).
- S1.4: load_model(model_id: str) -> None: resolve model path via model_path_resolver, verify GGUF magic bytes, compute VRAM budget from HardwareProbe.sample().gpus[0].vram_total_mb, call llama_model_load with n_gpu_layers = max(0, vram_budget // (model.vram_required_mb // 35)). Emit trace on load start/complete/failure.
- S1.5: generate(prompt: str, max_tokens: int, temperature: float) -> str: tokenize via llama_tokenize, decode loop via llama_decode with sampling. Emit trace per 50-token batch (OR61). Return generated string.
- S1.6: health_check() -> AdapterHealth: probe `import llama_cpp` in try/except. Return AdapterHealth(healthy: bool, detail: str).
- S1.7: Add txt/requirements.txt: `llama-cpp-python>=0.2.50`.
- S1.8: Edit adapters/external/ollama_adapter/manifest.toml — add routing_priority=10 if absent.
- S1.9: Run /verify on each. Add tests/test_llama_cpp_adapter.py with llama_cpp mocked.

## S2 — RoutingEngine failover
- S2.1: Edit sovereignai/shared/routing_engine.py — route() reads routing_priority from registered component metadata. On adapter exception (typed AdapterUnavailableError), try next adapter in priority order. Log failover as trace event with old_adapter_id, new_adapter_id, capability.
- S2.2: Edit sovereignai/shared/capability_graph.py — store routing_priority on register(). Add method `adapters_by_capability(capability: str) -> list[ComponentMetadata]` sorted by routing_priority ascending.
- S2.3: Edit sovereignai/shared/types.py — add `AdapterUnavailableError` exception, `ComponentMetadata` dataclass (component_id, version, capabilities, routing_priority).
- S2.4: Run /verify on each. Extend tests/test_routing_engine.py with failover test (mock Ollama adapter raises AdapterUnavailableError, llama.cpp adapter succeeds, verify failover trace emitted).

## S3 — First-run experience (functional if either adapter installed)
- S3.1: Edit sovereignai/main.py build_container() — after manifest loading, query CapabilityGraph for healthy model.inference adapters. If none: emit WARN trace "No inference adapter healthy — install Ollama or llama.cpp". Do NOT raise (system runs without inference).
- S3.2: Edit web/main.py — add `GET /api/first-run-check` returning FirstRunStatusDTO (healthy_adapters: list[str], instructions: str).
- S3.3: WILL edit UI: web/templates/index.html — Models panel empty-state distinguishes "no models in DB" vs "no healthy adapter". web/static/app.js — loadModelsPanel() fetches /api/first-run-check, shows adapter-install prompt if healthy_adapters empty. web/schemas.py — add FirstRunStatusDTO.
- S3.4: Run /verify after each. Add tests/test_first_run_adapter_check.py covering: GET returns 200; empty healthy_adapters list when both adapters fail health_check; non-empty when at least one healthy.

## S4 — P4 compliance verification (mechanical)
- S4.1: Create scripts/ar_checks/check_p4_compliance.py — mechanical scan: (a) count adapters in adapters/external/ with manifest declaring capability "model.inference" — must be ≥2; (b) verify RoutingEngine tests cover failover; (c) verify main.py does not require any single adapter to start (grep for hard `raise` on adapter absence — forbidden). Exit≠0 on violation.
- S4.2: Edit .devin/workflows/close.md step 8 — add check_p4_compliance.py to AR checks list.
- S4.3: Run /verify. Add tests/test_p4_compliance.py.

## S5 — Vision compliance scorecard
- S5.1: In documents/plan-19-report.md (written at /close step 14.5), add "Vision Compliance Scorecard" section listing P1-P14 status (Active/Deferred/Violated) with evidence (file path or test name). Each Active principle must cite a passing test or implemented file. Deferred principles must cite DEBT.md entry.

## Closing
- Run /close (full suite, coverage ≥90%, all AR checks including check_p4_compliance.py, browser smoke test on first-run UX, spec_match.py, commit, tag prompt-19, push).
