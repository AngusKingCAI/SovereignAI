# SovereignAI — Models Panel: Provider Catalog Implementation Spec

**Audience:** GLM (implementing agent)
**Author:** Angus / Claude (design pass)
**Status:** Draft — partially superseded by Plan 17 (v1 MVP)
**Date:** 2026-07-01 (revised post-prompt-15.1)

---

> **Status note (post-Plan 17):** v1 implements the `DatabaseProvider` protocol directly (see Plan 17 §S1-S2) — each provider (HF, Ollama service) exposes `list_models() -> list[ModelEntry]` with a 1-hour in-memory cache. The 4-table SQLite catalog and per-provider sync jobs defined in §3-§5 below are **deferred** to a post-Plan-19 plan (DEBT.md entry). This document remains the canonical design for when sync-based durability is needed (offline browse, fast queries across thousands of models, surviving provider API outages). The `DatabaseProvider` protocol in Plan 17 is the contract under which any future sync-based implementation must plug in.

---

## 1. Goal

The `Models` panel currently has a row of tabs (Ollama, llama.cpp, HuggingFace, etc.) but only Ollama is wired up. We want every tab to show a **browsable catalog** of models for that provider/runtime, structured as:

```
Provider Tab (Ollama, llama.cpp, HuggingFace, vLLM, LM Studio, ...)
  └─ Publisher / Family (Meta/Llama, Google/Gemma, DeepSeek, Mistral, Alibaba/Qwen, ...)
       └─ Model (e.g. "Llama 3.3", "Qwen 3.6", "Gemma 4")
            └─ Version / Tag (e.g. "70b-instruct-q4_K_M", "27b", "e4b")
                 - size on disk
                 - VRAM requirement (and CPU-RAM fallback if relevant)
                 - context length
                 - capabilities (tools, vision, embedding, thinking)
                 - quantization
                 - pull/download command or API identifier
```

Clicking down each level should feel instant — this is browsing a **local cache/database**, not live-scraping a website on every click. A separate "Update databases" action in **Options** refreshes the cache from each provider's source.

This doc is purely about catalog browsing — it does not cover actually pulling/running models, which presumably already exists for Ollama (`ollama pull` integration).

> **v1 note:** Plan 17's `HFDatabaseProvider` uses an in-memory cache rather than the SQLite catalog below. The browse experience is the same; durability is deferred.

---

## 2. Why a local database, not live scraping per click

- `ollama.com/library` (and HuggingFace, etc.) is **not a stable JSON API** — it's an HTML page meant for browsers, and there's no first-party endpoint that returns the full catalog with tags/sizes/VRAM in one shot. Scraping it live on every UI click would be slow, fragile, and would break the moment the page markup changes.
- Each provider has a *different* shape of "catalog": Ollama has model→tags, HuggingFace has repos→files→quant variants, llama.cpp doesn't really have its own catalog at all (it just runs GGUF files, usually sourced from HuggingFace).
- We want offline/airgapped capability (P4 — local-first) — that means the catalog must be cached locally and refreshed on demand, not fetched live.

**Conclusion:** ingest each provider's catalog into a normalized local database on a schedule/manual trigger ("Update databases" in Options), and have the UI read only from that local database. This is effectively a **mini search-engine index** for model metadata, refreshed periodically.

> **v1 note:** Plan 17 ships provider-direct queries with TTL cache (P5 — wire as you go). The SQLite catalog below is the durable target; provider-direct is the MVP.

---

## 3. Data model (normalized across providers)

> **Deferred to post-Plan-19.** v1 uses `DatabaseProvider.list_models() -> list[ModelEntry]` (Plan 17 §S1.7) with no SQL persistence. The schema below is the target for when sync-based durability lands.

Use one schema so the UI doesn't need provider-specific rendering logic. Recommend SQLite (file-based, zero-ops, trivially backed-up/inspected, fine for tens of thousands of rows) unless SovereignAI already has a Postgres instance — in which case just add tables there instead of standing up a second datastore.

### Tables

**`providers`**
| column | type | notes |
|---|---|---|
| id | TEXT PK | `ollama`, `llamacpp`, `huggingface`, `vllm`, `lmstudio` |
| display_name | TEXT | "Ollama" |
| integrated | BOOLEAN | whether this provider is actually wired to run models, vs catalog-only |
| catalog_source_url | TEXT | where ingestion pulls from |
| last_synced_at | TIMESTAMP | nullable |
| sync_status | TEXT | `idle`/`syncing`/`error` |
| sync_error | TEXT | nullable, last error message |

**`families`** (the "publisher" grouping: Meta, Google, DeepSeek, Mistral, Alibaba/Qwen, Z.ai/GLM, etc.)
| column | type | notes |
|---|---|---|
| id | TEXT PK | slug, e.g. `meta-llama` |
| provider_id | TEXT FK → providers.id | a family is scoped to a provider's catalog (Ollama's "llama" family ≠ HF's, even if same upstream model, because availability/tags differ) |
| display_name | TEXT | "Meta / Llama" |
| logo_url | TEXT | nullable, optional icon |

**`models`** (e.g. "Llama 3.3", "Qwen 3.6", "Gemma 4")
| column | type | notes |
|---|---|---|
| id | TEXT PK | slug, e.g. `ollama:llama3.3` |
| provider_id | TEXT FK | |
| family_id | TEXT FK | |
| name | TEXT | "Llama 3.3" |
| description | TEXT | short blurb shown on hover/expand |
| capabilities | TEXT (JSON array) | `["tools","vision","thinking"]` etc |
| pulls_or_popularity | INTEGER | nullable, for sort-by-popularity |
| upstream_url | TEXT | link to provider page for this model |

**`model_versions`** (the leaf — what the user actually downloads/runs)
| column | type | notes |
|---|---|---|
| id | TEXT PK | e.g. `ollama:llama3.3:70b-instruct-q4_K_M` |
| model_id | TEXT FK | |
| tag | TEXT | `70b-instruct-q4_K_M` |
| parameter_count | TEXT | `70B` |
| quantization | TEXT | nullable, `Q4_K_M` |
| size_bytes | INTEGER | on-disk download size |
| context_length | INTEGER | nullable |
| vram_estimate_gb | REAL | nullable — see §4 on how this is derived |
| ram_estimate_gb | REAL | nullable, CPU-only fallback estimate |
| identifier | TEXT | the exact string used to pull/run it (e.g. Ollama pull name, HF repo+file) |
| is_default_tag | BOOLEAN | whether this is the tag returned by a bare pull with no tag suffix |
| raw_metadata | TEXT (JSON) | anything else scraped, kept for forward-compat without schema migration |

Index `model_versions(model_id)`, `models(family_id)`, `families(provider_id)` for fast tree expansion.

This schema lets the UI do exactly 4 cheap queries to render the whole drill-down:
1. `SELECT * FROM providers` → tabs
2. `SELECT * FROM families WHERE provider_id=?` → second level
3. `SELECT * FROM models WHERE family_id=?` → third level
4. `SELECT * FROM model_versions WHERE model_id=?` → leaf detail list

> **v1 mapping:** `ModelEntry` dataclass (Plan 17 §S1.7) is the in-memory equivalent of one `model_versions` row joined with its parent `models` and `families`. The 4-table normalization is deferred.

---

## 4. Ingestion (the "sync" job, triggered from Options)

> **Deferred to post-Plan-19.** v1 uses `DatabaseProvider.list_models()` calling the upstream API directly with a 1-hour in-memory TTL cache (Plan 17 §S2.3).

One ingestion module per provider, each implementing a common interface:

```
sync_provider(provider_id) -> SyncResult { families, models, versions, errors }
```

### Ollama ingestion
- Ollama doesn't expose a clean public JSON API for the library, but the **library page list + each model's tag page** can be parsed. Practical approach:
  1. Fetch `https://ollama.com/library` (paginated/scrolled or via their internal search endpoint if one is discoverable through dev-tools network inspection) to get the model name list + short description + capability badges.
  2. For each model, fetch `https://ollama.com/library/<model>/tags` to get the tag list with sizes (Ollama shows size per tag, e.g. "70b — 40GB").
  3. Derive `family` from the model name prefix/publisher metadata Ollama shows on the model page (e.g. "by Meta", "by Google").
  4. VRAM is **not given directly** by Ollama — estimate it (see formula below) from parameter count + quantization, rather than trying to scrape a number that doesn't exist.
- Treat this as **HTML scraping with a documented, versioned parser**, not an API integration — flag clearly in code comments (per AR17: clear naming, no docstrings) that this can break if Ollama changes their site, and have the sync job fail soft (keep last-good cache, log error, surface `sync_status=error` in UI) rather than wiping the table on failure.
- Respect robots.txt / reasonable rate limiting (e.g. 1 request per 200–500ms, with caching headers honored) since this is hitting their live site.

### HuggingFace ingestion
- Unlike Ollama, HuggingFace **does** have a real API: `https://huggingface.co/api/models?search=...&filter=gguf` etc. Use that instead of scraping HTML — it returns JSON with siblings (files), tags, downloads, library, pipeline_tag.
- "Family" here = the model's `author`/org on the Hub (e.g. `meta-llama`, `Qwen`, `google`).
- "Version" = each quantized GGUF file in the repo's file list (size is directly available from the API — no estimation needed here, which is a nice contrast to Ollama).

> **v1:** Plan 17 §S2.3 implements `HFDatabaseProvider.list_models()` against this API directly. Quant selection at download time uses `select_best_quant()` from `sovereignai/shared/quant_priority.py` (Plan 17 §S1.8).

### llama.cpp
- llama.cpp itself has no catalog — it's a runtime, not a model source. Two sane options:
  - (a) Don't give llama.cpp its own catalog at all; instead, treat "llama.cpp" as a *runtime target* and let the HuggingFace catalog's GGUF entries be runnable via either Ollama or llama.cpp depending on which runtime is selected elsewhere in the app.
  - (b) If a dedicated tab is wanted anyway, populate it from the same HuggingFace GGUF ingestion, just filtered/labeled as "llama.cpp compatible."
- Recommend (a) — avoids a duplicate, confusing data source for the same files.

> **v1:** Plan 19 ships llama.cpp as an adapter, not a catalog provider. HF is the only database in v1; Ollama service (Plan 17 §S3) is a service, not a database.

### Other providers (vLLM, LM Studio, etc.)
- Same pattern: either a real API (preferred) or a documented scraper, normalized into the same 4 tables. Each provider module should declare in its config whether it's "catalog-only" (browsable but not yet runnable from SovereignAI) vs "integrated" (can actually pull/run) — this maps to the `providers.integrated` flag, and the UI should visually distinguish catalog-only tabs (e.g. a small "browse only" badge) so it's clear why a Download button might be disabled there.

> **v1 alignment:** "integrated" maps to `DatabaseProvider.health_check().installed` (Plan 17 §S1.2 `DatabaseStatus`).

### VRAM/RAM estimation formula (for providers that don't report it directly)
Standard rule of thumb used across the local-LLM community:

```
vram_gb ≈ (parameter_count_billions × bytes_per_param) × 1.2   [1.2x overhead for KV cache/runtime]
```

Where `bytes_per_param` by quant level: FP16 ≈ 2, Q8 ≈ 1, Q4_K_M ≈ 0.5–0.6, Q3 ≈ 0.4. This is an *estimate* — label it as such in the UI ("~14GB VRAM (estimated)") rather than presenting it as a guaranteed number.

> **v1 note:** Plan 18 §S3.2 VRAM badge logic uses `max(gpus[].vram_total_mb) * 0.9` for the VRAM-fit check and `ram_available_gb * 1024 * 0.9` for the CPU-offload check (0.9 is an OS-reservation heuristic). The formula here is the upstream catalog estimate; Plan 18's is the runtime fit check. Both are estimates.

---

## 5. Sync triggers & scheduling

> **Deferred to post-Plan-19.** v1 uses 1-hour TTL in-memory cache per `DatabaseProvider` (Plan 17 §S2.3).

- **Manual:** "Update Databases" button in **Options**, per-provider or "Update All." Shows progress (families found / models found / versions found) and a final summary + timestamp.
- **Automatic (optional, off by default):** a background job (e.g. daily) that re-syncs providers whose `last_synced_at` is older than N days, only if the user has opted in — this avoids unexpected network calls on a tool meant for sovereign/local-first use (P4).
- **Incremental vs full refresh:** simplest correct approach is full refresh per provider (delete-and-replace that provider's rows in a transaction) rather than diffing — catalogs are small enough (hundreds to low-thousands of rows) that this is fast and avoids stale-row bugs. Wrap in a transaction so a failed sync never leaves a half-updated table (OR50 — atomic writes).

---

## 6. UI behavior

- **Tab row** = `providers` table, in the existing red-boxed tab bar. Tabs for providers with `integrated=false` still show (so users know they exist) but are visually marked "browse only" and any "Run/Pull" action is disabled with a tooltip explaining why.
- **Tab click** → right panel splits into 3 collapsible columns or a breadcrumb drill-down (Family → Model → Version), whichever matches the rest of SovereignAI's existing navigation idiom (the Tasks/Skills panels presumably already have a pattern — match that rather than inventing a new one).
- **Version detail row** shows: tag, params, quant, size, VRAM (flagged "est." if estimated), context length, capability badges, and a copy-able identifier string.
- **Empty/never-synced state:** if a provider's tables are empty, show "No catalog data yet — go to Options → Update Databases" rather than a blank panel.
- **Stale indicator:** show `last_synced_at` (e.g. "Synced 3 days ago") somewhere in the panel header so it's clear this is cached data, not live.

> **v1 UI (Plan 18 §S3):** Models panel renders a flat sortable table (Org, Family, Version, Quant, Size, VRAM, Tok/s [estimated], Source) with filter bar. Drill-down tree UI deferred with the sync jobs. Empty-DB state preserved. Tok/s estimated column is new (not in original spec).

---

## 7. Suggested file/module layout

```
/databases                       # OR67 — root-level package (Plan 17 §S1.1)
  /hf_database                   # Plan 17 §S2 — v1 provider
    provider.py
  base.py                        # Plan 17 §S1.2 — DatabaseProvider protocol
  # Future (post-Plan-19):
  /ollama_database               # sync-based catalog (this spec)
    sync.py
  catalog_schema.sql             # the 4 tables (this spec §3)

/services                        # OR67 — root-level package (Plan 17 §S1.3)
  /ollama_service                # Plan 17 §S3 — v1 service provider
    provider.py
  base.py                        # Plan 17 §S1.4 — ServiceProvider protocol

/sovereignai/shared
  database_registry.py           # Plan 17 §S1.5
  service_registry.py            # Plan 17 §S1.6
  model_catalog.py               # Plan 18 §S1.1 — aggregates DatabaseProviders
  tok_sampler.py                 # Plan 18 §S1.2 — tok/s estimate
  quant_priority.py              # Plan 17 §S1.8 — single source of quant order
  model_path_resolver.py         # Plan 19 §S2.1

/web
  /main.py                       # GET /api/models, /api/hardware, /api/hardware/stream (Plan 18 §S4)
  /schemas.py                    # ModelEntryDTO, HardwareSnapshotDTO (Plan 18 §S4)
  /static/{app.js,styles.css}    # Models panel + Hardware panel UI (Plan 18 §S4)
```

REST endpoints are read-only/cheap (straight SQL reads once sync lands; in v1 they call `ModelCatalog.list_models()` which delegates to registered `DatabaseProvider`s) except `POST /catalog/sync`, which kicks off the ingestion job (run it async/background, return a job id, let the frontend poll or receive an SSE event — SovereignAI already has SSE infra per its architecture, reuse it here for sync progress).

> **v1 endpoints (Plan 18 §S4):** `GET /api/models` (with filters), `GET /api/hardware`, `GET /api/hardware/stream` SSE. No `POST /catalog/sync` in v1.

---

## 8. Implementation order (suggested)

> **v1 (Plans 16-19) ships steps 1-4 equivalent via `DatabaseProvider` protocol. Steps 5-7 below are post-Plan-19.**

1. ~~Schema + migrations (the 4 tables).~~ → Deferred. v1: `DatabaseProvider` protocol + `ModelEntry` dataclass (Plan 17).
2. ~~Ollama sync module + manual "Update" button.~~ → Deferred. v1: `OllamaServiceProvider` (runtime only, no catalog) (Plan 17 §S3).
3. ~~UI drill-down (Provider → Family → Model → Version) wired to the read endpoints.~~ → Deferred. v1: flat sortable table with filters (Plan 18 §S3).
4. ~~HuggingFace sync module.~~ → v1: `HFDatabaseProvider.list_models()` with 1hr cache (Plan 17 §S2).
5. ~~Mark llama.cpp as an alias/view over the HuggingFace GGUF data.~~ → v1: llama.cpp as adapter (Plan 19), no catalog.
6. **Post-Plan-19:** SQLite catalog schema + sync jobs (this spec §3-§5).
7. **Post-Plan-19:** UI drill-down tree (this spec §6).
8. **Post-Plan-19:** Remaining provider stubs as catalog-only, `integrated=false`.
9. **Post-Plan-19:** Background auto-sync as opt-in setting.

---

## 9. Open questions to confirm with Angus before/while building

- Confirm whether SQLite is acceptable or whether SovereignAI already standardizes on a different DB (Postgres?) for everything else, to avoid a second persistence technology.
- Confirm whether "Download/Pull" actions should live inside this same panel (i.e. clicking a version triggers an actual `ollama pull`) or whether catalog browsing is purely informational and pulling happens elsewhere in the existing Ollama integration.
- Decide the actual UI pattern for the 3-level drill-down (breadcrumb vs split columns vs accordion) to match the rest of the app rather than inventing a new pattern.

> **Post-Plan-19 additional question:** Does the v1 `DatabaseProvider` protocol need extension to support sync-status reporting (`syncing`/`error`/`last_synced_at`) when the SQLite catalog lands, or does that stay an Options-panel-only concern?
