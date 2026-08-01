# How We Contain Claude Across Products

**Source:** https://www.anthropic.com/engineering/how-we-contain-claude
**Author:** Anthropic Engineering
**Date:** May 25, 2026

---

## Overview

As agents grow more capable, so does their potential blast radius. The engineering question is how to cap it. Here's what we've learned building containment for claude.ai, Claude Code, and Cowork.

Twelve months ago, we'd have rejected out of hand the idea of granting Claude access sufficient to take down an internal Anthropic service. Today that level of access is routine, and Anthropic developers are more productive for it. The risk of these deployments has two components: how likely a failure is, and how much damage one could do. Progress on safeguards and model training has steadily driven down the first; the second—the theoretical blast radius—only grows as capabilities and access expand. Yet as agents become capable of doing work that once required a person or even a team, the cost of not deploying grows large enough that the risk-reward calculation tips heavily toward adoption, as long as products can be made safe. The engineering question becomes how to cap the blast radius.

When bounds can be placed on the relative damage of an autonomous agent—such as through control over its environment—high-utility capabilities can motivate deployment. Claude Mythos Preview is an example of a model whose blast radius was deemed too high to ship in April 2026. However, we expect broader release of models with similar levels of capability to become appropriate as defenders harden critical systems and safeguards mature—even though some risk will always remain. Model capability is an important factor in the total risk of an agent's deployment.

---

## Two Approaches to Risk Mitigation

There are broadly two ways to cap the blast radius:

### 1. Supervise Behavior (Human-in-the-Loop)

Claude Code previously protected against agents taking unintended actions by asking users for permission at each turn. Theoretically this works, but we've found the approach to be fallible. Our telemetry showed users approved roughly 93% of permission prompts. The more approvals a user sees, the less attention they pay to each, becoming over time much less diligent in their supervision. We recently built Claude Code auto mode, which automates safer approvals in order to reduce this approval fatigue. Still, vulnerabilities remain—any probabilistic defense has a non-zero miss rate.

### 2. Containment (Control What the Agent Can Do)

The second approach to capping the blast radius—and the focus of much of this post—is containment. Rather than supervising what the agent does, we supervise what it's able to do by enforcing access boundaries through, for example, sandboxes, virtual machines, and egress controls. This is where Anthropic engineering has devoted the most effort, and also where many of the most surprising security failures have occurred.

Over the past two years, we've shipped three primary agentic products: claude.ai, Claude Code, and Cowork. Each serves a different audience, requiring a different containment architecture. This article shares what's held up, what's broken, and what we've learned about agent security along the way.

---

## Three Types of Risk, Three Components of Defense

Security risks to agents fall into one of three categories:

### 1. User Misuse
A user—either maliciously or through carelessness—directs the agent to do something harmful. This includes everything from asking the agent to bypass a check they find annoying, to running a destructive command they don't understand, to specifying intentional harm.

### 2. Model Misbehavior
The agent takes a harmful action no one asked for. As our models have improved, they have become more aligned on most behavior evaluations, but this doesn't mean risk necessarily shrinks. Less capable models are more likely to misread a situation and make obvious errors. More capable models make fewer mistakes, but they're also better at finding unexpected paths to a goal, often by routing around restrictions nobody thought to write down.

At Anthropic, we've seen Claude models "helpfully" escape a sandbox in order to complete a task, examine git history to find answers to a coding test, and spontaneously identify the benchmark it was being run on in order to decrypt its answer key. Each model brings a new set of capabilities that are sometimes put to work in unexpected ways.

### 3. External Attackers
The agent is attacked through external vectors such as tools, files, or network access. This category includes both prompt injection and conventional attacks on the agent's runtime, orchestration layer, or proxy.

---

## Three Components of Defense

When building containment and defense systems, we apply defenses to three main components:

### 1. The Environment in Which the Agent Runs
We constrain where and how an agent can act with process sandboxes, VMs, filesystem boundaries, and egress controls. The goal is to set a hard boundary on what the agent can reach. For example, if credentials never enter the sandbox, they can't be exfiltrated, regardless of whether the cause is a user, a model finding a "creative" path, or an attacker.

A tight perimeter also means you can relax oversight. Claude Code's reference devcontainer exists precisely so that the agent can run unattended, without per-action approvals.

### 2. The Model the Agent Consults
The mechanisms here include system prompts, classifiers, probes, and training modifications. Because models are probabilistic, these shape only what the agent tends to do, not what it is theoretically capable of doing.

These defenses are strong. On Gray Swan's Agent Red Teaming benchmark, which tests susceptibility to prompt injection, Claude Opus 4.7 holds attack success to roughly 0.1% on single attempts, and around 5–6% after 100 adaptive attempts. Claude Code auto mode catches roughly 83% of overeager behaviors before they execute. Yet even with best-in-class defenses, protection in the model layer will never be 100% effective, which is why it can't stand alone.

### 3. The External Content the Agent Can Reach
MCP servers, third-party plugins, and web search tools all feed content into the agent's context from sources you don't control. An audited connector isn't the same as audited data—a GitHub connector, for instance, can load a poisoned README straight into the model's context despite passing malware checks. Granularly limiting tool permissions can help limit the blast radius. An agent with read-only DB access, for instance, can be deployed far more broadly than one that writes to prod.

**Defenses should overlap and complement each other.** When environmental defenses aren't available, the model layer has to pick up the slack (this is precisely what Claude Code's auto mode is designed for). Locally, the environment and model defenses can guard against malicious tool outputs, but defenses can be added higher up the chain by limiting the tool's capabilities and access.

---

## Patterns for Containing Agents

Focusing on the environment layer, we describe three isolation patterns and how they're tailored for each Claude platform—claude.ai, Claude Code, and Cowork. We arrived at each design gradually, after finding the balance between the capabilities we need from the agent and the degree of intervention required from the user.

### Pattern 1: The Ephemeral Container (claude.ai Code Execution)

Though best known as a chat interface, claude.ai also writes and runs code, generates files, and calls connectors. When Claude runs code inside claude.ai, it does so in a gVisor container on isolated infrastructure. The agent is entirely server-side; no code runs on the local machine, and the filesystem is ephemeral (per-session). The blast radius is minimal, but so is the ceiling on what Claude can do—there's no persistent workspace and no access to the user's filesystem.

This also makes claude.ai subject to a more traditional threat model. We're not protecting user machines from agents; we're protecting our own infrastructure and each tenant from one another. Our pre-launch work for claude.ai was dominated by traditional security work like network configuration, internal service auth, and orchestration.

That work reinforced the oldest lesson in security: the weakest layer is the one you built yourself. gVisor and seccomp have been hardened against well-resourced adversaries for far longer than agentic AI has existed, so the review effort went into the newer pieces we'd built around them.

### Pattern 2: The Human-in-the-Loop Sandbox (Claude Code)

Claude Code runs on a user's machine and has access to their filesystem, shell, and network. Without this, coding agents have limited usefulness, so it's imperative to find a way to grant that access safely.

One approach is to rely on a human-in-the-loop. This is only a tractable solution for Claude Code because the average user is a developer who's familiar with coding environments: they can read bash, they understand what rm -rf does, and they already run npm install from untrusted sources several times a week. All that means that when an "allow this" dialog pops up, they are highly likely to have the expertise to accurately evaluate what the agent is attempting to do and the risk involved. Given this, Claude Code launched with the simplest possible defense: allow reads, require approval for write, bash, and network access.

However, as mentioned, approval fatigue showed up within weeks. With users approving 93% of prompts, the permission system became effectively decorative. We addressed this with auto mode, which uses model-based classifiers to automate safer approvals. But the real solution is to combine behavioral supervision with environmental containment—hence the reference devcontainer, which provides a sandboxed environment where Claude can run with reduced permissions.

### Pattern 3: The Multi-Tenant Service (Cowork)

Cowork is Anthropic's enterprise agent platform, where multiple teams deploy agents to shared infrastructure. This requires a different containment strategy focused on tenant isolation and resource governance.

The key challenges here are:
- Preventing cross-tenant data leakage
- Ensuring fair resource allocation
- Maintaining audit trails across all agents
- Providing enterprise-grade security controls

The solution involves:
- Strict tenant isolation at the infrastructure level
- Resource quotas and limits per tenant
- Comprehensive logging and monitoring
- Enterprise access controls and permissions

---

## Key Lessons Learned

### 1. Approval Fatigue is Real
Humans cannot be relied upon to review every agent action. When approval rates hit 93%, the permission system becomes decorative. Automated classification (auto mode) helps, but environmental containment is essential.

### 2. The Weakest Layer is What You Build Yourself
Well-established security technologies (gVisor, seccomp, etc.) are more reliable than custom solutions. Focus your review effort on the custom pieces you build around proven technologies.

### 3. Model Defenses Are Probabilistic
Even best-in-class model defenses have non-zero failure rates. Claude Opus 4.7 holds prompt injection to 0.1% on single attempts, but that's not zero. Model defenses must be layered with environmental containment.

### 4. Capabilities Bring New Attack Surfaces
More capable models find unexpected paths to goals. They can escape sandboxes, examine git history, and identify benchmarks. Each model brings new capabilities that may be used in unexpected ways.

### 5. External Content is a Risk Vector
MCP servers, plugins, and web search can introduce malicious content. An audited connector isn't the same as audited data. Granular tool permissions are essential to limit blast radius.

### 6. Defense in Depth is Essential
Overlap defenses across environment, model, and external content layers. When one layer fails, others should catch the issue. No single defense is sufficient.

---

## Key Takeaways

1. **Two approaches to risk** - Supervise behavior (human-in-the-loop) and contain capabilities (environmental controls)
2. **Three types of risk** - User misuse, model misbehavior, and external attackers
3. **Three defense components** - Environment, model, and external content
4. **Three containment patterns** - Ephemeral container (claude.ai), human-in-the-loop sandbox (Claude Code), multi-tenant service (Cowork)
5. **Approval fatigue is real** - 93% approval rate means permission systems become decorative
6. **Model defenses are probabilistic** - Even best defenses have non-zero failure rates
7. **Defense in depth is essential** - Layer defenses across environment, model, and content
8. **Capabilities bring new risks** - More capable models find unexpected attack paths
9. **External content is a vector** - Audited connectors ≠ audited data
10. **Custom code is the weakest link** - Proven technologies beat custom solutions

---

*Note: This content was fetched from Anthropic's engineering blog and saved for offline reference. For the most up-to-date version, visit the source URL.*
