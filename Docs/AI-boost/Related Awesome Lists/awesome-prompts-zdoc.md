# Awesome Prompts (zdoc)

**Source URL:** https://www.zdoc.app/en/ai-boost/awesome-prompts

**Description:** This is a comprehensive curated collection of prompts, frameworks, and papers with an engineering bias. The resource covers two main approaches to prompt engineering: (1) Prompt templates for copy-paste recipes and system prompts, and (2) Prompt as engineering including LM programs (DSPy), prompt testing (promptfoo), structural generation control (Guidance), and automatic optimization (TextGrad, GEPA). The collection includes prompts for various domains including coding, DevOps, data engineering, AI/ML, product strategy, healthcare, legal compliance, and more. It also features frameworks for prompt programming, automatic optimization, evaluation/testing, red team security, and low-code workflow platforms. Additionally, it includes system prompt leaks, prompt engineering techniques, context engineering, agent ecosystem resources (MCP, Skills, Harness), official guides, academic papers, and tools/libraries.

---

# Web Content from https://www.zdoc.app/en/ai-boost/awesome-prompts

[zdoc][1]

[ai-boost/awesome-prompts ][2]

[Github Trending][3]
[Share][4]
English
[English(original)][5][Deutsch][6][Español][7][français][8][日本語][9][한국어][10][Português][11][Русский][12][中文][13]
Commit at: 23 Jul 2026

## Awesome Prompts 🪶


Curated prompts, frameworks, and papers — with an engineering bias.

[Deutsch][14] | [English][15] | [Español][16] | [français][17] | [日本語][18] | [한국어][19] |
[Português][20] | [Русский][21] | [中文][22]

[[Awesome]][23] [[PRs Welcome]][24]

The prompt engineering world has split into two camps:
* **Camp 1 — Prompt templates**: collect system prompts, share copy-paste recipes, curate persona
  prompts. Useful, but limited.
* **Camp 2 — Prompt as engineering**: compile LM programs (DSPy), test and regress prompts
  (promptfoo), control generation structurally (Guidance), optimize prompts automatically (TextGrad,
  GEPA). This is where the long-term value is.

This repo covers both. The engineering camp gets more space.

## Table of Contents
* [📋 Prompts][25] — copy-paste ready
  * [Coding & Development][26]
  * [DevOps & SRE][27]
  * [Data Engineering][28]
  * [AI & ML][29]
  * [Product & Strategy][30]
  * [Project Management][31]
  * [Healthcare & Clinical][32]
  * [Industrial & Automotive][33]
  * [Legal & Compliance][34]
  * [Knowledge & Documentation][35]
  * [Writing & Academic][36]
  * [Learning & Education][37]
  * [Research & Analysis][38]
  * [Productivity & Tasks][39]
  * [Safety & Compliance][40]
  * [Meta & Prompt Engineering][41]
  * [Image, Video & Audio Generation][42]
  * [Creative & Role-play][43]
  * [Game Development][44]
  * [Translation][45]
  * [Legacy (2023 era)][46]
* [🔬 Frameworks][47] — the engineering camp
  * [Prompt Programming][48]
  * [Automatic Prompt Optimization][49]
  * [Eval & Testing][50]
  * [Red Team & Security][51]
  * [Low-Code & Workflow Platforms][52]
* [🕵️ System Prompt Leaks][53] — learn from production
* [🧠 Prompt Engineering][54] — techniques & defense
* [🔭 Context Engineering][55]
* [🤖 Agent Ecosystem][56] — MCP, Skills, Harness
* [📖 Official Guides][57]
* [📄 Papers][58] — Foundations, Optimization, Reasoning, RAG, Agents, Multi-Agent, Safety,
  Self-Improving Agents, Tool Use, Evaluation, Memory, Multimodal
* [🛠 Tools & Libraries][59]

## Prompts

All prompts are open — click, copy, use directly.

### Coding & Development

─────┬────────────────────────────────────────────────────────────────────────────────────────┬─────
Name │Description                                                                             │Promp
     │                                                                                        │t    
─────┼────────────────────────────────────────────────────────────────────────────────────────┼─────
🤖   │Plan-first coding agent — security checklist, test discipline, PR summary format (2025) │[prom
Agent│                                                                                        │pt][6
ic   │                                                                                        │0]   
Coder│                                                                                        │     
─────┼────────────────────────────────────────────────────────────────────────────────────────┼─────
🔔   │Design coding agents that notice what matters before being asked — reactive / scheduled │[prom
Proac│/ situation-aware levels, insight policy (monitor → evaluate → decide → ground → adapt),│pt][6
tive │emission gates, developer context model, and feedback-driven learning; based on "Agentic│1]   
Codin│Coding Needs Proactivity, Not Just Autonomy" (arXiv 2605.06717, 2026) and Google's Jules│     
g    │evaluation work (June 2026)                                                             │     
Agent│                                                                                        │     
Archi│                                                                                        │     
tect │                                                                                        │     
─────┼────────────────────────────────────────────────────────────────────────────────────────┼─────
🪿   │Vendor-neutral open-source AI engineering agent operator — MCP-native extension         │[prom
Goose│discipline, plan-then-execute loops, multi-provider awareness, least-privilege          │pt][6
AI   │permission model; based on block/goose → aaif-goose/goose under the Linux Foundation    │2]   
Engin│Agentic AI Foundation (Apache-2.0, ~50k stars, June 2026)                               │     
eerin│                                                                                        │     
g    │                                                                                        │     
Agent│                                                                                        │     
Opera│                                                                                        │     
tor  │                                                                                        │     
─────┼────────────────────────────────────────────────────────────────────────────────────────┼─────
♊   │Gemini-CLI-optimized prompt engineer — four-element task prompts                        │[prom
Gemin│(goal/context/constraints/done-when), GEMINI.md discipline, built-in tool preferences   │pt][6
i CLI│(search/file/shell/fetch), MCP @-server mentions, multimodal inputs, and anti-patterns; │3]   
Promp│based on google-gemini/gemini-cli (Apache-2.0, 105k+ stars, 2026)                       │     
t    │                                                                                        │     
Archi│                                                                                        │     
tect │                                                                                        │     
─────┼────────────────────────────────────────────────────────────────────────────────────────┼─────
🛠    │Codex-optimized prompt engineer — four-element task prompts                             │[prom
OpenA│(goal/context/constraints/done-when), AGENTS.md discipline, tool preferences, and       │pt][6
I    │anti-patterns; based on OpenAI's official Codex Prompting Guide (Feb 2026)              │4]   
Codex│                                                                                        │     
CLI  │                                                                                        │     
Promp│                                                                                        │     
t    │                                                                                        │     
Archi│                                                                                        │     
tect │                                                                                        │     
─────┼────────────────────────────────────────────────────────────────────────────────────────┼─────
🖥    │Cline-optimized prompt engineer — four-element task prompts                             │[prom
Cline│(goal/context/constraints/done-when), Plan/Act mode discipline, `.clinerules` authoring,│pt][6
Promp│MCP server and plugin preferences, multi-agent team scoping, and headless CI/CD         │5]   
t    │conventions; based on cline/cline (Apache-2.0, 64k+ stars, 2026)                        │     
Archi│                                                                                        │     
tect │                                                                                        │     
─────┼────────────────────────────────────────────────────────────────────────────────────────┼─────
🔱   │Grok-Build-optimized prompt engineer — four-element task prompts                        │[prom
Grok │(goal/context/constraints/done-when), AGENTS.md / CLAUDE.md project-rule discipline,    │pt][6
Build│`.grok/skills/` authoring, TUI slash commands (`/compact`, `/fork`, `/rewind`), headless│6]   
Promp│`grok -p` / ACP `grok agent stdio` scoping, MCP-aware tool preferences, permission      │     
t    │rules, and sandbox profiles; based on xai-org/grok-build (Apache-2.0, 18k+ stars, July  │     
Archi│2026)                                                                                   │     
tect │                                                                                        │     
─────┼────────────────────────────────────────────────────────────────────────────────────────┼─────
🟠   │MiMo-Code-optimized prompt engineer — four-element task prompts                         │[prom
MiMo │(goal/context/constraints/done-when), build/plan/compose agent selection, persistent    │pt][6
Code │SQLite FTS5 memory (MEMORY.md / checkpoint.md / tasks), `/goal` judge-verified stop     │7]   
Promp│conditions, compose-mode specs-driven workflows, deterministic JS workflows, and        │     
t    │`.mimocode/skills/` authoring; based on XiaomiMiMo/MiMo-Code (MIT, 12k+ stars, June     │     
Archi│2026)                                                                                   │     
tect │                                                                                        │     
─────┼────────────────────────────────────────────────────────────────────────────────────────┼─────
🧩   │Author installable Codex skills in the official Agent Skills format — SKILL.md with     │[prom
OpenA│trigger-tuned description, optional agents/openai.yaml for invocation policy and MCP    │pt][6
I    │dependencies, scripts-only-when-needed discipline, and progressive-disclosure context   │8]   
Codex│design; based on OpenAI's Codex Skills docs and github.com/openai/skills (2026, 22.6k+  │     
Skill│stars)                                                                                  │     
Autho│                                                                                        │     
r    │                                                                                        │     
─────┼────────────────────────────────────────────────────────────────────────────────────────┼─────
🦘   │Design focused, least-privilege Custom Modes for the open-source Roo Code VS Code agent │[prom
Roo  │— role definition, tool allowlist (read/edit/browser/command/mcp), file-permission      │pt][6
Code │discipline, model-routing hints, and mode-specific safety guardrails; outputs           │9]   
Custo│`.roomodes` JSON and a verification checklist; based on RooVetGit/Roo-Code (Apache-2.0, │     
m    │50k+ stars, 2026)                                                                       │     
Mode │                                                                                        │     
Archi│                                                                                        │     
tect │                                                                                        │     
─────┼────────────────────────────────────────────────────────────────────────────────────────┼─────
🐼   │Design agentic coding harnesses for Qwen3-Coder-Next — 80B/3B hybrid MoE economics, 256K│[prom
Qwen3│native context (1M via YaRN), non-thinking output, specialized function-call format, FIM│pt][7
|-Code│editing, plan-then-execute loops, and verifiable reward signals; based on the           │0]   
r-Nex│Qwen3-Coder-Next Technical Report (arXiv 2603.00729, 2026)                              │     
t    │                                                                                        │     
Agent│                                                                                        │     
ic   │                                                                                        │     
Codin│                                                                                        │     
g    │                                                                                        │     
Archi│                                                                                        │     
tect │                                                                                        │     
─────┼────────────────────────────────────────────────────────────────────────────────────────┼─────
📐   │Blueprint-driven Lean 4 prover — dependency-graph decomposition, parallel lemma proving,│[prom
Forma│compiler-feedback refinement loops; 99.2% pass@1 on MiniF2F-test, 75.6% on PutnamBench; │pt][7
l    │based on Goedel-Architect (arXiv 2606.06468, June 2026)                                 │1]   
Theor│                                                                                        │     
em   │                                                                                        │     
Provi│                                                                                        │     
ng   │                                                                                        │     
Archi│                                                                                        │     
tect │                                                                                        │     
─────┼────────────────────────────────────────────────────────────────────────────────────────┼─────
🧪   │Throwaway-prototype skill — logic prototypes (interactive TUI for state machines) and UI│[prom
Proto│prototypes (radically different variants on a single route with floating switcher);     │pt][7
type │based on mattpocock/skills (Jan 2026, 117k+ stars)                                      │2]   
Archi│                                                                                        │     
tect │                                                                                        │     
─────┼────────────────────────────────────────────────────────────────────────────────────────┼─────
🔍   │Security-focused code reviewer — OWASP Top 10, severity grading, fix examples (2026)    │[prom
Code │                                                                                        │pt][7
Revie│                                                                                        │3]   
wer  │                                                                                        │     
─────┼────────────────────────────────────────────────────────────────────────────────────────┼─────
🕸    │Central dispatch agent — task decomposition, parallel delegation, state tracking, error │[prom
Multi│recovery (2026)                                                                         │pt][7
|-Agen│                                                                                        │4]   
t    │                                                                                        │     
Orche│                                                                                        │     
strat│                                                                                        │     
or   │                                                                                        │     
─────┼────────────────────────────────────────────────────────────────────────────────────────┼─────
🎛    │Teams-first multi-agent orchestration layer for Claude Code — 19 specialized agents with│[prom
Teams│model routing (haiku/sonnet/opus), delegation rules, skill triggers, team pipeline      │pt][7
|-Firs│(plan→prd→exec→verify→fix), structured commit trailers, and project memory; based on    │5]   
t    │Yeachan-Heo/oh-my-claudecode (Feb 2026, 35k+ stars)                                     │     
Multi│                                                                                        │     
-Agen│                                                                                        │     
t    │                                                                                        │     
Orche│                                                                                        │     
strat│                                                                                        │     
or   │                                                                                        │     
─────┼────────────────────────────────────────────────────────────────────────────────────────┼─────
🧱   │System prompt for designing reliable agent runtimes — tool minimization, approval gates,│[prom
Agent│memory/compaction, rollback, observability, evals; derived from OpenAI/Anthropic harness│pt][7
Harne│guidance (2026)                                                                         │6]   
ss   │                                                                                        │     
Desig│                                                                                        │     
ner  │                                                                                        │     
─────┼────────────────────────────────────────────────────────────────────────────────────────┼─────
🔐   │Design model-based permission classifiers for coding agents — prompt-injection probe,   │[prom
Auton│reasoning-blind transcript classifier with two-stage filter, block/allow templates,     │pt][7
omous│deny-and-continue semantics, and recursive subagent handoff gates; based on Anthropic's │7]   
Permi│"How we built Claude Code auto mode" (March 2026)                                       │     
ssion│                                                                                        │     
Class│                                                                                        │     
ifier│                                                                                        │     
Archi│                                                                                        │     
tect │                                                                                        │     
─────┼────────────────────────────────────────────────────────────────────────────────────────┼─────
🔁   │Design external loop specifications that let coding agents run without step-by-step     │[prom
Loop │prompting — trigger, goal, five-level verification ladder, architecture, stopping rule, │pt][7
Engin│durable memory; based on "Stop Hand-Holding Your Coding Agent" (arXiv 2607.00038, July  │8]   
eerin│2026)                                                                                   │     
g    │                                                                                        │     
Archi│                                                                                        │     
tect │                                                                                        │     
─────┼────────────────────────────────────────────────────────────────────────────────────────┼─────
🔄   │Turn/goal/time/proactive loop operator for Claude Code — choose the right primitive     │[prom
Claud│(`/goal` · `/loop` · `/schedule`), encode verification skills, manage tokens, and design│pt][7
e    │routines that run while you sleep; based on Anthropic's official "Loop engineering:     │9]   
Code │Getting started with loops" guide (July 2026)                                           │     
Loops│                                                                                        │     
Opera│                                                                                        │     
tor  │                                                                                        │     
─────┼────────────────────────────────────────────────────────────────────────────────────────┼─────
📜   │Reconstruct prompt-heavy enterprise LLM prototypes into traceable, auditable, code-owned│[prom
Audit│systems — source-to-claim pipeline, code-owned contracts, seven validation dimensions,  │pt][8
able │replaceable composition boundary, insight-first answer structure; based on "From Prompts│0]   
Proto│to Contracts" (arXiv 2608.00014, August 2026)                                            │     
type│                                                                                        │     
Recon│                                                                                        │     
stru│                                                                                        │     
ctio│                                                                                        │     
n    │                                                                                        │     
─────┼────────────────────────────────────────────────────────────────────────────────────────┼─────

*Note: This content was fetched from zdoc.app and saved for offline reference. The full content includes an extensive collection of prompts across multiple categories and was truncated during fetching. For the complete content and interactive prompt access, visit the source URL.*