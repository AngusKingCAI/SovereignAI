# Ollama Library Scraper — Architecture Proposal

**Purpose:** Systematically crawl every model page on `ollama.com/library`, visit each model's `/tags` sub-page, and persist structured metadata (Model Name, Version/Tag, Size, Context Size, Input Type) to a database.

**Audience:** Architect / engineering lead, for review before implementation.

---

## 1. Prior Art (researched before writing this doc)

This is not a novel problem — several open-source projects already solve it, which validates the approach and de-risks the design:

| Project | Approach | Notes |
|---|---|---|
| [`chrizzo84/OllamaScraper`](https://github.com/chrizzo84/OllamaScraper) | Async Python scraper, catalogs all library models, runs daily via GitHub Actions, outputs JSON | Closest match to our use case; proves async HTML scraping is sufficient (no headless browser needed) |
| [`webfarmer/ollama-get-models`](https://github.com/webfarmer/ollama-get-models) | Python + BeautifulSoup, caches raw HTML locally before parsing | Good pattern for polite re-scraping / debugging |
| [`ManiAm/ollama-remote-models`](https://github.com/ManiAm/ollama-remote-models) | Python, scrapes model search page, outputs JSON/Markdown/HTML, supports sort/filter | Confirms the site is scrapable with plain requests, not JS-rendering |

**Key finding:** Ollama's `/api/tags` REST endpoint (documented at docs.ollama.com) is a **local endpoint served by a running Ollama instance on `localhost:11434`** — it is not a public API for browsing the ollama.com model catalog. There is no public JSON API for `ollama.com/library`. **HTML scraping is the only viable route**, which all three prior projects confirm independently.

---

## 2. Target Page Structure

### 2.1 Index page — `ollama.com/library`
Lists all models with name, short description, and tag badges (e.g. `vision`, `tools`, `thinking`) plus a few size shortcuts (e.g. `8b`, `70b`). This page is the seed list — we need every model's slug (e.g. `llama3.1`, `deepseek-r1`, `qwen3`) to build the `/tags` URLs.

### 2.2 Detail page — `ollama.com/library/{model}/tags`
Confirmed structure (from `llama3.1/tags`) — each row contains:

```
{model}:{tag}  ·  {digest_short}  •  {size}  •  {context_window}  •  {input_type}  •  {relative_last_updated}
```

Example row:
```
llama3.1:8b-instruct-q3_K_M · 4faa21fca5a2 • 4.0GB • 128K context window • Text input • 1 year ago
```

Fields map cleanly to requirements:
- **Model Name** → the part before `:` (e.g. `llama3.1`)
- **Version/Tag** → the part after `:` (e.g. `8b-instruct-q3_K_M`, or `latest`)
- **Size** → e.g. `4.0GB`, `243GB` (needs normalization — see §5)
- **Context Size** → e.g. `128K` (strip "context window")
- **Input Type** → e.g. `Text`, `Vision`, `Text, Vision` for multimodal models
- **Bonus fields worth capturing while we're there:** digest hash, last-updated timestamp (relative — will need parsing or leave as raw string)

This is static, server-rendered HTML (confirmed by the search-engine cache rendering full text content) — **no JavaScript execution / headless browser required**. A simple HTTP client + HTML parser is sufficient, matching what all three prior-art projects do.

---

## 3. Proposed Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌───────────────────┐
│  1. Seed Crawler │ --> │  2. Tags Scraper  │ --> │  3. Parser/Mapper │
│  (library index) │     │  (per-model page) │     │  (HTML -> struct) │
└─────────────────┘     └──────────────────┘     └───────────────────┘
                                                              │
                                                              v
                                                   ┌───────────────────┐
                                                   │  4. Upsert Layer   │
                                                   │  (DB writer)       │
                                                   └───────────────────┘
                                                              │
                                                              v
                                                   ┌───────────────────┐
                                                   │  5. Scheduler /    │
                                                   │  Orchestrator      │
                                                   └───────────────────┘
```

### Stage 1 — Seed Crawler
- Fetch `ollama.com/library`.
- Handle pagination if present (verify at build time — the index may lazy-load or paginate for the full catalog, which numbers in the hundreds).
- Extract the list of model slugs → build target URLs of the form `ollama.com/library/{slug}/tags`.
- Output: a flat list of URLs (can be written to a queue table or file for resumability).

### Stage 2 — Tags Scraper (per model)
- For each seed URL, issue an HTTP GET.
- **Concurrency:** use an async HTTP client (e.g. Python `httpx`/`aiohttp`, or Node `undici`) with a bounded concurrency pool (e.g. 5–10 concurrent requests) — mirrors the async approach in `OllamaScraper`.
- **Politeness:** respect `robots.txt`, add a realistic `User-Agent`, insert small randomized delays between requests, and implement exponential backoff on 429/5xx.
- **Caching layer:** save raw HTML to disk/object storage keyed by model+timestamp before parsing (pattern borrowed from `ollama-get-models`) — this decouples scraping from parsing, so a parser bug doesn't require re-hitting the site, and gives you an audit trail.

### Stage 3 — Parser / Mapper
- Parse cached HTML with a standard parser (BeautifulSoup/lxml in Python, or Cheerio in Node).
- Select the tag-row elements and extract the five fields per row via CSS selectors (selectors need to be captured directly from the live DOM at build time, since search-cache text doesn't preserve exact class names/attributes).
- Normalize into a clean intermediate schema (see §4) before hitting the database — keep raw scrape and normalized record separate so re-normalization doesn't require re-scraping.
- **Validation:** reject/flag rows where expected fields are missing (defensive — site markup will drift over time).

### Stage 4 — Upsert Layer
- Idempotent writes keyed on `(model_name, tag)` — re-running the scraper should update existing rows, not duplicate them.
- Batch inserts/upserts rather than row-by-row for throughput.
- Record a `scraped_at` timestamp and `source_url` per row for lineage.

### Stage 5 — Scheduler / Orchestrator
- Since the catalog changes over time (new models, new quantizations, updated timestamps), this needs to run on a schedule, not just once.
- Options, roughly in order of operational simplicity:
  - **Cron job / GitHub Actions scheduled workflow** (what `OllamaScraper` itself uses) — simplest, good for daily/weekly refresh.
  - **Airflow / Dagster / Prefect DAG** — better if this becomes one part of a larger data pipeline, gives you retries, backfills, and observability for free.
  - **Simple systemd timer or serverless cron (e.g. AWS EventBridge → Lambda/Fargate task)** — if you want to avoid running your own orchestrator.
- Recommendation: start with scheduled GitHub Actions or cron (matches proven prior art, low operational overhead), and only move to a full orchestrator if this scraper becomes one node in a bigger data platform.

---

## 4. Data Model

```sql
CREATE TABLE ollama_models (
    id                BIGSERIAL PRIMARY KEY,
    model_name         TEXT NOT NULL,          -- e.g. 'llama3.1'
    tag                TEXT NOT NULL,          -- e.g. '8b-instruct-q3_K_M'
    full_reference     TEXT NOT NULL,          -- 'llama3.1:8b-instruct-q3_K_M' (convenience/unique key)
    digest             TEXT,                    -- short hash, e.g. '4faa21fca5a2'
    size_raw           TEXT,                    -- '4.0GB' as scraped
    size_bytes         BIGINT,                  -- normalized, for sorting/filtering
    context_size_raw   TEXT,                    -- '128K' as scraped
    context_size_tokens INTEGER,                 -- normalized, e.g. 131072
    input_types        TEXT[],                  -- ['text'], ['text','vision'], etc.
    last_updated_raw   TEXT,                    -- '1 year ago' as scraped
    source_url         TEXT NOT NULL,
    scraped_at          TIMESTAMPTZ NOT NULL,
    UNIQUE (model_name, tag)
);
```

- **Both raw and normalized columns** are recommended for `size` and `context_size` — the site's display format (`4.9GB`, `128K`) is lossy/rounded and inconsistent across models, so keeping the raw string preserves what was actually shown, while the normalized numeric column makes the data usable for queries/joins.
- `input_types` as an array handles multimodal models (some rows show `Text, Vision`).
- Database choice: any relational store works (Postgres recommended for array support and upsert ergonomics via `ON CONFLICT`). A NoSQL/document store is also viable if downstream consumers want flexible schema, but the data here is naturally tabular, so relational is the simpler default.

---

## 5. Key Implementation Risks & Design Decisions for the Architect

1. **No public API — scraping is inherently fragile.** Ollama can change class names, markup structure, or move to client-side rendering at any time. Mitigate with: cached raw HTML (for reprocessing without re-scraping), a small test suite of "golden" HTML fixtures + expected parse output, and alerting when parse success rate drops (e.g. <95% of rows parsed cleanly triggers a warning).
2. **Size/context normalization is lossy.** `4.9GB` and `128K` are display-rounded. Decide up front whether the business need requires byte-exact sizes (in which case you may want to also pull the model's `manifest`/blob digest info from the Ollama registry API, which is a *separate*, documented, public registry API distinct from the local `/api/tags` — worth a follow-up spike if precision matters) or whether the rounded display values are sufficient.
3. **Rate limiting / being a good citizen.** With ~150+ models and up to ~100 tags each, a full crawl could be 5,000+ requests. Bounded concurrency + delays + caching avoids hammering the site and reduces risk of IP blocking.
4. **Pagination/completeness of the index page.** Needs verification at implementation time — confirm whether `ollama.com/library` requires scrolling/pagination requests to reveal the full model list, or whether it's fully present in the initial HTML.
5. **Idempotency & incremental runs.** Since this will run repeatedly, upsert-by-unique-key (not insert-only) is essential, and a `scraped_at` column lets consumers ask "what changed since last run."

---

## 6. Suggested Tech Stack

| Layer | Recommendation | Rationale |
|---|---|---|
| HTTP client | Python `httpx` (async) or Node `undici`/`got` | Matches proven prior art; no headless browser needed since content is server-rendered |
| HTML parsing | BeautifulSoup + lxml (Python) or Cheerio (Node) | Standard, well-supported |
| Database | PostgreSQL | Native array types, robust upsert (`ON CONFLICT`) |
| Scheduling | Scheduled GitHub Actions workflow or cron | Matches `OllamaScraper` prior art; low ops overhead to start |
| Raw HTML cache | Local disk or S3-compatible object storage | Decouples scrape from parse; enables replay/debugging |

---

## 7. Open Questions for the Architect

- Do we need historical versioning (track how a model's tags change over time) or just current-state snapshots?
- Is exact byte-level size precision required, or is the site's rounded display sufficient?
- Expected refresh cadence — daily, weekly, on-demand?
- Should this integrate into an existing data pipeline/orchestrator, or run standalone?
