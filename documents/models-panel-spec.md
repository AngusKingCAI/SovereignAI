# SovereignAI — Models Panel: Provider Catalog Implementation Spec

**Audience:** GLM (implementing agent)
**Author:** Angus / Claude (design pass)
**Status:** Draft for implementation

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

---

## 2. Why a local database, not live scraping per click

- `ollama.com/library` (and HuggingFace, etc.) is **not a stable JSON API** — it's an HTML page meant for browsers, and there's no first-party endpoint that returns the full catalog with tags/sizes/VRAM in one shot. Scraping it live on every UI click would be slow, fragile, and would break the moment the page markup changes.
- Each provider has a *different* shape of "catalog": Ollama has model→tags, HuggingFace has repos→files→quant variants, llama.cpp doesn't really have its own catalog at all (it just runs GGUF files, usually sourced from HuggingFace).
- We want offline/airgapped capability (SovereignAI implies local-first / sovereign infra) — that means the catalog must be cached locally and refreshed on demand, not fetched live.

**Conclusion:** ingest each provider's catalog into a normalized local database on a schedule/manual trigger ("Update databases" in Options), and have the UI read only from that local database. This is effectively a **mini search-engine index** for model metadata, refreshed periodically.

---

## 3. Data model (normalized across providers)

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

---

## 4. Ingestion (the "sync" job, triggered from Options)

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
- Treat this as **HTML scraping with a documented, versioned parser**, not an API integration — flag clearly in code comments that this can break if Ollama changes their site, and have the sync job fail soft (keep last-good cache, log error, surface `sync_status=error` in UI) rather than wiping the table on failure.
- Respect robots.txt / reasonable rate limiting (e.g. 1 request per 200–500ms, with caching headers honored) since this is hitting their live site.

### HuggingFace ingestion
- Unlike Ollama, HuggingFace **does** have a real API: `https://huggingface.co/api/models?search=...&filter=gguf` etc. Use that instead of scraping HTML — it returns JSON with siblings (files), tags, downloads, library, pipeline_tag.
- "Family" here = the model's `author`/org on the Hub (e.g. `meta-llama`, `Qwen`, `google`).
- "Version" = each quantized GGUF file in the repo's file list (size is directly available from the API — no estimation needed here, which is a nice contrast to Ollama).

### llama.cpp
- llama.cpp itself has no catalog — it's a runtime, not a model source. Two sane options:
  - (a) Don't give llama.cpp its own catalog at all; instead, treat "llama.cpp" as a *runtime target* and let the HuggingFace catalog's GGUF entries be runnable via either Ollama or llama.cpp depending on which runtime is selected elsewhere in the app.
  - (b) If a dedicated tab is wanted anyway, populate it from the same HuggingFace GGUF ingestion, just filtered/labeled as "llama.cpp compatible."
- Recommend (a) — avoids a duplicate, confusing data source for the same files.

### Other providers (vLLM, LM Studio, etc.)
- Same pattern: either a real API (preferred) or a documented scraper, normalized into the same 4 tables. Each provider module should declare in its config whether it's "catalog-only" (browsable but not yet runnable from SovereignAI) vs "integrated" (can actually pull/run) — this maps to the `providers.integrated` flag, and the UI should visually distinguish catalog-only tabs (e.g. a small "browse only" badge) so it's clear why a Download button might be disabled there.

### VRAM/RAM estimation formula (for providers that don't report it directly)
Standard rule of thumb used across the local-LLM community:

```
vram_gb ≈ (parameter_count_billions × bytes_per_param) × 1.2   [1.2x overhead for KV cache/runtime]
```

Where `bytes_per_param` by quant level: FP16 ≈ 2, Q8 ≈ 1, Q4_K_M ≈ 0.5–0.6, Q3 ≈ 0.4. This is an *estimate* — label it as such in the UI ("~14GB VRAM (estimated)") rather than presenting it as a guaranteed number.

---

## 5. Sync triggers & scheduling

- **Manual:** "Update Databases" button in **Options**, per-provider or "Update All." Shows progress (families found / models found / versions found) and a final summary + timestamp.
- **Automatic (optional, off by default):** a background job (e.g. daily) that re-syncs providers whose `last_synced_at` is older than N days, only if the user has opted in — this avoids unexpected network calls on a tool meant for sovereign/local-first use.
- **Incremental vs full refresh:** simplest correct approach is full refresh per provider (delete-and-replace that provider's rows in a transaction) rather than diffing — catalogs are small enough (hundreds to low-thousands of rows) that this is fast and avoids stale-row bugs. Wrap in a transaction so a failed sync never leaves a half-updated table.

---

## 6. UI behavior

- **Tab row** = `providers` table, in the existing red-boxed tab bar. Tabs for providers with `integrated=false` still show (so users know they exist) but are visually marked "browse only" and any "Run/Pull" action is disabled with a tooltip explaining why.
- **Tab click** → right panel splits into 3 collapsible columns or a breadcrumb drill-down (Family → Model → Version), whichever matches the rest of SovereignAI's existing navigation idiom (the Tasks/Skills panels presumably already have a pattern — match that rather than inventing a new one).
- **Version detail row** shows: tag, params, quant, size, VRAM (flagged "est." if estimated), context length, capability badges, and a copy-able identifier string.
- **Empty/never-synced state:** if a provider's tables are empty, show "No catalog data yet — go to Options → Update Databases" rather than a blank panel.
- **Stale indicator:** show `last_synced_at` (e.g. "Synced 3 days ago") somewhere in the panel header so it's clear this is cached data, not live.

---

## 7. Suggested file/module layout

```
/backend
  /catalog
    schema.sql                 # the 4 tables above
    base.py                    # SyncResult, BaseProviderSync interface
    providers/
      ollama_sync.py
      huggingface_sync.py
      llamacpp_sync.py        # thin wrapper, likely delegates to huggingface_sync
    vram_estimate.py           # the formula in §4, isolated + unit-testable
    api.py                     # REST endpoints: GET /catalog/providers, /catalog/families?provider=, /catalog/models?family=, /catalog/versions?model=, POST /catalog/sync
/frontend
  /components/models-panel/
    ProviderTabs.tsx
    FamilyList.tsx
    ModelList.tsx
    VersionList.tsx
    SyncStatusBadge.tsx
  /options/
    UpdateDatabasesSection.tsx
```

REST endpoints are read-only/cheap (straight SQL reads) except `POST /catalog/sync`, which kicks off the ingestion job (run it async/background, return a job id, let the frontend poll or receive an SSE/WebSocket progress event — SovereignAI already has SSE infra per its architecture, reuse it here for sync progress).

---

## 8. Implementation order (suggested)

1. Schema + migrations (the 4 tables).
2. Ollama sync module + manual "Update" button — this is the provider that's already partially integrated, so it validates the whole pipeline first.
3. UI drill-down (Provider → Family → Model → Version) wired to the read endpoints, using Ollama's data to verify the tree renders correctly.
4. HuggingFace sync module (easier than Ollama since it has a real API) — validates the schema generalizes to a second provider.
5. Mark llama.cpp as an alias/view over the HuggingFace GGUF data rather than its own scraper (§4).
6. Add remaining provider stubs as catalog-only, `integrated=false`.
7. Add background auto-sync as an opt-in setting once manual sync is proven stable.

---

## 9. Open questions to confirm with Angus before/while building

- Confirm whether SQLite is acceptable or whether SovereignAI already standardizes on a different DB (Postgres?) for everything else, to avoid a second persistence technology.
- Confirm whether "Download/Pull" actions should live inside this same panel (i.e. clicking a version triggers an actual `ollama pull`) or whether catalog browsing is purely informational and pulling happens elsewhere in the existing Ollama integration.
- Decide the actual UI pattern for the 3-level drill-down (breadcrumb vs split columns vs accordion) to match the rest of the app rather than inventing a new pattern.
