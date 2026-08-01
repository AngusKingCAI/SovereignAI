# Improving Deep Agents with Harness Engineering

**Source:** https://www.langchain.com/blog/improving-deep-agents-with-harness-engineering

**Description:** This article covers how LangChain improved their coding agent from Top 30 to Top 5 on Terminal Bench 2.0 using harness engineering techniques. It discusses system prompts, tools, middleware, self-verification, context injection, and reasoning compute optimization.

---

# Web Content from https://www.langchain.com/blog/improving-deep-agents-with-harness-engineering

[
][1]
Products
[
LangSmith Platform
][2]
Agent Improvement
[
Engine
Improve agents autonomously
][3][
Observability
See exactly what your agents are doing
][4][
Evaluation
Score and improve agent performance
][5]
Agent Infrastructure
[
Deployment
Ship and scale agents in production
][6][
Sandboxes
Run agent-generated code safely
][7][
LLM Gateway
Control agent model calls
][8]
No-Code Agents
[
Fleet
Agents for the whole company
][9]
Open Source Frameworks
[
deepagents
Build long-running agents for complex tasks
][10][
langgraph
Build reliable agents with low-level control
][11][
langchain
Quick start agents with any model provider
][12]
Learn
Resources
[
Blog
][13][
Customer Stories
][14][
Guides
][15][
Max Agency
][16]
How-To
[
LangChain Academy
][17][
YouTube
][18][
Documentation
][19]
Community
[
LangSmith for Startups
][20][
Meetups
][21][
Community
][22]
[Docs][23]
Company
[
About
][24][
Careers
][25][
Partners
][26][
Events
][27]
[Pricing][28]
[
Try LangSmith
][29]
[
Get a demo
][30]
[
Try LangSmith
][31]
[
Get a demo
][32]
Deep Agents
Observability & Evals
Agent Architecture

# Improving Deep Agents with harness engineering

Vivek Trivedy
February 17, 2026
8
min
[
Go back to blog
][33]
[
Create agents
][34]
Share
[
][35][
][36][
][37]

TLDR: Our coding agent went from Top 30 to Top 5 on [Terminal Bench 2.0][38]. We only changed the
harness. Here's our approach to harness engineering (teaser: self-verification & tracing help a
lot).

## The Goal of Harness Engineering

The goal of a harness is to mold the inherently spiky intelligence of a model for tasks we care
about. **Harness Engineering** is about systems, you're building tooling around the model to
optimize goals like task performance, token efficiency, latency, etc. Design decisions include the
system prompt, tool choice, and execution flow.

But how should you change the harness to improve your agent?

At LangChain, we use [Traces][39] to understand agent failure modes at scale. Models today are
largely black-boxes, their inner mechanisms are hard to interpret. But we can see their inputs and
outputs in text space which we then use in our improvement loops.

We used a simple recipe to iteratively improve [deepagents-cli][40] (our coding agent) `13.7 points`
from `52.8` to `66.5` on Terminal Bench 2.0. We only tweaked the harness and kept the model fixed,
`gpt-5.2-codex`.

## Experiment Setup & The Knobs on a Harness

We used [Terminal Bench 2.0][41], a now standard benchmark to evaluate agentic coding. It has 89
tasks across domains like machine learning, debugging, and biology. We use [Harbor][42] to
orchestrate the runs. It spins up sandboxes ([Daytona][43]), interacts with our agent loop, and runs
verification + scoring.

Every agent action is stored in [LangSmith][44]. It also includes metrics like latency, token
counts, and costs.

### **The Knobs we can Turn**

An agent harness has a lot of knobs: system prompts, tools, hooks/middleware, skills, sub-agent
delegation, memory systems, and more. We deliberately compress the optimization space and focus on
three: **System Prompt, Tools,** and [**Middleware**][45] (our term for hooks around model and tool
calls).

We start with a default prompt and standard tools+middleware. This scores 52.8% with GPT-5.2-Codex.
A solid score, just outside the Top 30 of the leaderboard today, but room to grow.

### **The Trace Analyzer Skill**

We wanted trace analysis to be repeatable so we made it into an Agent Skill. This serves as our
recipe to **analyze errors across runs and make improvements to the harness**. The flow is:
1. Fetch experiment traces from LangSmith
2. Spawn parallel error analysis agents → main agent synthesizes findings + suggestions
3. Aggregate feedback and make targeted changes to the harness.

This works similarly to [boosting][46] which focuses on mistakes from previous runs. A human can be
pretty helpful in Step 3 (though not required) to verify and discuss proposed changes. Changes that
overfit to a task are bad for generalization and can lead to regressions in other Tasks.

Automated trace analysis saves hours of time and made it easy to quickly try experiments. We'll be
publishing this skill soon, we're currently testing it for prompt optimization generally.

## What Actually Improved Agent Performance

Automated Trace analysis allowed us to [debug where agents were going wrong][47]. Issues included
reasoning errors, not following task instructions, missing testing and verification, running out of
time, etc. We go into these improvements in more details in the sections below.

### Build & Self-Verify

Today's models are exceptional self-improvement machines.

**Self-verification allows agents to self-improve via feedback within a run**. However, they don't
have a natural tendency to enter this **build-verify loop.**

The most common failure pattern was that the agent wrote a solution, re-read its own code, confirmed
it looks ok, and stopped. Testing is a key part of autonomous agentic coding. It helps test for
overall correctness and simultaneously gives agents signal to hill-climb against.

We added guidance to the system prompt on how to approach problem solving.
1. **Planning & Discovery:** Read the task, scan the codebase, and build an initial plan based on
   the task specification and how to verify the solution.
2. **Build:** Implement the plan with verification in mind. Build tests, if they don't exist and
   test both happy paths and edge cases.
3. **Verify:** Run tests, read the full output, compare against what was asked (not against your own
   code).
4. **Fix:** Analyze any errors, revisit the original spec, and fix issues.

We really focus on testing because it powers the changes in every iteration. We found that alongside
prompting, deterministic context injection helps agents verify their work. We use a
`PreCompletionChecklistMiddleware` that intercepts the agent before it exits and reminds it to run a
verification pass against the Task spec. This is similar to a [Ralph Wiggum Loop][48] where a hook
forces the agent to continue executing on exit, we use this for verification.

### Giving Agents Context about their Environment

Part of harness engineering is **building a good delivery mechanism for context engineering.**
Terminal Bench tasks come with directory structures, built-in tooling, and strict timeouts.
1. **Directory Context & Tooling:** A `LocalContextMiddleware` runs on agent start to map the `cwd`
   and other parent+children directories. We run `bash` commands to find tools like `Python`
   installations. Context discovery and search are error prone, so injecting context reduces this
   error surface and helps **onboard the agent into its environment.**
2. **Teaching Agents to Write Testable Code:** Agents don't know how their code needs to be
   testable. We add prompting say their work will be measured against programatic tests, similar to
   when committing code. For example, Task specs that mention file paths should be followed exactly
   so the solutions works in an automated scoring step. Prompting that stresses edge-cases helps the
   agent avoid only checking "happy path" cases. Forcing models to conform to testing standards is a
   powerful strategy to avoid "slop buildup" over time.
3. **Time Budgeting:** We inject time budget warnings to nudge the agent to finish work and shift to
   verification. Agents are famously bad at time estimation so this heuristic helps in this
   environment. Real world coding usually doesn't have strict time limits, but without adding any
   knowledge of constraints, agents won't work within time bounds.

The more that agents know about their environment, constraints, and evaluation criteria, the better
they can autonomously self-direct their work.

**The purpose of the harness engineer: prepare and deliver context so agents can autonomously
complete work.**

### Encouraging Agents to Step Back & Reconsider Plans

Agents can be myopic once they've decided on a plan which results in "doom loops" that make small
variations to the same broken approach (10+ times in some traces).

We use a `LoopDetectionMiddleware` that tracks per-file edit counts via tool call hooks. It adds
context like "…consider reconsidering your approach" after `N` edits to the same file. This can help
agents recover from doom loops, though the model can continue down the same path if it thinks it's
correct.

Important note. This is a design heuristic that engineers around today's perceived model issues. As
models improve, these guardrails will likely be unnecessary, but today helps agents execute
correctly and autonomously.

### Choosing How Much Compute to Spend on Reasoning

Reasoning models can run autonomously for hours so we have to decide how much compute to spend on
every subtask. You can use the max reasoning budget on every task, but most work can benefit from
optimizing reasoning compute spend.

Terminal Bench timeout limits create a tradeoff. More reasoning helps agents evaluate each step, but
can burn over `2x` more tokens/time. `gpt-5.2-codex` has 4 reasoning modes, `low`, `medium`, `high`,
and `xhigh`.

We found that reasoning helps with planning to fully understand the problem, some Terminal Bench
tasks are very difficult. A good plan helps get to a working solution more quickly.

Later stage verification also benefits from more reasoning to catch mistakes and get a solution
submitted. As a heuristic, we choose a xhigh-high-xhigh "**reasoning sandwich**" as a baseline.

*Spending more reasoning compute on planning and verification*

Running only at `xhigh` scored poorly at `53.9%` due to agent timeouts compared to `63.6%` at
`high`. There weren't large differences in trial runs across reasoning budget splits so we stuck
with our approach which pushed the score to `66.5%`.

The natural question is what if we made it more granular and smarter, maybe an agent that can decide
its own reasoning budget based on task difficulty? We're exploring this direction.

## Lessons Learned

### Harness Engineering is Systems Engineering

Building a good harness is about building systems that optimize model performance. It's not just
about the model, it's about the entire system around it.

### Self-Verification is Critical

Models are great at self-improvement when given the right feedback loops. Testing and verification
are key to unlocking this capability.

### Context Engineering is Part of Harness Engineering

Agents need to know about their environment, constraints, and evaluation criteria to perform well.
The harness engineer's job is to prepare and deliver this context effectively.

### Traces are Your Best Friend

Understanding agent failure modes at scale is crucial for improvement. Traces provide the visibility
needed to make targeted improvements.

### Design Heuristics Help Today but May Not Tomorrow

Some of our improvements are design heuristics that work around current model limitations. As models
improve, these may become unnecessary, but they're valuable today.

## Conclusion

By focusing on harness engineering - system prompts, tools, middleware, and context delivery - we
improved our coding agent's performance significantly on Terminal Bench 2.0. The key insights were
self-verification, context injection, and smart reasoning compute allocation. This demonstrates that
harness engineering is a powerful approach to improving agent performance without changing the
underlying model.
