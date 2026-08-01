# Awesome Harness Engineering (zdoc.app)

**Source URL:** https://www.zdoc.app/en/ai-boost/awesome-harness-engineering

**Description:** This resource provides a comprehensive curated list of resources, patterns, and templates for building reliable AI agent harnesses. It covers the discipline of designing the scaffolding — context delivery, tool interfaces, planning artifacts, verification loops, memory systems, and sandboxes — that surrounds an AI agent and determines whether it succeeds or fails on real tasks. The list focuses on the harness components rather than the model itself, recognizing that these components exist because the model can't do them alone.

---

# Web Content from https://www.zdoc.app/en/ai-boost/awesome-harness-engineering

[zdoc][1]

[ai-boost/awesome-harness-engineering ][2]

[Github Trending][3]
[Share][4]
English
[English(original)][5][Deutsch][6][Español][7][français][8][日本語][9][한국어][10][Português][11][Русский][12][中文][13]
Commit at: 25 Jul 2026
[Awesome Harness Engineering]

# Awesome Harness Engineering

Curated resources, patterns, and templates for building reliable AI agent harnesses.

[[Awesome]][14] [[License: CC0]][15] [[GitHub Stars]][16] [[GitHub Forks]][17] [[Last Commit]][18]
[[linux.do]][19]

[Deutsch][20] | [English][21] | [Español][22] | [Français][23] | [日本語][24] | [한국어][25] |
[Português][26] | [Русский][27] | [中文][28]

**Harness engineering** is the discipline of designing the scaffolding — context delivery, tool
interfaces, planning artifacts, verification loops, memory systems, and sandboxes — that surrounds
an AI agent and determines whether it succeeds or fails on real tasks.

This list focuses on the *harness*, not the model. Every component here exists because the model
can't do it alone — and the best harnesses are designed knowing those components will become
unnecessary as models improve.

## Contents
* [📐 Foundations][29]
* [🧩 Design Primitives][30]
  * [🔄 Agent Loop][31]
  * [🗺️ Planning & Task Decomposition][32]
  * [📦 Context Delivery & Compaction][33]
  * [🔧 Tool Design][34]
  * [🔌 Skills & MCP][35]
  * [🛡️ Permissions & Authorization][36]
  * [🧠 Memory & State][37]
  * [⚙️ Task Runners & Orchestration][38]
  * [✔️ Verification & CI Integration][39]
  * [👁️ Observability & Tracing][40]
  * [🐛 Debugging & Developer Experience][41]
  * [🧑‍💼 Human-in-the-Loop][42]
* [🔍 Reference Implementations][43]
  * [🎓 Tutorials & Educational][44]
  * [🏭 Generators & Meta-Harnesses][45]
  * [🧪 Demo Harnesses][46]
  * [🗂️ Adjacent Collections][47]
* [🔒 Security, Sandbox & Permissions][48]
* [✅ Evals & Verification][49]
* [📋 Templates][50]
* [📚 Related Awesome Lists][51]
* [🤝 Contributing][52]

## Foundations

Canonical essays that define what harness engineering is and why it matters.
* [Harness Engineering][53] — OpenAI's framing of harness engineering as a discipline: how to design
  the scaffolding that lets Codex and similar agents operate reliably in an agent-first world.
* [Unrolling the Codex Agent Loop][54] — OpenAI's detailed breakdown of the Codex agent loop,
  exposing each harness component and where it can be improved.
* [Run Long-Horizon Tasks with Codex][55] — OpenAI's practice guide for long-horizon task planning:
  introduces Plan.md, Implement.md, Documentation.md as reusable harness artifacts.
* [Building Effective Agents][56] — Anthropic's foundational guide on agent architecture, covering
  when to use workflows vs. agents and how to compose primitives.
* [Harness Design for Long-Running Application Development][57] — Anthropic's engineering blog on
  designing harnesses for sustained, multi-session development tasks. Key insight: every harness
  component assumes the model can't do something; those assumptions expire.
* [Writing Effective Tools for Agents][58] — Anthropic's guide on tool interface design: naming,
  schemas, error surfaces, and the principle that tool design is agent UX.
* [Beyond Permission Prompts][59] — Anthropic on building structured permission and authorization
  systems into agent harnesses instead of relying on natural-language permission text.
* [Demystifying Evals for AI Agents][60] — Anthropic's framework for evaluating agent behavior: what
  to measure, how to build eval harnesses, and why unit-test-style evals fail for agents.
* [What is an AI Agent?][61] — IBM's definitional piece, useful for anchoring harness design
  decisions to a clear model of what an agent actually is.
* [Agent Development Kit: Making it easy to build multi-agent applications][62] — Google's
  announcement and design rationale for ADK: explains the multi-agent topology, tool registration
  model, and eval pipeline that shaped their framework. Complements the Anthropic/OpenAI framing
  with Google's production perspective.
* [Harness Engineering][63] — Martin Fowler's synthesis of what harness engineering practice looks
  like: three interlocking systems — context engineering (curating what the agent knows),
  architectural constraints (deterministic linters and structural tests), and entropy management
  (periodic agents that repair documentation drift). The "humans on the loop" framing — harness
  engineers who design and maintain agent environments rather than inspecting individual outputs —
  is the clearest conceptual map of what the discipline actually entails.
* [The Anatomy of an Agent Harness][64] — LangChain's structural breakdown of the five primitives
  that compose a harness: filesystem (durable state + agent collaboration surface), code execution
  (autonomous problem-solving without pre-designed solutions), sandbox (isolation + verification),
  memory (cross-session persistence), and context management (compaction against "context rot"). The
  co-evolution warning — models trained with specific harnesses can become overfitted to those
  designs — explains why harness architecture choices have lasting consequences beyond the immediate
  task.
* [Building AI Coding Agents for the Terminal: Scaffolding, Harness, Context Engineering, and
  Lessons Learned][65] — The first systematic practitioner paper on terminal-native coding agent
  harness design: eager-construction scaffolding (pre-build all components before the first message
  to eliminate first-call latency and race conditions), compound multi-model architecture (different
  model instances for execution, reasoning, critique, and vision tasks), 5-layer defense-in-depth
  safety, and schema-filtered planning subagents (enforce behavioral constraints via tool schema
  rather than runtime permission checks). The five lessons distilled from building OpenDev apply to
  any server-side agent harness.
* [Natural-Language Agent Harnesses][66] — Proposes externalizing agent control logic as portable
  natural-language artifacts (NLAHs) executed by a shared Intelligent Harness Runtime, enabling
  harness design to be studied, transferred, and reproduced rather than buried in bespoke controller
  code. Directly addresses the root cause of harness fragility: control logic scattered across
  framework defaults and hard-coded controller logic that can't be inspected, versioned, or
  transferred.
* [Ranking Engineer Agent (REA): Meta's Autonomous AI System for Ads Ranking][67] — Meta's
  production harness for multi-day ML pipeline automation with hibernate-and-wake checkpointing for
  resuming interrupted 6-hour tasks without losing context. Demonstrates harness design for
  scientific workflows where individual turns can exceed model context limits but the overall
  pipeline must maintain coherence across days.
* [Supercharge Your AI Agents: The New ADK Integrations Ecosystem][68] — Google's 2026 update to
  Agent Development Kit expanding the ecosystem integrations (Hugging Face, GitHub, Daytona, Notion,
  etc.) and providing reference patterns for how orchestration harnesses wire external services
  without losing determinism or state coherence.
* [2026 Agentic Coding Trends Report][69] — Anthropic's industry benchmark identifying
  infrastructure configuration as a first-class optimization variable: harness setup alone can swing
  benchmarks by 5+ percentage points. Documents the shift from single-agent to orchestrated
  multi-agent teams and introduces the "agentic engineering platform" category, bridging the gap
  between agent frameworks and production deployment infrastructure.
* [How We Build Azure SRE Agent with Agentic Workflows][70] — Architecture walkthrough of
  Microsoft's agent that has handled 35,000+ production incidents autonomously, reducing Azure App
  Service time-to-mitigation from 40.5 hours to 3 minutes. Documents the integration of MCP tools,
  telemetry, code repositories, and incident management platforms into a single agent harness with
  human-in-the-loop governance. The most data-backed production harness case study published in
  2026.
* [Context Engineering for Reliable AI Agents: Lessons from Building Azure SRE Agent][71] —
  Microsoft's account of shifting from 100+ bespoke tools and a prescriptive prompt to a
  filesystem-based context engineering system for their SRE agent. Key finding: exposing everything
  (source code, runbooks, query schemas, past investigation notes) as files and letting the agent
  use `read_file`, `grep`, `find`, and `shell` outperformed specialized tooling — "Intent Met" score
  rose from 45% to 75% on novel incidents.
* [Harness Engineering: Structured Workflows for AI-Assisted Development][72] — Red Hat's enterprise
  perspective on harness engineering (April 7, 2026): AI writes better code when you design the
  environment it works in. Emphasizes structured context over free-form tickets, expanding the
  agent's toolbox through MCP integrations (CI status, deployment logs, runtime metrics) as real
  data sources, and a four-pillar model (vibes, specs, skills, agents) for organizing how humans and
  agents collaborate.
* [Harness engineering for coding agent users][73] — Birgitta Böckeler's systematic mental model
  (April 2026) for coding-agent harnesses, framing them as feedforward guides plus feedback sensors
  that self-correct before output reaches human eyes. Distinguishes computational controls (linters,
  tests) from inferential ones (LLM-as-judge), and argues that harnessability should become a
  first-class criterion in technology and architecture decisions.
* [A Practical Guide to Building AI Agents][74] — OpenAI's April 2026 comprehensive guide distilling
  production deployment practices for agent systems.
* [AI Engineering][75] — Full Stack Deep Learning's systematic breakdown of AI engineering as a
  discipline distinct from ML engineering: focuses on harness components (context delivery, tool
  interfaces, verification loops) that bridge the gap between model capabilities and reliable
  real-world performance.

## Design Primitives

### Agent Loop

Core loop patterns that define how agents think, act, and iterate.
* [ReAct: Synergizing Reasoning and Acting in Language Models][76] — The foundational agent loop
  pattern: interleave Thought (reasoning) and Action (tool use) to solve multi-step problems.
* [Reflexion: Language Agents with Verbal Reinforcement Learning][77] — Extends ReAct with a
  self-reflection loop: after each episode, the agent generates verbal feedback on what went wrong
  and stores it in episodic memory for future episodes.
* [Tree of Thoughts (ToT)][78] — Enables agents to explore multiple reasoning paths in parallel,
  evaluate them, and backtrack, rather than committing to a single linear chain.
* [Chain of Thought with Self-Consistency][79] — Generates multiple reasoning chains, aggregates
  the most common answer, and improves reliability on math and logic tasks.
* [Least-to-Most Prompting][80] — Decomposes complex problems into subproblems, solves them
  sequentially, and feeds intermediate results into later steps.
* [AutoGPT][81] — Autonomous agent that breaks goals into sub-goals, executes them with tools, and
  loops until completion. Early demonstration of recursive goal decomposition.
* [BabyAGI][82] — Task management agent that creates, prioritizes, and executes tasks based on
  previous results. Demonstrates iterative task refinement.
* [AgentLoop][83] — Reference implementation of agent loop patterns (ReAct, Reflexion, ToT) with
  tool integration and state management.
* [LangGraph][84] — Framework for building stateful, multi-actor applications with LLMs, built on
  the concept of cyclic graphs where nodes represent agent actions and edges represent state
  transitions.
* [CrewAI][85] — Framework for orchestrating role-playing autonomous agents with defined roles,
  goals, and backstories.
* [AutoGen][86] — Microsoft's framework for multi-agent conversations where agents can interact
  with each other to solve tasks.
* [State Machines for Agents][87] — Using finite state machines to model agent behavior, ensuring
  predictable state transitions and preventing infinite loops.
* [Event-Driven Agent Architectures][88] — Designing agents that respond to external events rather
  than polling, improving efficiency and real-time responsiveness.

### Planning & Task Decomposition

How agents break down complex goals into executable steps.
* [Plan-and-Solve Prompting][89] — Two-stage prompting: first generate a plan, then execute each
  step with the plan as context.
* [Task Decomposition with LLMs][90] — Survey of techniques for breaking down complex tasks into
  subtasks using language models.
* [Hierarchical Planning][91] — Multi-level planning where high-level plans are refined into
  lower-level subplans.
* [Goal-Directed Agent Planning][92] — Planning with explicit goal states and success criteria.
* [Temporal Planning][93] — Planning with time constraints and deadlines.
* [Contingency Planning][94] — Planning with fallback strategies for when initial plans fail.
* [Plan Verification][95] — Techniques for validating that generated plans are feasible and safe.
* [Plan Execution Monitoring][96] — Tracking plan execution and detecting deviations.

### Context Delivery & Compaction

How to give agents the right information at the right time without overwhelming them.
* [Context Engineering for AI Agents][97] — Anthropic's guide on curating and structuring context
  for agent tasks.
* [Retrieval-Augmented Generation (RAG)][98] — Framework for retrieving relevant documents and
  feeding them as context to the model.
* [Context Window Management][99] — Strategies for working within limited context windows.
* [Context Compression][100] — Techniques for compressing context while preserving important
  information.
* [Dynamic Context Selection][101] — Selecting relevant context dynamically based on the current
  task.
* [Context Caching][102] — Caching frequently-used context to reduce costs and latency.
* [Context Hierarchies][103] — Organizing context into hierarchical layers (global, session,
  task-specific).
* [Context Compaction Strategies][104] — Summary-based compaction, importance-based filtering,
  and semantic clustering.

### Tool Design

Principles for designing tools that agents can use effectively.
* [Tool Design for AI Agents][105] — Anthropic's comprehensive guide on tool interface design.
* [Tool Schema Design][106] — Best practices for defining tool schemas (names, descriptions,
  parameters).
* [Tool Error Handling][107] — Designing tools that provide clear error messages and recovery
  paths.
* [Tool Composition][108] — Combining multiple tools into workflows.
* [Tool Discovery][109] — Helping agents discover available tools.
* [Tool Validation][110] — Validating tool inputs and outputs.
* [Tool Security][111] — Designing tools with security in mind (input validation, output sanitization).
* [Tool Performance][112] — Optimizing tools for speed and efficiency.

### Skills & MCP

Model Context Protocol and skill systems for extending agent capabilities.
* [Model Context Protocol (MCP)][113] — Open standard for connecting AI models to external data and
  tools.
* [MCP Server Implementation Guide][114] — How to build MCP servers.
* [MCP Client Integration][115] — How to integrate MCP clients into applications.
* [Skill Systems][116] — Frameworks for defining and managing agent skills.
* [Skill Discovery][117] — Helping agents discover available skills.
* [Skill Composition][118] — Combining skills into complex behaviors.
* [Skill Versioning][119] — Managing skill versions and compatibility.
* [Skill Marketplace][120] — Platforms for sharing and discovering skills.

### Permissions & Authorization

Safety and access control systems for agent operations.
* [Permission Systems for Agents][121] — Anthropic's guide on building permission systems.
* [Authorization Frameworks][122] — Frameworks for managing agent permissions.
* [Human-in-the-Loop Approval][123] — Designing approval workflows for agent actions.
* [Permission Granularity][124] — Determining the right level of permission granularity.
* [Permission Auditing][125] — Logging and auditing agent permissions.
* [Permission Revocation][126] — Revoking permissions dynamically.
* [Permission Delegation][127] — Delegating permissions between agents.
* [Zero-Trust Agent Security][128] — Applying zero-trust principles to agent security.

### Memory & State

How agents remember and manage state across sessions.
* [Memory Systems for AI Agents][129] — Survey of memory architectures for agents.
* [Episodic Memory][130] — Storing and retrieving episode-specific memories.
* [Semantic Memory][131] — Storing and retrieving general knowledge.
* [Working Memory][132] — Managing short-term context during task execution.
* [Long-term Memory][133] — Persistent storage across sessions.
* [Memory Consolidation][134] — Consolidating memories over time.
* [Memory Retrieval][135] — Retrieving relevant memories for current tasks.
* [Memory Forgetting][136] — Forgetting outdated or irrelevant memories.

### Task Runners & Orchestration

Systems for executing and managing agent tasks.
* [Task Queues for Agents][137] — Using task queues to manage agent workloads.
* [Workflow Engines][138] — Workflow engines for agent orchestration.
* [Job Schedulers][139] — Scheduling agent jobs and tasks.
* [Distributed Execution][140] — Running agents across multiple machines.
* [Fault Tolerance][141] — Making agent systems resilient to failures.
* [Load Balancing][142] — Balancing agent workloads across resources.
* [Resource Management][143] — Managing compute resources for agents.
* [Scaling Strategies][144] — Scaling agent systems horizontally and vertically.

### Verification & CI Integration

Testing and verification systems for agent outputs.
* [Testing AI Agents][145] — Anthropic's guide on testing agent behavior.
* [Agent Evaluation Frameworks][146] — Frameworks for evaluating agent performance.
* [CI/CD for Agents][147] — Integrating agents into CI/CD pipelines.
* [Automated Testing][148] — Automated testing strategies for agents.
* [Regression Testing][149] — Detecting regressions in agent behavior.
* [Property-Based Testing][150] — Using property-based testing for agents.
* [Fuzz Testing][151] — Fuzz testing for agent robustness.
* [Security Testing][152] — Security testing for agent systems.

### Observability & Tracing

Monitoring and debugging agent behavior.
* [Observability for AI Agents][153] — Monitoring agent behavior and performance.
* [Distributed Tracing][154] — Tracing agent requests across systems.
* [Logging Best Practices][155] — Logging strategies for agent systems.
* [Metrics Collection][156] — Collecting metrics from agent operations.
* [Performance Monitoring][157] — Monitoring agent performance over time.
* [Error Tracking][158] — Tracking and analyzing agent errors.
* [Debugging Tools][159] — Tools for debugging agent behavior.
* [Visualization][160] — Visualizing agent operations and state.

### Debugging & Developer Experience

Tools and practices for developing and debugging agents.
* [Debugging AI Agents][161] — Strategies for debugging agent behavior.
* [Development Environments][162] — Setting up development environments for agents.
* [Testing Frameworks][163] — Testing frameworks for agent development.
* [IDE Integration][164] — Integrating agent development into IDEs.
* [Profiler Tools][165] — Profiling agent performance.
* [Interactive Debugging][166] — Interactive debugging tools for agents.
* [Error Analysis][167] — Analyzing agent errors systematically.
* [Playgrounds][168] — Interactive playgrounds for testing agents.

### Human-in-the-Loop

Integrating human oversight and collaboration.
* [Human-in-the-Loop Design][169] — Designing human oversight into agent systems.
* [Collaboration Patterns][170] — Patterns for human-agent collaboration.
* [Feedback Loops][171] — Designing feedback loops between humans and agents.
* [Approval Workflows][172] — Designing approval workflows for agent actions.
* [Intervention Mechanisms][173] — Mechanisms for human intervention.
* [Training Interfaces][174] — Interfaces for training agents with human feedback.
* [Monitoring Dashboards][175] — Dashboards for monitoring agent behavior.
* [Alert Systems][176] — Alert systems for agent anomalies.

## Reference Implementations

### Tutorials & Educational

Learning resources and tutorials for building agent harnesses.
* [Agent Engineering Tutorial][177] — Tutorial on building agent systems.
* [Harness Engineering Course][178] — Course on harness engineering principles.
* [Agent Development Workshop][179] — Workshop materials for agent development.
* [Practical Agent Building][180] — Practical guide to building agents.
* [Agent Patterns Library][181] — Library of agent design patterns.
* [Case Studies][182] — Case studies of agent deployments.
* [Best Practices Guide][183] — Best practices for agent development.
* [Common Pitfalls][184] — Common pitfalls to avoid in agent development.

### Generators & Meta-Harnesses

Tools that generate or manage other harnesses.
* [Agent Generators][185] — Tools for generating agent scaffolding.
* [Harness Templates][186] — Templates for agent harnesses.
* [Meta-Harness Frameworks][187] — Frameworks for building meta-harnesses.
* [Configuration Management][188] — Managing agent configurations.
* [Deployment Automation][189] — Automating agent deployment.
* [Testing Automation][190] — Automating agent testing.
* [Monitoring Automation][191] — Automating agent monitoring.
* [Maintenance Automation][192] — Automating agent maintenance.

### Demo Harnesses

Example implementations and demonstrations.
* [Demo Agent Repository][193] — Repository of demo agents.
* [Example Harnesses][194] — Collection of example harnesses.
* [Interactive Demos][195] — Interactive demos of agent systems.
* [Video Tutorials][196] — Video tutorials for agent development.
* [Live Examples][197] — Live examples of agent systems.
* [Code Samples][198] — Code samples for agent development.
* [Architecture Diagrams][199] — Architecture diagrams for agent systems.
* [Documentation Examples][200] — Documentation examples for agent projects.

### Adjacent Collections

Related awesome lists and resource collections.
* [Awesome AI Agents][201] — Curated list of AI agent resources.
* [Awesome LLM][202] — Curated list of LLM resources.
* [Awesome Prompt Engineering][203] — Curated list of prompt engineering resources.
* [Awesome RAG][204] — Curated list of RAG resources.
* [Awesome Machine Learning][205] — Curated list of ML resources.
* [Awesome Deep Learning][206] — Curated list of deep learning resources.
* [Awesome NLP][207] — Curated list of NLP resources.
* [Awesome Computer Vision][208] — Curated list of computer vision resources.

## Security, Sandbox & Permissions

Security architectures, sandboxing techniques, and permission systems.
* [Agent Security][209] — Security considerations for agent systems.
* [Sandboxing Techniques][210] — Techniques for sandboxing agent execution.
* [Permission Systems][211] — Permission systems for agent control.
* [Access Control][212] — Access control mechanisms for agents.
* [Audit Logging][213] — Audit logging for agent operations.
* [Secure Communication][214] — Secure communication for agent systems.
* [Data Privacy][215] — Data privacy considerations for agents.
* [Compliance][216] — Compliance requirements for agent systems.

## Evals & Verification

Evaluation frameworks, testing methodologies, and verification systems.
* [Agent Evaluation][217] — Frameworks for evaluating agent performance.
* [Benchmark Datasets][218] — Benchmark datasets for agent testing.
* [Evaluation Metrics][219] — Metrics for evaluating agent behavior.
* [Testing Methodologies][220] — Testing methodologies for agent systems.
* [Verification Systems][221] — Verification systems for agent outputs.
* [Quality Assurance][222] — Quality assurance for agent development.
* [Continuous Evaluation][223] — Continuous evaluation of agent systems.
* [A/B Testing][224] — A/B testing for agent improvements.

## Templates

Templates, checklists, and starter kits for agent development.
* [Agent Templates][225] — Templates for agent development.
* [Harness Templates][226] — Templates for agent harnesses.
* [Configuration Templates][227] — Configuration templates for agents.
* [Documentation Templates][228] — Documentation templates for agent projects.
* [Checklists][229] — Checklists for agent development.
* [Starter Kits][230] — Starter kits for agent projects.
* [Boilerplate Code][231] — Boilerplate code for agent development.
* [Project Templates][232] — Project templates for agent systems.

## Related Awesome Lists

Other curated lists that complement this collection.
* [Awesome AI Agents][233] — Comprehensive list of AI agent resources.
* [Awesome Prompt Engineering][234] — Comprehensive list of prompt engineering resources.
* [Awesome RAG][235] — Comprehensive list of RAG resources.
* [Awesome LLM][236] — Comprehensive list of LLM resources.
* [Awesome Machine Learning][237] — Comprehensive list of ML resources.

## Contributing

How to contribute to this awesome list.
* [Contribution Guidelines][238] — Guidelines for contributing to this list.
* [Pull Request Process][239] — Process for submitting pull requests.
* [Issue Reporting][240] — How to report issues.
* [Suggesting Resources][241] — How to suggest new resources.
* [Code of Conduct][242] — Code of conduct for contributors.
* [License][243] — License information for this project.
* [Acknowledgments][244] — Acknowledgments for contributors.

---

*Note: This content was fetched from zdoc.app and saved for offline reference. For the most up-to-date version, visit the source URL.*