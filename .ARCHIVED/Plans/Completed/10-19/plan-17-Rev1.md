Depends on: Plan 16
Vision principles: P2 (everything pluggable), P3 (no provider lock-in), P4 (local-first), P5 (wire as you go)
Open questions resolved: none

## S0 — Opening
- S0.1: Run /open (verify tag prompt-16 on origin)
- S0.2: Read AGENTS.md in full
- S0.2.5: Re-read AGENTS.md if S0.3 adds rules
- S0.3: Add OR67 (databases/ and services/ are root-level packages, never nested in sovereignai/), OR68 (every ServiceProvider and DatabaseProvider exposes health_check() returning typed status dataclass), commit before coding

## S1 — Root-level packages + core registries
- S1.1: Create databases/ package: databases/__init__.py empty.
- S1.2: Create databases/base.py defining `DatabaseStatus` dataclass (installed: bool, version: str | None, size_bytes: int | None) and `DatabaseProvider` protocol (name: str, list_models() -> list[ModelEntry], download_model(model_id: str), update_model(model_id: str), uninstall_model(model_id: str), health_check() -> DatabaseStatus).
- S1.3: Create services/ package: services/__init__.py empty.
- S1.4: Create services/base.py defining `ServiceStatus` dataclass (running: bool, pid: int | None, port: int | None) and `ServiceProvider` protocol (name: str, start(), stop(), health_check() -> ServiceStatus).
- S1.5: Create sovereignai/shared/database_registry.py — DatabaseRegistry class. Constructor: trace. Methods: register(name, provider), list_databases() -> list[str], get_database(name) -> DatabaseProvider. No globals (AR4).
- S1.6: Create sovereignai/shared/service_registry.py — ServiceRegistry class. Constructor: trace. Methods: register(name, provider), list_services() -> list[str], get_service(name) -> ServiceProvider, start_all(), stop_all().
- S1.7: Create sovereignai/shared/types.py addition: `ModelEntry` dataclass (org, family, version, quant, file_size_bytes, vram_required_mb, category, source_db: str).
- S1.8: Run /verify on each. Add tests/test_database_registry.py and tests/test_service_registry.py covering register/retrieve/start_all/stop_all with fake providers.

## S2 — HuggingFace database provider
- S2.1: Create databases/hf_database/ package: databases/hf_database/__init__.py empty.
- S2.2: Create databases/hf_database/provider.py — HFDatabaseProvider implementing DatabaseProvider. Constructor: trace, cache_dir: Path. Methods call huggingface_hub library.
- S2.3: list_models() returns list[ModelEntry] by calling HfApi().list_models(filter="gguf", sort="downloads", direction=-1, limit=500). Cache result in-memory for 1 hour. Map HF fields to ModelEntry.
- S2.4: download_model(model_id): hf_hub_download to ~/.sovereignai/models/{org}/{name}/. Emit trace on start/progress/complete/failure. Atomic metadata write per OR50.
- S2.5: update_model(model_id): re-pull latest revision. uninstall_model(model_id): delete local dir (temp + os.replace for metadata file).
- S2.6: health_check(): probe ~/.cache/huggingface and HF API endpoint. Return DatabaseStatus.
- S2.7: Add txt/requirements.txt entry: `huggingface_hub>=0.20.0`.
- S2.8: Run /verify. Add tests/test_hf_database.py with hf_hub mocked.

## S3 — Ollama service provider
- S3.1: Create services/ollama_service/ package: services/ollama_service/__init__.py empty.
- S3.2: Create services/ollama_service/provider.py — OllamaServiceProvider implementing ServiceProvider. Constructor: trace, port: int = 11434.
- S3.3: start(): check `ollama` on PATH via shutil.which. If absent, raise typed ServiceNotFoundError. Spawn `ollama serve` as subprocess, capture pid, poll http://localhost:{port}/api/version until 200 or 10s timeout. Emit trace.
- S3.4: stop(): terminate subprocess via SIGTERM, wait 5s, SIGKILL fallback.
- S3.5: health_check(): GET /api/version. Return ServiceStatus with running=True if 200.
- S3.6: Run /verify. Add tests/test_ollama_service.py with subprocess + HTTP mocked.

## S4 — Wire into main.py + Options panel UI
- S4.1: Edit sovereignai/main.py build_container() — instantiate DatabaseRegistry and ServiceRegistry, register HFDatabaseProvider and OllamaServiceProvider, add to DI container. Guard with `if not _test_mode`.
WILL edit UI elements:
- web/templates/index.html: replace `<section id="panel-options">` content with three tabs (Model Services / Model Databases / Authentication). Each provider row: name, status badge, three buttons (Start-or-Download / Update / Stop-or-Uninstall).
- web/static/app.js: add `loadOptionsPanel()` fetching /api/databases and /api/services, renders rows, wires button clicks to POST endpoints.
- web/static/styles.css: add `.options-tabs`, `.provider-row`, `.status-badge`, `.tab-button` styles.
- web/main.py: add `GET /api/databases` -> list[dict]; `GET /api/services` -> list[dict]; `POST /api/databases/{name}/{action}` (action in download_model/update_model/uninstall_model); `POST /api/services/{name}/{action}` (action in start/stop). All emit success traces.
- web/schemas.py: add `DatabaseProviderDTO`, `ServiceProviderDTO`.
- S4.2: Edit each file per WILL list. Run /verify after each edit.
- S4.3: Add tests/test_options_panel.py covering: GET endpoints return 200 with provider list; POST endpoints invoke provider methods; unknown provider returns 404; action validation.

## Closing
- Run /close (full suite, coverage ≥90%, all AR checks, browser smoke test on Options panel, spec_match.py, commit, tag prompt-17, push).
