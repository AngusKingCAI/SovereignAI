# Harness Engineering for Coding Agent Users

**Source:** https://martinfowler.com/articles/exploring-gen-ai/harness-engineering.html
**Author:** Birgitta Böckeler, Distinguished Engineer and AI-assisted delivery expert at Thoughtworks
**Date:** April 2, 2026

---

## Overview

To let coding agents work with less supervision, we need ways to increase our confidence in their result. As software engineers, we have a natural trust barrier with AI-generated code - LLMs are non-deterministic, they don't know our context, and they don't really understand the code, they think in tokens. This article explores a mental model that brings together emerging concepts from context and harness engineering to build that trust.

---

## The Harness Concept

The term harness has emerged as a shorthand to mean everything in an AI agent except the model itself - **Agent = Model + Harness**. That is a very wide definition, and therefore worth narrowing down for common categories of agents. In the bounded context of using a coding agent, part of the harness is already built in (e.g. via the system prompt, or the chosen code retrieval mechanism, or even a sophisticated orchestration system). But coding agents also provide us, their users, with many features to build an outer harness specifically for our use case and system.

### Three-Layer Model

```
┌─────────────────────────────────────┐
│   User Harness (Outer Harness)      │
│   - Guides (feedforward controls)   │
│   - Sensors (feedback controls)      │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│   Builder Harness (Inner Harness)   │
│   - System prompt                   │
│   - Code retrieval mechanism        │
│   - Orchestration system            │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│   Model (LLM)                        │
│   - The core reasoning engine       │
└─────────────────────────────────────┘
```

A well-built outer harness serves two goals:
1. It increases the probability that the agent gets it right in the first place
2. It provides a feedback loop that self-corrects as many issues as possible before they even reach human eyes

Ultimately it should reduce the review toil and increase the system quality, all with the added benefit of fewer wasted tokens along the way.

---

## Feedforward and Feedback

To harness a coding agent we both anticipate unwanted outputs and try to prevent them, and we put sensors in place to allow the agent to self-correct:

### Guides (Feedforward Controls)
- Anticipate the agent's behavior and aim to steer it before it acts
- Increase the probability that the agent creates good results in the first attempt
- Examples: coding conventions, project structure rules, architectural principles

### Sensors (Feedback Controls)
- Observe after the agent acts and help it self-correct
- Particularly powerful when they produce signals that are optimized for LLM consumption
- Examples: custom linter messages that include instructions for self-correction (a positive kind of prompt injection)

Separately, you get either an agent that keeps repeating the same mistakes (feedback-only) or an agent that encodes rules but never finds out whether they worked (feedforward-only). Both are needed for effective harness engineering.

---

## Computational vs Inferential

There are two execution types of guides and sensors:

### Computational
- Deterministic and fast, run by the CPU
- Tests, linters, type checkers, structural analysis
- Run in milliseconds to seconds; results are reliable
- Computational guides increase the probability of good results with deterministic tooling
- Computational sensors are cheap and fast enough to run on every change, alongside the agent

### Inferential
- Semantic analysis, AI code review, "LLM as judge"
- Typically run by a GPU or NPU
- Slower and more expensive; results are more non-deterministic
- Allow us to both provide rich guidance, and add additional semantic judgment
- Despite their non-determinism, inferential sensors can particularly increase our trust when used with a strong model

### Examples Table

| Control Type | Direction | Computational/Inferential | Example Implementations |
|--------------|-----------|--------------------------|------------------------|
| Coding conventions | Feedforward | Inferential | AGENTS.md, Skills |
| Instructions how to bootstrap a new project | Feedforward | Both | Skill with instructions and a bootstrap script |
| Code mods | Feedforward | Computational | A tool with access to OpenRewrite recipes |
| Structural tests | Feedback | Computational | A pre-commit (or coding agent) hook running ArchUnit tests that check for violations of module boundaries |
| Instructions how to review code changes | Feedback | Inferential | Skills |
| Static analysis | Feedback | Computational | A pre-commit hook running ESLint or similar |
| Review agents | Feedback | Inferential | An agent that reviews code changes for conformance to coding conventions |
| Logs | Feedback | Computational | Application logs that the agent can query |

---

## The Steering Loop

The harness creates a steering loop where:

1. **Guides** provide feedforward control - they steer the agent before it acts
2. **Agent** takes action based on the guides
3. **Sensors** provide feedback - they observe the results and signal issues
4. **Self-correction** - the agent uses sensor feedback to correct its own mistakes
5. **Iteration** - the loop continues until quality thresholds are met

This loop is powered by both computational and inferential controls, providing a robust system for guiding and correcting agent behavior.

---

## Timing: Keep Quality Left

A key principle in harness engineering is to "keep quality left" - that is, to catch and fix issues as early as possible in the development process:

1. **Pre-generation** - Guides steer the agent to produce good code in the first attempt
2. **During generation** - Sensors catch issues as they're being created
3. **Post-generation** - Additional validation before code reaches human review
4. **Human review** - Final quality gate, but with reduced toil due to earlier quality checks

By keeping quality left, we:
- Reduce wasted tokens on bad code
- Decrease human review burden
- Increase overall system quality
- Enable faster iteration cycles

---

## Regulation Categories

Harness controls can be categorized into three main types:

### 1. Maintainability Harness

Focuses on code maintainability and long-term health:
- Coding conventions and style guides
- Code structure and organization rules
- Documentation requirements
- Test coverage standards

### 2. Architecture Fitness Harness

Focuses on architectural integrity and design quality:
- Module boundary enforcement
- Dependency rules and constraints
- Architectural pattern compliance
- System design principles

### 3. Behavior Harness

Focuses on functional correctness and runtime behavior:
- Functional requirements
- Performance constraints
- Security rules
- Error handling standards

Each category requires different types of guides and sensors, and may use different combinations of computational and inferential controls.

---

## Harnessability

**Harnessability** is the degree to which a system, technology, or architecture can be effectively harnessed by AI agents. When making technology and architecture decisions, harnessability should become a first-class criterion alongside performance, maintainability, and other traditional concerns.

Factors that affect harnessability:
- **Explicitness** - How well are rules and constraints documented?
- **Mechanical verifiability** - Can rules be checked automatically?
- **Determinism** - How predictable is the system behavior?
- **Observability** - How easy is it to understand what's happening?
- **Modifiability** - How easy is it to make controlled changes?

When evaluating technologies for use with AI agents, consider:
- Can agents understand the rules?
- Can agents verify compliance?
- Can agents make changes safely?
- Can agents recover from errors?

---

## Harness Templates

As teams develop harness patterns, they can create reusable harness templates that encode best practices for specific types of projects or technologies. These templates can include:

- Standard guide configurations (AGENTS.md templates, skill definitions)
- Common sensor setups (linter configurations, test suites)
- Validation pipelines (CI/CD configurations)
- Feedback mechanisms (review agent prompts)

Templates enable:
- Faster onboarding for new projects
- Consistency across teams
- Knowledge sharing and reuse
- Continuous improvement of harness patterns

---

## The Role of the Human

Even with sophisticated harnesses, humans play crucial roles:

### Harness Engineer
- Designs and maintains the harness system
- Monitors harness effectiveness
- Updates guides and sensors as the system evolves
- Balances automation with appropriate human oversight

### System Architect
- Makes architecture decisions with harnessability in mind
- Designs systems that are amenable to agent operation
- Provides clear architectural constraints and guidelines

### Domain Expert
- Provides domain-specific knowledge and constraints
- Reviews and validates agent decisions in critical areas
- Handles edge cases and exceptions

The "humans on the loop" framing is key: harness engineers who design and maintain agent environments rather than inspecting individual outputs. This is the clearest conceptual map of what the discipline actually entails.

---

## A Starting Point - and Open Questions

### Getting Started
A practical starting point for harness engineering:
1. Start with computational guides (coding conventions, structure rules)
2. Add computational sensors (linters, tests, type checkers)
3. Gradually introduce inferential controls where they add value
4. Iterate based on what works for your specific context

### Open Questions
The field is still evolving, and many questions remain:
- How do we measure harness effectiveness?
- What's the right balance of computational vs inferential controls?
- How do we prevent harness brittleness as systems evolve?
- How do we scale harness engineering across large organizations?
- What are the anti-patterns to avoid?

---

## Key Takeaways

1. **Agent = Model + Harness** - The harness is everything except the model itself
2. **Two types of controls** - Feedforward (guides) and feedback (sensors), both needed
3. **Two execution modes** - Computational (fast, deterministic) and inferential (semantic, expensive)
4. **Keep quality left** - Catch issues early in the process
5. **Three regulation categories** - Maintainability, architecture fitness, and behavior
6. **Harnessability matters** - Make it a first-class criterion in technology decisions
7. **Humans are harness engineers** - Design environments, not inspect outputs

---

## Relationship to Context Engineering

Harness engineering is closely related to context engineering but focuses on different aspects:

- **Context engineering** focuses on what information the agent has access to and how it's structured
- **Harness engineering** focuses on how the agent is guided and controlled

Both are essential for reliable agent operation, and they complement each other. Good context engineering provides the agent with the right information; good harness engineering ensures the agent uses that information effectively.

---

*Note: This content was fetched from Martin Fowler's bliki and saved for offline reference. For the most up-to-date version, visit the source URL.*
