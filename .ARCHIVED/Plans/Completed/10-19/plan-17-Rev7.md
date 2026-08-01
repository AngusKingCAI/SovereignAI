Depends on: Plan 16
Vision principles: P2 (everything pluggable), P3 (no provider lock-in), P4 (local-first), P5 (wire as you go)
Open questions resolved: none

## S0 — Opening
- S0.1: Run /open (verify tag prompt-16 on origin)
- S0.2: Read AGENTS.md in full
- S0.2.5: Re-read AGENTS.md if S0.3 adds rules
- S0.3: Add OR67 (databases/ and services/ are root-level packages, never nested in sovereignai/), OR68 (every ServiceProvider and DatabaseProvider exposes health_check() returning typed status dataclass; provider __init__ must not perform I/O — lazy execution only in start()/list_models()), commit before coding

## S1 — Root-level packages + core registries
- S1.1: Create databases/ package: databases/__init__.py empty.
- S1.2: Create databases/base.py defining `DatabaseStatus` dataclass (installed: bool, version: str | None, size_bytes: int | None), `DatabaseProvider` protocol (name: str, list_models() -> list[ModelEntry], download_model(model_id: str), update_model(model_id: str), uninstall_model(model_id: str), health_check() -> DatabaseStatus), `NoCompatibleQuantError(Exception)` with `__init__(self, repo_id: str)`, and `ModelNotFoundError(Exception)` with `__init__(self, model_id: str)`.
- S1.3: Create services/ package: services/__init__.py empty.
- S1.4: Create services/base.py defining `ServiceStatus` dataclass (running: bool, pid: int | None, port: int | None), `ServiceProvider` protocol (name: str, start(), stop(), health_check() -> ServiceStatus), `ServiceNotFoundError(Exception)`, and `ServiceStartError(Exception)`.
- S1.5: Create sovereignai/shared/database_registry.py — DatabaseRegistry class. Constructor: trace. Methods: register(name, provider), list_databases() -> list[str], get_database(name) -> DatabaseProvider, find_model(model_id: str) -> tuple[str, ModelEntry] | None (iterates all registered DBs, returns (db_name, model) or None).
- S1.6: Create sovereignai/shared/service_registry.py — ServiceRegistry class. Constructor: trace. Methods: register(name, provider), list_services() -> list[str], get_service(name) -> ServiceProvider, start_all(), stop_all().
- S1.7: Create sovereignai/shared/types.py addition: `ModelEntry` dataclass (org, family, version, quant, file_size_bytes, vram_required_mb, num_layers: int, category, source_db: str).
- S1.8: Run /verify on each. Add tests/test_database_registry.py and tests/test_service_registry.py covering register/retrieve/start_all/stop_all/find_model with fake providers.

## S2 — HuggingFace database provider
- S2.1: Create databases/hf_database/ package: databases/hf_database/__init__.py empty.
- S2.2: Create databases/hf_database/provider.py — HFDatabaseProvider implementing DatabaseProvider. Constructor: trace, cache_dir: Path. __init__ must not perform I/O (per OR68). Methods call huggingface_hub library lazily. Import NoCompatibleQuantError from databases.base.
- S2.3: list_models() returns list[ModelEntry] by calling HfApi().list_models(filter="gguf", sort="downloads", direction=-1, limit=500). Cache result in-memory with `time.monotonic()` timestamp; TTL=3600s hardcoded (configurable deferred). Re-fetch if `now - cache_time > 3600`. Map HF fields to ModelEntry including num_layers from model card metadata (default 32 if absent).
- S2.4: download_model(model_id): enumerate GGUF files in repo. Quant selection fallback chain: first q4_K_M → q4_K_S → q5_K_M → q5_K_S → q6_K → q8_0 → first available GGUF. Raise typed `NoCompatibleQuantError(repo_id)` if no GGUF present. Emit ERROR trace with detail=repo_id before raising. `hf_hub_download(repo_id=model_id, filename=<selected>, local_dir=str(Path.home() / ".sovereignai" / "models" / org / name), local_dir_use_symlinks=False)`. Note: use_symlinks=False trades disk for re-download speed; document trade-off in code comment; defer env var configurability to post-Plan-19. Persist selected filename in `~/.sovereignai/models/{org}/{name}/model_info.json` (atomic write per OR50) so load_model can read exact path instead of globbing. Atomic metadata write per OR50 (temp + os.replace). Emit trace on start/complete/failure.
- S2.5: update_model(model_id): re-pull latest revision, update model_info.json. uninstall_model(model_id): delete local dir (temp + os.replace for metadata file).
- S2.6: health_check(): probe ~/.cache/huggingface and HF API endpoint. Return DatabaseStatus.
- S2.7: Add txt/requirements.txt entry: `huggingface_hub>=0.20.0`.
- S2.8: Run /verify. Add tests/test_hf_database.py with hf_hub mocked. Assert __init__ performs no I/O. Test quant fallback chain (including q6_K). Test NoCompatibleQuantError on empty repo. Test local_dir uses Path.home() not literal "~". Test model_info.json persists selected filename.

## S3 — Ollama service provider
- S3.1: Create services/ollama_service/ package: services/ollama_service/__init__.py empty.
- S3.2: Create services/ollama_service/provider.py — OllamaServiceProvider implementing ServiceProvider. Constructor: trace, port: int = 11434. __init__ must not perform I/O (per OR68). Store port as instance attr for use in start()/health_check(). Import ServiceNotFoundError and ServiceStartError from services.base.
- S3.3: start(): check `ollama` on PATH via shutil.which. If absent: emit ERROR trace with detail="ollama not on PATH", raise typed ServiceNotFoundError. Spawn `ollama serve` as subprocess via `subprocess.Popen`, capture pid. Poll http://localhost:{self.port}/api/version until 200 or 10s timeout. On timeout: `proc.terminate()`, wait 2s, `proc.kill()` fallback, emit ERROR trace with detail=f"startup timeout: {reason}", raise ServiceStartError.
- S3.4: stop(): `proc.terminate()`, wait 5s, `proc.kill()` if still alive. Do NOT use signal.SIGTERM/SIGKILL (unsupported on Windows).
- S3.5: health_check(): GET /api/version on self.port. Return ServiceStatus with running=True if 200.
- S3.6: Run /verify. Add tests/test_ollama_service.py with subprocess + HTTP mocked. Include test with non-default port passed to constructor. Test trace emitted on ServiceNotFoundError. Test trace emitted on ServiceStartError with reason in detail.

## S4 — Wire into main.py + Options panel UI
- S4.1: Edit sovereignai/main.py build_container() — instantiate DatabaseRegistry and ServiceRegistry, register HFDatabaseProvider and OllamaServiceProvider, add to DI container. Guard with `if not _test_mode` (existing pattern from prompt-15.1).
WILL edit UI elements:
- web/templates/index.html: replace `<section id="panel-options">` with three tabs (Model Services / Model Databases / Authentication). Services + Databases: provider rows (name, status badge, Start-or-Download / Update / Stop-or-Uninstall buttons). Authentication: placeholder "Coming soon — deferred to future plan" + DEBT.md entry.
- web/static/app.js: add `loadOptionsPanel()` fetching /api/databases and /api/services, renders rows, wires button clicks.
- web/static/styles.css: `.options-tabs`, `.provider-row`, `.status-badge`, `.tab-button`.
- web/main.py: add `GET /api/databases` -> list[dict]; `GET /api/services` -> list[dict]; `POST /api/databases/{name}/{action}` (action in download_model/update_model/uninstall_model); `POST /api/services/{name}/{action}` (action in start/stop). All emit success traces.
- web/schemas.py: add `DatabaseProviderDTO`, `ServiceProviderDTO`.
- S4.2: Edit each file per WILL list. Run /verify after each edit.
- S4.3: Add tests/test_options_panel.py covering: GET endpoints return 200; POST endpoints invoke methods; unknown provider 404; action validation; Authentication tab present.
- S4.4: Add DEBT.md entry: "Authentication tab UI — deferred, target plan TBD."

## Closing
- Run /close (full suite, coverage ≥90% per OR43, all AR checks, browser smoke test on Options panel with screenshots to logs/screenshots/prompt-17/, spec_match.py, commit, tag prompt-17, push).
