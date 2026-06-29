# SovereignAI — Research Department: Implementation Specification

**Document Type:** Deep Implementation Spec
**Author:** Angus / Claude (design pass)
**Audience:** GLM (implementing agent) + Round Table review
**Status:** Draft v1 — ready for Round Table review
**Date:** 2026-06-29
**Depends on:** `SovereignAI_Architecture_Decisions.md`, `project-vision-Rev5.md`, `SovereignAI_Education_Department_Spec.md`

---

## 0. Purpose

This document specifies the **Research Department** — SovereignAI's internal capability for conducting deep, multi-source, structured research across any domain. The department is not training-specific. It serves every other department in the system: the Education Department receives dataset briefs and base model recommendations; the Engineering Department receives technical landscape reports; the Communication Department receives audience research and competitor analysis; the Owner receives direct research outputs for personal or professional use.

The Research Department is the system's epistemic infrastructure. Wherever the system or the user needs to know something that isn't already in memory, the Research Department finds, evaluates, synthesizes, and delivers it.

---

## 1. Company Metaphor Placement

Following the SovereignAI company structure:

| Entity | Role in Research Department |
|--------|----------------------------|
| **Owner (User)** | Issues research requests, defines scope and depth, accepts or rejects deliverables |
| **Orchestrator (CEO)** | Translates vague research requests ("find out about X") into structured Research Briefs with measurable scope and output format |
| **Research Manager** | Permanent department head. Receives Research Briefs, decomposes them into worker assignments, synthesizes findings into final deliverables. Maintains the Research Registry |
| **Source Discovery Workers** | Identify candidate sources — web, academic, internal, API-based — relevant to the research question |
| **Deep Retrieval Workers** | Fetch full content from identified sources (web pages, PDFs, database records, API responses). Handle pagination, authentication, and format normalization |
| **Evaluation Workers** | Score and filter retrieved content for relevance, recency, authority, and credibility. Flag conflicting claims |
| **Synthesis Workers** | Combine evaluated findings into coherent structured outputs: reports, briefs, summaries, datasets, comparison tables |
| **Fact-Check Workers** | Cross-reference claims across sources, flag unverifiable assertions, escalate conflicts for Manager review |
| **Librarian** | Routes queries to the correct memory backend (Qdrant for semantic recall of past research, Postgres for structured records, Obsidian for user notes) before the department hits the web |
| **Security Guard** | Audits source URLs and content for malicious payloads, enforces source blocklists, validates provenance of retrieved documents |

The Research Department is a **permanent department** (not task-spawned). It maintains its own state: a Research Registry of all briefs, in-progress jobs, completed deliverables, and source caches. It surfaces in the Workers panel under a dedicated "Research" section.

---

## 2. What the Department Produces

Each output is called a **Research Deliverable**. The deliverable type is declared in the Research Brief and determines how Synthesis Workers structure the output. The following types are supported:

| Deliverable Type | Description | Typical Requester |
|-----------------|-------------|------------------|
| **Domain Brief** | Structured handoff for another department — schema-compliant TOML/JSON summarising key findings, ranked recommendations, and open questions | Education Department, Engineering Department |
| **Research Report** | Long-form narrative document covering a topic in depth, with sourced claims, conflict flags, and a conclusions section | Owner (personal/professional use) |
| **Comparison Table** | Side-by-side structured comparison of options, tools, datasets, models, vendors, etc. | Owner, any department |
| **Source Inventory** | A curated list of sources relevant to a domain, annotated with relevance scores, recency, authority ratings, and license notes | Education Department (dataset discovery), Engineering (tool evaluation) |
| **Fact Sheet** | Short, dense summary of key facts about a specific entity, concept, or event | Owner, CEO for context injection |
| **Competitive Intelligence Report** | Analysis of competing products, projects, or organisations in a target space | Owner, Communication Department |
| **Gap Analysis** | Identifies what is missing from a given body of knowledge, dataset, or capability landscape | Education Department, Engineering Department |
| **Ongoing Monitor** | A recurring research job that watches a topic for new developments and delivers delta summaries on a schedule | Owner (set up via Tasks panel) |

All deliverables are stored in the Research Registry and can be retrieved by any department or the Owner without re-running the research. Deliverables carry a `freshness_score` that degrades over time — the Manager can flag stale deliverables and offer to re-run.

---

## 3. Research Sources

The Research Department operates across five source tiers. Each tier has different access methods, reliability characteristics, and appropriate use cases.

### 3.1 Tier 1 — Internal Memory (Always consulted first)

Before touching the web or any external source, the Research Manager queries the Librarian for relevant existing knowledge:

- **Qdrant (vector search):** semantic similarity search across past research, documents, and chat history
- **Postgres (structured records):** exact-match or filter queries for structured data (past deliverables, registered models, task history)
- **Obsidian (user documents):** full-text search over the user's personal notes and uploaded files

**Why first:** avoids redundant external fetches; respects local-first principle (P4); leverages research the system has already done. A Research Brief that can be answered entirely from internal memory costs no external calls.

The Librarian returns a **memory hit score** alongside results. If hit score is above threshold (configurable, default 0.85 semantic similarity), the Research Manager can issue the deliverable from memory without external retrieval — subject to a freshness check on the cached content's timestamp.

### 3.2 Tier 2 — Structured Public APIs

Machine-readable data sources with stable, well-documented endpoints. These are preferred over web scraping when they cover the needed domain.

| API | Domain | Notes |
|-----|--------|-------|
| HuggingFace Hub API | ML models, datasets, spaces | JSON; filter by task, license, size |
| arXiv API | Academic ML/CS papers | Atom/JSON; filter by category, date |
| Semantic Scholar API | Academic papers (all fields) | JSON; citation graph, abstracts, full text links |
| GitHub REST API | Code repositories, issues, releases | JSON; rate-limited, requires token |
| PyPI JSON API | Python package metadata | JSON; stable |
| npm Registry API | JavaScript package metadata | JSON; stable |
| PapersWithCode API | ML benchmarks, SOTA tables, datasets | JSON; maps papers to code |
| OpenAlex API | Academic literature (open, broad) | JSON; replacement for deprecated Microsoft Academic |
| CORE API | Open-access full-text academic papers | JSON; broader than arXiv |

Each API is wrapped as a **Source Adapter** (a typed plugin, following the same adapter contract as MCP adapters) that normalises the response into SovereignAI's internal `SourceRecord` schema (see §5). Adding a new API source means adding a new adapter file — no changes to the Research Manager or worker pipeline.

### 3.3 Tier 3 — Web Search

General-purpose web retrieval for topics not covered by Tier 2 APIs. The Research Department uses SovereignAI's existing web search adapter (configured in the Adapters panel) and supplements it with direct fetching.

**Search strategy:**

- **Query decomposition:** complex research questions are broken into multiple targeted sub-queries by the Research Manager, not submitted as a single broad search. A question like "best base models for code fine-tuning in 2025" becomes three sub-queries: "open-source code LLM comparison 2025", "QLoRA fine-tuning base model benchmarks", "coding benchmark HumanEval MBPP leaderboard".
- **Result ranking:** raw search results are ranked by Source Evaluation Workers (§4.2) before being passed to Deep Retrieval Workers for full-content fetching.
- **Depth control:** the Research Brief specifies a `search_depth` parameter (shallow / standard / deep). Shallow = top 5 results per sub-query, summaries only. Standard = top 10, full fetch of top 5. Deep = top 20, full fetch of all, recursive link-following up to 2 hops.

**Fetching pipeline:** search result → URL extracted → `web_fetch` adapter retrieves full page → Markdown conversion → passed to Evaluation Workers. The fetching step is skipped if the URL matches a Tier 2 API endpoint that can be called directly (e.g. a GitHub URL gets routed to the GitHub API, not raw HTML scraping).

### 3.4 Tier 4 — Document Stores and Uploaded Files

Files the user has manually provided: PDFs, Word documents, spreadsheets, CSV files. These enter the pipeline via the Librarian (stored in the memory backends) and are treated as high-authority sources for the duration of the research job in which they appear.

- **PDF retrieval:** full text extraction via the pdf-reading pipeline.
- **Chunking and embedding:** long documents are chunked (512-token default, with 64-token overlap) and embedded into Qdrant for semantic retrieval within the research job — not permanently unless the user consents.
- **Citation handling:** academic PDFs include citation metadata; these are extracted and used to populate the source chain (a Fact-Check Worker can verify a citation exists by querying Semantic Scholar or OpenAlex).

### 3.5 Tier 5 — Specialist External Databases (Optional, Adapter-Gated)

High-value databases requiring explicit configuration (API keys, institutional access, or rate agreements). These are not enabled by default and are listed as available adapters in the Adapters panel.

Examples: PubMed (biomedical), JSTOR (humanities), LexisNexis (legal), Bloomberg (financial), Crunchbase (startup intelligence), Patents (Google Patents API, USPTO), Standards bodies (ISO, IEEE Xplore).

Each specialist adapter declares its domain tags in its capability manifest. When the Research Manager builds a query plan, it checks the Adapters panel for any installed specialist adapters whose domain tags match the research topic, and routes relevant sub-queries to them.

---

## 4. The Research Pipeline

A Research Brief enters the department and flows through six stages. The Research Manager orchestrates the stages; workers are spawned per stage as needed (parallelism within a stage is the default).

```
Brief Intake
     ↓
Stage 1: Query Planning
     ↓
Stage 2: Source Discovery
     ↓
Stage 3: Deep Retrieval
     ↓
Stage 4: Evaluation & Filtering
     ↓
Stage 5: Fact-Checking
     ↓
Stage 6: Synthesis & Delivery
```

### Stage 1: Query Planning

**Actor:** Research Manager

The Manager receives the structured Research Brief (see §6 for schema) and produces a **Query Plan** — a DAG of sub-queries, their source tier assignments, their depth settings, and their dependency relationships (some sub-queries can only run after others return results that refine the scope).

Query planning also includes a **memory pre-check**: the Manager asks the Librarian whether any past Research Deliverable covers the same or a subset of the current brief. If a fresh enough match exists, the Manager can:

- Return it immediately (full cache hit)
- Use it as a starting point, running only the delta (partial cache hit — reduces external calls significantly)
- Ignore it and run fresh (if the brief specifies `force_fresh: true`)

The Query Plan is written to the Research Registry as a job record with `status: planning`.

### Stage 2: Source Discovery

**Actor:** Source Discovery Workers (spawned in parallel, one per source tier relevant to the query plan)

Workers search each relevant source tier for candidate sources matching each sub-query. They return a list of `CandidateSource` records (URL or API identifier, a short relevance justification, and an initial credibility flag).

The Research Manager reviews the candidate list and prunes:
- Duplicate sources (same content, different URL)
- Sources blocked by Security Guard rules
- Sources with credibility flags below threshold

The pruned list becomes the input to Stage 3.

### Stage 3: Deep Retrieval

**Actor:** Deep Retrieval Workers (spawned in parallel, one per source)

Each worker fetches the full content of its assigned source. Workers handle:

- **Web pages:** full HTML → Markdown conversion, removing navigation, ads, and boilerplate
- **PDFs:** text extraction, table detection, metadata extraction
- **API responses:** JSON normalisation into `SourceRecord` schema
- **Paginated content:** automatic pagination (e.g. multi-page arXiv result sets, GitHub repo file trees)
- **Rate limiting:** each worker respects the source's rate limits (declared in the Source Adapter config); a shared rate-limit token bucket per domain prevents the department from hammering a single host

Retrieved content is stored in a **research job cache** (ephemeral, scoped to the job — not persisted to long-term memory unless the Manager explicitly promotes it). Cache entries have a TTL of 24 hours by default, so a re-run of the same job within a day re-uses fetched content rather than re-fetching.

### Stage 4: Evaluation and Filtering

**Actor:** Evaluation Workers (spawned in parallel, one per retrieved source)

Each worker scores the retrieved content on four dimensions:

| Dimension | Description | Signal |
|-----------|-------------|--------|
| **Relevance** | How directly does this content answer the sub-query? | Semantic similarity to query embedding (0–1) |
| **Recency** | How fresh is this content? | Publication date vs. query's `recency_requirement` |
| **Authority** | Is the source credible for this domain? | Domain whitelist, citation count, peer-review status, known-author index |
| **Coverage** | What fraction of the sub-query's required aspects does this source address? | Aspect checklist defined in Query Plan |

Sources below a minimum composite score (configurable, default 0.5) are dropped. Sources above a conflict threshold in the same sub-query are flagged for Fact-Checking (Stage 5) before synthesis.

The output of Stage 4 is a **Ranked Source Set** per sub-query: an ordered list of sources with their scores, ready for synthesis.

### Stage 5: Fact-Checking

**Actor:** Fact-Check Workers (spawned only for flagged claims)

Fact-checking is not exhaustive — it targets specific claims that are either:
- **Contested:** two or more sources disagree on a specific factual assertion
- **High-stakes:** the Research Brief marks certain claim types as requiring verification (e.g. benchmark numbers, licensing terms, pricing, legal requirements)
- **Unverifiable:** a source makes a claim that no other source in the retrieved set corroborates

For each flagged claim, a Fact-Check Worker:
1. Identifies the specific assertion (extracted as a structured claim)
2. Searches for a primary or authoritative source (the original paper, the vendor's official documentation, a government record)
3. Returns one of: **Verified**, **Contested** (with both sides documented), **Unverifiable** (no corroborating source found), or **Contradicted** (primary source contradicts the claim)

The Manager includes the fact-check status in the final deliverable. Contested or Contradicted claims are flagged visually in the output and never presented as settled facts.

### Stage 6: Synthesis and Delivery

**Actor:** Synthesis Workers (one per deliverable type — different workers are optimised for different output formats)

Synthesis Workers take the Ranked Source Set plus Fact-Check results and produce the deliverable. The worker is selected based on the `deliverable_type` declared in the Research Brief:

- **Report Synthesis Worker:** long-form narrative, section-by-section, with inline source citations and a references list
- **Brief Synthesis Worker:** structured TOML/JSON output (for machine consumption by other departments), with ranked recommendations and confidence scores
- **Table Synthesis Worker:** structured comparison, normalised across sources
- **Monitor Synthesis Worker:** delta from previous deliverable, highlights only new findings

The deliverable is written to the Research Registry with `status: complete`, a `freshness_score` of 1.0 (decaying on a configurable schedule), and a full provenance chain (which sources were fetched, what scores they received, what claims were fact-checked).

The Manager notifies the requester (Owner, CEO, or requesting department) that the deliverable is ready, via the event bus.

---

## 5. Internal Data Schemas

### 5.1 Research Brief

The canonical input to the Research Department. All requesters (Owner via chat, CEO, other departments) produce a Research Brief before work can begin.

```toml
[brief]
id            = "brief-20260629-001"                  # UUID assigned by Research Manager
requested_by  = "education_manager"                   # entity requesting the research
created_at    = "2026-06-29T14:47:00Z"

[brief.scope]
title         = "Python Code Fine-Tuning: Dataset & Base Model Selection"
description   = """
Identify the best publicly available datasets for Python code instruction fine-tuning,
recommend a base model suited to QLoRA training on consumer hardware, and identify
appropriate evaluation benchmarks.
"""
domains       = ["machine_learning", "software_engineering", "datasets"]
recency_requirement = "last_12_months"      # oldest acceptable primary sources
force_fresh   = false                        # true = ignore cache

[brief.output]
deliverable_type = "domain_brief"            # report | domain_brief | comparison_table | source_inventory | fact_sheet | competitive_intelligence | gap_analysis | ongoing_monitor
output_schema    = "education_domain_brief_v1"  # named schema if deliverable_type is domain_brief
depth            = "standard"               # shallow | standard | deep

[brief.constraints]
max_sources      = 30
require_open_access = true                  # only sources freely accessible (no paywalls)
source_tier_priority = ["tier2_api", "tier3_web", "tier1_memory"]  # override default order
blocked_domains  = []                        # additional blocks beyond Security Guard defaults

[brief.claims_to_verify]
high_stakes = ["benchmark_scores", "model_licenses", "dataset_licenses"]
```

### 5.2 SourceRecord

The normalised internal representation of any retrieved source, regardless of origin tier.

```python
@dataclass
class SourceRecord:
    id: str                       # UUID assigned on creation
    brief_id: str                 # parent research brief
    url: str                      # canonical URL or API identifier
    title: str
    authors: list[str]            # empty list if not applicable
    publication_date: date | None
    retrieved_at: datetime
    source_tier: int              # 1–5
    content_markdown: str         # normalised full text
    content_hash: str             # SHA-256 of raw retrieved bytes
    relevance_score: float        # 0–1, assigned by Evaluation Worker
    authority_score: float        # 0–1
    recency_score: float          # 0–1
    coverage_score: float         # 0–1
    composite_score: float        # weighted average
    fact_check_status: str        # "pending" | "verified" | "contested" | "unverifiable" | "contradicted" | "not_checked"
    license: str | None           # SPDX identifier or free text if known
    raw_metadata: dict            # anything else, for forward-compat
```

### 5.3 Domain Brief (Education Department Handoff Schema)

When a Research Brief from the Education Department requests a `domain_brief`, the deliverable is a structured TOML file conforming to this schema:

```toml
[brief_meta]
generated_by     = "research_department"
brief_id         = "brief-20260629-001"
schema_version   = "education_domain_brief_v1"
generated_at     = "2026-06-29T15:30:00Z"
freshness_ttl_days = 30            # Research Manager will flag as stale after this

[domain]
name             = "Python Code Instruction Fine-Tuning"
description      = "Hyper-specialized model for Python code generation and instruction following"

[datasets]
# Ranked list. Education Manager takes top recommended datasets.

[[datasets.recommended]]
name         = "iamtarun/python_code_instructions_18k_alpaca"
source       = "HuggingFace Hub"
url          = "https://huggingface.co/datasets/iamtarun/python_code_instructions_18k_alpaca"
size_rows    = 18000
format       = "alpaca"
license      = "unknown"           # flag for Education Manager review
quality_notes = "Clean instruction-output pairs; moderate diversity"
rank         = 1
confidence   = 0.87

[[datasets.recommended]]
name         = "bigcode/the-stack"
source       = "HuggingFace Hub"
url          = "https://huggingface.co/datasets/bigcode/the-stack"
size_rows    = 3_000_000          # Python subset
format       = "raw_code"
license      = "various_permissive"
quality_notes = "Extremely large, high diversity, raw code not instructions; needs reformatting"
rank         = 2
confidence   = 0.81

[datasets.gaps]
description  = "No large-scale Python debugging dataset found (bug → fix format). Recommend synthetic generation for this gap."
gap_severity = "moderate"

[base_model]
recommended_model  = "Qwen/Qwen2.5-Coder-7B"
provider           = "HuggingFace"
parameter_count    = "7B"
license            = "Apache-2.0"
rationale          = """
Qwen2.5-Coder has disproportionate code pre-training, outperforms general 7B models on HumanEval
by ~15–20 points at the same parameter count. Apache-2.0 license permits fine-tuning and
redistribution of derivative models.
"""
vram_qlora_estimate_gb = 8.5
confidence             = 0.91

[[base_model.alternatives]]
model     = "deepseek-ai/deepseek-coder-7b-instruct-v1.5"
license   = "deepseek_license"     # restricts commercial use — flag
rationale = "Strong code performance but license requires review for downstream use"

[benchmarks]
primary   = ["HumanEval", "MBPP"]
secondary = ["HumanEval+", "BigCodeBench"]
notes     = "HumanEval is the de facto standard for Python completion. MBPP covers broader programming problems."

[open_questions]
items = [
  "Dataset license for iamtarun/python_code_instructions_18k_alpaca is unclear — Education Manager should verify before training.",
  "Consider whether debugging tasks (bug→fix) should be included; no public dataset found, synthetic generation required.",
]

[provenance]
source_count  = 14
sources_used  = [
  "https://huggingface.co/datasets/iamtarun/python_code_instructions_18k_alpaca",
  "https://huggingface.co/datasets/bigcode/the-stack",
  # ... etc
]
fact_checks_run = 3
contested_claims = 0
```

---

## 6. Research Manager Behaviour

The Research Manager is the department's permanent orchestrator. It does not execute retrieval or synthesis directly — it plans, delegates, monitors, and synthesises the outputs of workers.

### 6.1 Brief Intake and Validation

On receiving a Research Brief (from the CEO event bus, from another department Manager, or directly from the Owner via the Workers panel):

1. **Schema validation:** confirm the brief conforms to the Research Brief schema. Reject malformed briefs with a structured error (not a silent failure — see project P-criterion on no silent failures).
2. **Scope clarification:** if `description` is ambiguous or too broad for the declared `depth`, the Manager publishes a clarification request to the CEO event bus (CEO surfaces it to the Owner). The Manager does not block indefinitely — if no clarification is received within a configurable timeout (default: 2 minutes for automated pipelines, indefinite for Owner-issued briefs), it proceeds with best-effort interpretation and documents the assumption in the deliverable.
3. **Memory pre-check:** query Librarian as described in Stage 1.
4. **Job registration:** write the job record to the Research Registry.

### 6.2 Parallel Execution

The Manager builds the Query Plan as a DAG. Independent sub-queries run in parallel — the Manager spawns workers concurrently and collects results via the event bus. Dependent sub-queries (e.g. "find papers that cite X" where X is determined by a preceding sub-query) are scheduled only after their dependencies resolve.

Maximum concurrent worker count is configurable (default: 4 workers) and bounded by the Hardware panel's reported available CPU/RAM headroom — the Manager queries the Hardware panel before spawning workers and delays if resources are constrained.

### 6.3 Failure Handling

Workers report success or failure to the Research Manager via the event bus. On worker failure:

- **Transient failures** (network timeout, rate limit): the Manager retries up to 3 times with exponential backoff. After 3 failures, the source is marked `status: failed` and dropped from the source set. The Manager notes the failure in the deliverable's provenance section.
- **Permanent failures** (404, access denied, blocked by Security Guard): no retry. Source dropped immediately.
- **Partial results:** if fewer than a minimum number of sources are retrieved (configurable, default: 3 per sub-query), the Manager escalates a warning to the CEO for Owner awareness. The deliverable is still produced with a low-confidence flag.

The circuit breaker (50 errors / 10 seconds) inherited from the core architecture applies to individual workers, not the Manager itself.

### 6.4 Ongoing Monitor Jobs

When `deliverable_type = "ongoing_monitor"`, the Research Department registers the brief as a **recurring research task** in the Tasks panel. On each scheduled run:

1. The Manager re-executes Stages 2–4 (Source Discovery, Deep Retrieval, Evaluation) with `recency_requirement` set to "since last run".
2. New sources are identified by comparing content hashes against the previous run's source set.
3. Synthesis Worker produces a **delta deliverable** — only new findings, not a full re-synthesis. The full deliverable remains accessible in the Registry for context.
4. If no new material is found, the Manager issues a "no change" signal rather than an empty deliverable, so the Owner isn't flooded with empty reports.

---

## 7. Integration with Other Departments

### 7.1 Education Department

The Research Department is the **mandatory upstream** for Education Department training jobs. The Education Manager cannot start a training job without a completed Domain Brief attached to the job record (or an explicit Owner override recorded in the job log).

The handoff protocol:

```
Education Manager publishes: ResearchBriefRequest {
    domain: "Python Code Fine-Tuning",
    output_schema: "education_domain_brief_v1",
    depth: "standard",
    urgency: "normal"
}

Research Manager responds (via event bus): ResearchBriefComplete {
    brief_id: "brief-20260629-001",
    deliverable_path: "research/deliverables/brief-20260629-001.toml",
    confidence: 0.88
}

Education Manager reads deliverable and proceeds to Stage 1 (Domain Specification).
```

### 7.2 Engineering Department

The Engineering Department requests research for technical decisions: library selection, API evaluation, performance benchmarks for candidate approaches, security vulnerability research, and dependency audits. The deliverable type is typically `comparison_table` or `source_inventory`.

Example Research Brief triggers from Engineering:
- "Which Python async HTTP libraries are actively maintained and support HTTP/3 as of 2026?"
- "What are known CVEs for the current version of dependency X?"
- "Compare vLLM vs SGLang vs llama.cpp for throughput on 7B models with 8K context"

### 7.3 Communication Department

The Communication Department requests audience research, competitor analysis, and topic landscape reports to support content creation and outreach. Deliverable types: `competitive_intelligence`, `research_report`, `fact_sheet`.

### 7.4 Owner (Direct Requests)

The Owner can issue Research Briefs directly through the Orchestrator chat (the CEO translates the Owner's natural language request into a structured brief) or via a "New Research Job" form in the Workers panel's Research section. The Owner can also browse the Research Registry for past deliverables and re-run any job.

---

## 8. Source Authority System

The Research Department maintains a **Source Authority Database** — a curated, updateable scoring table for known sources, used to bootstrap Evaluation Worker scoring before content-based analysis completes.

### 8.1 Authority Tiers

| Tier | Description | Examples | Default Authority Score |
|------|-------------|---------|------------------------|
| **Tier A** | Peer-reviewed, primary sources | arXiv papers, published journal articles, official vendor documentation | 0.90 |
| **Tier B** | High-quality secondary sources | Well-known technical blogs, official GitHub repositories, established industry publications | 0.75 |
| **Tier C** | Community sources with editorial standards | Stack Overflow (accepted answers), Reddit (r/MachineLearning, r/LocalLLaMA, with vote threshold) | 0.55 |
| **Tier D** | Unverified community content | General forums, anonymous blog posts, social media | 0.30 |
| **Tier E** | Blocked / prohibited | Known misinformation sources, domains on the Security Guard blocklist | 0.00 (dropped) |

The Source Authority Database is seeded with a default set of known domains and their tier assignments. The Owner can promote or demote domains via the Options panel ("Research Source Trust Settings"). Changes are recorded in the audit log.

### 8.2 Dynamic Authority Adjustment

During Fact-Checking (Stage 5), if a Tier A source contradicts a Tier B source and a Tier B source is subsequently found to be citing a retracted paper or a misquoted result, the Fact-Check Worker can submit a **trust signal** to the Source Authority Database. Trust signals are not applied automatically — they queue for Owner review. Over time, the database accumulates source-level reputation that improves evaluation quality across all future research jobs.

---

## 9. Privacy and Provenance

### 9.1 Internal Memory as Research Input

When the Research Department queries internal memory (chat history, user documents) as a Tier 1 source, the following controls apply:

- **Explicit consent by default:** using personal data (chat history, private notes) as research input requires an explicit permission flag in the Research Brief (`allow_personal_memory: true`). This flag defaults to `false` for briefs issued by other departments; it defaults to `true` for briefs issued directly by the Owner.
- **Data scope limitation:** the Manager queries only the memory backends explicitly declared in the brief's `memory_scope` field. It does not speculatively search all memory backends.
- **No exfiltration:** retrieved personal content is never written into externally-visible deliverables without the Owner's explicit approval. Domain Briefs passed to other departments contain only synthesised findings, never raw personal data.

### 9.2 Provenance Chain

Every Research Deliverable carries a complete provenance chain:

- Which sources were fetched, from which tier, at what time
- Which sources were dropped and why (score below threshold, fact-check failed, blocked)
- Which claims were fact-checked and their outcome
- Which workers produced which outputs (worker IDs, model used for synthesis)
- SHA-256 hash of each raw source document at time of retrieval

The Security Guard can audit any deliverable's provenance chain on demand. The provenance chain is stored in the Research Registry alongside the deliverable and is never modified after the job completes.

---

## 10. Backend Module Layout

```
/backend
  /research
    manager.py                  # Research Manager — orchestrates all stages
    registry.py                 # CRUD for research jobs and deliverables (Postgres/SQLite)
    brief_validator.py          # Research Brief schema validation
    query_planner.py            # Stage 1: decompose brief into sub-query DAG
    /sources
      base.py                   # SourceAdapter interface + SourceRecord dataclass
      /adapters
        huggingface_api.py      # Tier 2: HuggingFace Hub
        arxiv_api.py            # Tier 2: arXiv
        semantic_scholar_api.py # Tier 2: Semantic Scholar
        github_api.py           # Tier 2: GitHub REST
        paperwithcode_api.py    # Tier 2: PapersWithCode
        openalex_api.py         # Tier 2: OpenAlex
        web_search.py           # Tier 3: delegates to web_search adapter
        web_fetch.py            # Tier 3: delegates to web_fetch adapter
        memory_librarian.py     # Tier 1: delegates to Librarian
      authority_db.py           # Source Authority Database (read/write)
      rate_limiter.py           # per-domain token bucket
    /workers
      source_discovery.py       # Stage 2 worker
      deep_retrieval.py         # Stage 3 worker
      evaluation.py             # Stage 4 worker
      fact_check.py             # Stage 5 worker
      /synthesis
        base.py                 # SynthesisWorker interface
        report.py               # long-form narrative reports
        domain_brief.py         # structured TOML brief (for Education, Engineering)
        comparison_table.py     # side-by-side comparison output
        source_inventory.py     # annotated source list
        fact_sheet.py           # short dense summary
        competitive_intel.py    # competitor analysis
        gap_analysis.py         # gap identification
        monitor_delta.py        # delta summary for ongoing monitors
    /schemas
      education_domain_brief_v1.toml  # schema definition for Education handoff
      engineering_brief_v1.toml
      # ... extensible: new department schemas added here without changing core
    api.py                      # REST endpoints
      # GET  /research/jobs
      # POST /research/jobs              (submit Research Brief)
      # GET  /research/jobs/<id>         (status + stage progress)
      # POST /research/jobs/<id>/cancel
      # GET  /research/jobs/<id>/deliverable
      # GET  /research/deliverables      (all completed deliverables)
      # GET  /research/deliverables/<id> (specific deliverable)
      # POST /research/deliverables/<id>/rerun
      # GET  /research/authority         (Source Authority Database read)
      # PATCH /research/authority/<domain> (Owner trust adjustment)

/frontend
  /components/research/
    ResearchPanel.tsx            # main Research sub-view inside Workers panel
    ResearchJobList.tsx          # list of all jobs with status + freshness indicators
    ResearchJobDetail.tsx        # stage progress, live log, source list
    DeliverableViewer.tsx        # renders deliverable (report, brief, table) in UI
    SourceInspector.tsx          # browse sources for a job: scores, fact-check status
    ProvenanceViewer.tsx         # full provenance chain for a deliverable
    NewResearchJobForm.tsx       # Owner-issued brief form (alternatively routed via CEO chat)
    AuthoritySettings.tsx        # Source trust tier management (in Options panel)
    OngoingMonitorList.tsx       # list of recurring research jobs (links to Tasks panel)
```

---

## 11. Security Guard Integration

The Security Guard has audit hooks into the Research Department at the following points:

- **Source Discovery:** all discovered URLs are checked against the Security Guard's domain blocklist before any retrieval is attempted. Blocked URLs are dropped silently with a log entry (never surfaced to workers as "blocked" — treated as if they returned no results, to avoid blocklist inference attacks).
- **Deep Retrieval:** raw fetched content is scanned for embedded malicious payloads (script injection in fetched HTML, malicious macros in fetched documents). Flagged content is quarantined and the source is dropped.
- **Deliverable provenance:** before a deliverable is marked `status: complete`, the Security Guard verifies that every source URL in the provenance chain was either on the authority database or explicitly approved, and that no blocked domain contributed to the synthesis. If a blocked source snuck through (e.g. a redirect chain that ended at a blocked domain), the deliverable is quarantined for Owner review.
- **Ongoing Monitors:** the Security Guard runs a lightweight periodic audit of all active monitor jobs to ensure their source lists haven't drifted into blocked territory over time.

---

## 12. Open Questions for Round Table

1. **Brief issuance authority:** Should workers from other departments be able to issue Research Briefs directly, or must all briefs pass through the CEO → Research Manager chain? Direct issuance is faster (no CEO round-trip latency) but bypasses the CEO's scope-validation and prompt-cleaning function. Recommend: department Managers can issue briefs directly; individual workers cannot.

2. **Research as a blocking dependency:** The Education Department spec proposes that a training job cannot start without a completed Research Brief. Is this the right pattern for all departments? Engineering might want to start work while research runs in parallel, accepting a research update mid-task. A `research_dependency_mode` flag on the brief (blocking | advisory) could handle both cases.

3. **Deliverable format for Owner consumption:** Domain Briefs in TOML are machine-readable but not human-friendly. Should the Research Department produce a parallel human-readable version (Markdown summary) of every Domain Brief, stored alongside the TOML? This adds synthesis cost but makes deliverables usable without a viewer component.

4. **Source Authority Database governance:** Who can modify the authority database beyond the Owner? Should the Security Guard be able to auto-demote sources that repeatedly fail fact-checks, without Owner intervention? Auto-demotion is powerful but risks a feedback loop if fact-check quality is imperfect.

5. **Research vs. real-time data:** For time-sensitive queries (current stock prices, live API status, breaking news), the research pipeline's caching model (24-hour TTL) is inappropriate. Should certain query types bypass caching entirely and be routed to a "live data" sub-pipeline? Or is real-time data outside the Research Department's scope and handled instead by a dedicated LiveData adapter?

6. **Synthesis model selection:** Synthesis Workers call a language model to produce narrative outputs. Which model is used? The default system model? A dedicated synthesis-optimised model from the Education Department? A user-configurable selection per deliverable type? This decision affects quality, cost (VRAM), and latency significantly.

7. **Cross-job deduplication:** If two research jobs run simultaneously and both retrieve the same source, do they share the cached copy or each maintain their own? Sharing reduces fetches but introduces concurrency complexity. A shared content-addressed cache (keyed by URL + retrieved_at day) with read-after-write consistency could solve this — worth speccing before implementation.

8. **Legal and copyright exposure:** Full-text retrieval of web content and PDFs creates potential copyright concerns if content is stored in memory backends long-term. The 24-hour ephemeral job cache mitigates this for most cases, but content that gets promoted to long-term memory (user-approved) may require licence checking. Should the Security Guard enforce this, or is it an Owner responsibility?

---

## 13. Implementation Order (Suggested)

1. **registry.py + brief_validator.py** — job store and schema validation. The foundation; everything else depends on it.
2. **memory_librarian.py** — Tier 1 source, memory pre-check. Validates Librarian integration before external calls are introduced.
3. **web_search.py + web_fetch.py** — Tier 3 web retrieval. Wires to existing adapters; validates the fetching pipeline end-to-end.
4. **evaluation.py** — scoring and filtering. Test with a fixed source set before plugging in live retrieval.
5. **synthesis/report.py** — simplest synthesis type; validates the full pipeline with human-readable output.
6. **api.py (GET /research/jobs, POST /research/jobs)** — minimal REST surface to unblock UI work.
7. **ResearchPanel.tsx + ResearchJobDetail.tsx** — UI, wired to SSE for live stage progress.
8. **huggingface_api.py + arxiv_api.py** — first Tier 2 adapters. These are the highest-value for Education Department integration.
9. **domain_brief.py (synthesis)** — Education Department handoff. Validates the full Education → Research → Education loop.
10. **fact_check.py** — add fact-checking after core pipeline is stable and producing useful output.
11. **authority_db.py + AuthoritySettings.tsx** — Source Authority Database, after evaluation Worker has been validated.
12. **Remaining Tier 2 adapters** — Semantic Scholar, GitHub, PapersWithCode, OpenAlex, in order of anticipated use.
13. **monitor_delta.py + OngoingMonitorList.tsx** — Ongoing Monitor recurring jobs, after Tasks panel integration is confirmed.
14. **Security Guard hooks** — audit integration after core pipeline is stable.
15. **Specialist Tier 5 adapters** — as individual adapters, one by one, gated behind Adapters panel configuration.

---

*End of document.*
