Depends on: prompt-20.9.9
Vision principles: P1 (core sacred), P2 (pluggable), P5 (wire as you go), P11 (DI only)
Open questions resolved: none

S0.4 best practices: Pydantic structured output proven more reliable than native function calling for local 7B models (SWE-1.6 research). Session state via contextvar + DI injection avoids global mutable state. Skill manifest follows adapter pattern: manifest.toml + module.py, no import at discovery time. defusedxml required for safe XML parsing on untrusted LLM input.

## S0 — Opening

S0.1 — Run /open. Verify prompt-20.9.9 tag exists on origin. Working copy clean on main.
S0.2 — Read AGENTS.md in full.
S0.3 — No new rules for this plan.

## Plan Body

### S0.5 — Create CapabilityGraph in sovereignai/shared/capability_graph.py
- Real class with methods: register(name: str, cls: type) -> None (rejects duplicates with ValueError), resolve(name: str) -> type, list_capabilities() -> list[str].
- Runtime type check: register() rejects non-class values (e.g., int, str) with TypeError.
- No module-level global instance; instantiated in DI container per plan.
- This is the shared registry primitive used by Plans 21-24.

### S1 — Create ISkillRunner protocol in sovereignai/skills/runner.py
- Protocol with methods: run(skill_id, args, session), health_check(), list_capabilities(), close() (optional, default no-op).
- No concrete implementation imports in protocol file.
- run() returns SkillResult Pydantic BaseModel: output, error, execution_time_ms.

### S1.1 — Create ConcreteSkillRunner in sovereignai/skills/concrete_runner.py
- Implements ISkillRunner.
- Constructor injects CapabilityGraph for skill_id → manifest resolution.
- Module loaded via importlib once per skill_id and cached in _module_cache dict.
- Cache invalidation is process-scoped. Modifications to skill code require process restart. Hot-reload is explicitly out of scope; track in DEBT.md for a future plan (target: plan TBD when dev feedback cycle becomes pain point).
- run() resolves skill_id via CapabilityGraph, loads module via importlib, caches reference. Verification checks cached module identity, not fresh import per call.

### S2 — Create SkillManifest dataclass in sovereignai/skills/manifest.py
- Fields: id, name, version, capabilities list, execution config (runner, timeout), dependencies: list[str], memory integration hints.
- Capability schema: Pydantic model reference + auto-generated compact summary for LLM prompts.
- from_toml(path) classmethod reads manifest only — no code import. Validate code path via pathlib.Path.exists() only. Never call importlib or exec() on skill code during discovery.
- Each skill's manifest.toml gains optional [dag] section with dependencies = []. Parsed by from_toml() as list[str]. DAG semantics deferred to a future executor plan; from_toml() parses only, no cross-reference validation.

### S3 — Create SkillSession in sovereignai/skills/session.py
- Session-scoped state dict keyed by correlation_id (AR23).
- Injected via DI container, not global. Methods: get(key), set(key, value), get_history().
- History: list of Turn dataclasses (role, content, timestamp).

### S4 — Create ToolCallParser in sovereignai/skills/parser.py
- Hybrid: try JSON first, fallback to XML <tool_call> tags.
- Pluggable: register_format(name, parser_func). Raises ValueError on duplicate format name.
- Returns ToolCall Pydantic BaseModel: name, arguments dict.
- XML parsing uses defusedxml.ElementTree (add defusedxml to txt/requirements.txt per OR14).
- If XML parsing fails (after JSON parsing has already failed), return ToolCallErrorObservation with retryable=True. Do not attempt heuristics or regex extraction on malformed XML.

### S5 — Create ToolErrorObservation in sovereignai/skills/observation.py
- Pydantic BaseModel. Fields: error_type, message, suggestion, retryable.
- to_prompt_str() formats for LLM continuation.
- Web DTOs and Librarian persistence use .model_dump().

### S6 — Create initial skills in skills/official/
- file_read: read file path, return content. Manifest + skill.py + DAG JSON (AR9).
- file_write: write content to path. Manifest + skill.py + DAG JSON.
- file_search: search files by pattern. Manifest + skill.py + DAG JSON. Constrains search to project_root (configurable, defaults to repo root). Excludes hidden directories (.git/, .venv/, .tox/), binary file extensions by MIME sniff, and max depth of 10. Symlinks are not followed. Pattern is glob-based only, no regex. Error if path escapes project_root.
- Each skill produces identical output: manifest + code + DAG (AR9). Simple skills produce trivial 1-node DAG: {nodes: [{id: 'root', type: 'tool', name: skill_id}], edges: []}. DAG serialized as JSON alongside manifest.

### S7 — Create SkillDiscovery in sovereignai/skills/discovery.py
- Scan skills/ and adapters/ for manifest.toml.
- Read manifest only (no code import for discovery). Validate code path via pathlib.Path.exists() only.
- Register discovered capabilities in CapabilityGraph per DD-21.1.10.
- After all manifests scanned, log discovery-time warning (not error) for any dangling DAG dependency references. Do not block discovery.
- Add test asserting sys.modules is unchanged after SkillDiscovery.scan(). Test snapshots sys.modules.keys() before scan and asserts no new keys after (allowlist: stdlib modules via sys.stdlib_module_names + defusedxml).

### S8 — Wire in main.py build_container()
- Register ISkillRunner interface mapped to ConcreteSkillRunner implementation as singleton.
- Register SkillDiscovery.
- Register SkillSession provider.
- Register CapabilityGraph as singleton.

### S9 — Create web endpoints in web/main.py
- /api/skills GET: list discovered skills. Returns SkillListDTO.
- /api/skills/{skill_id}/execute POST: execute skill with args. Returns SkillResultDTO.
- Enable/disable endpoints deferred — add DEBT.md entry with target plan TBD.
- DTOs in web/schemas.py: SkillListDTO, SkillExecuteDTO, SkillResultDTO.

### S10 — Update TUI skills panel (tui/panels/skills.py)
- WILL edit: skills.py — add skill detail view, execution button.
- WILL NOT edit: other panels.
- Follow compose() -> on_mount() -> _load_data() pattern; call /api/skills via CapabilityAPI only in _load_data().

### S11 — Create tests
- test_skill_runner.py: protocol conformance, path resolution from relative paths, import-once behavior, test_module_cached_per_skill_id (asserts same object identity on repeated calls).
- test_skill_manifest.py: manifest parsing, no-import guarantee, sys.modules unchanged, dag_parse_simple, dag_parse_missing_optional.
- test_tool_call_parser.py: JSON + XML parsing, pluggable format, malformed XML rejection, duplicate format name rejection.
- test_skill_session.py: session state isolation by correlation_id.
- test_skill_discovery.py: auto-discovery, explicit disable, dangling dependency warning logged.
- test_file_search.py: test_depth_bounded, test_hidden_dir_excluded, test_symlink_not_followed, test_glob_only_rejects_regex.
- test_skills_api.py: list endpoint returns correct DTO, execute endpoint with mock skill, auth rejection without cookie.

### S12 — Run /verify after each edit. Run /close.
