# How to write a great agents.md: Lessons from over 2,500 repositories

**Source:** GitHub Blog  
**Date:** November 19, 2025 (Updated November 25, 2025)  
**Author:** Matt Nigh  
**URL:** https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-over-2500-repositories/  
**Fetched:** 2026-07-25  
**Purpose:** AGENTS.md creation for SovereignAI project

## Key Insights

### What works in practice: Lessons from 2,500+ repos

The analysis of over 2,500 `agents.md` files revealed a clear divide between the ones that fail and the ones that work. The successful agents aren't just vague helpers; they are specialists. Here's what the best-performing files do differently:

1. **Put commands early:** Put relevant executable commands in an early section: `npm test`, `npm run build`, `pytest -v`. Include flags and options, not just tool names. Your agent will reference these often.

2. **Code examples over explanations:** One real code snippet showing your style beats three paragraphs describing it. Show what good output looks like.

3. **Set clear boundaries:** Tell AI what it should never touch (e.g., secrets, vendor directories, production configs, or specific folders). "Never commit secrets" was the most common helpful constraint.

4. **Be specific about your stack:** Say "React 18 with TypeScript, Vite, and Tailwind CSS" not "React project." Include versions and key dependencies.

5. **Cover six core areas:** Hitting these areas puts you in the top tier: commands, testing, project structure, code style, git workflow, and boundaries.

### Example of a great agent.md file

```markdown
---
name: docs_agent
description: Expert technical writer for this project
---

You are an expert technical writer for this project.

## Your role
- You are fluent in Markdown and can read TypeScript code
- You write for a developer audience, focusing on clarity and practical examples
- Your task: read code from `src/` and generate or update documentation in `docs/`

## Project knowledge
- **Tech Stack:** React 18, TypeScript, Vite, Tailwind CSS
- **File Structure:**
  - `src/` – Application source code (you READ from here)
  - `docs/` – All documentation (you WRITE to here)
  - `tests/` – Unit, Integration, and Playwright tests

## Commands you can use
Build docs: `npm run docs:build` (checks for broken links)
Lint markdown: `npx markdownlint docs/` (validates your work)

## Documentation practices
Be concise, specific, and value dense
Write so that a new developer to this codebase can understand your writing, don’t assume your audience are experts in the topic/area you are writing about.

## Boundaries
- ✅ **Always do:** Write new files to `docs/`, follow the style examples, run markdownlint
- ⚠️ **Ask first:** Before modifying existing documents in a major way
- 🚫 **Never do:** Modify code in `src/`, edit config files, commit secrets
```

### Why this agent.md file works well

- **States a clear role:** Defines who the agent is (expert technical writer), what skills it has (Markdown, TypeScript), and what it does (read code, write docs).
- **Executable commands:** Gives AI tools it can run (`npm run docs:build` and `npx markdownlint docs/`). Commands come first.
- **Project knowledge:** Specifies tech stack with versions (React 18, TypeScript, Vite, Tailwind CSS) and exact file locations.
- **Real examples:** Shows what good output looks like with actual code. No abstract descriptions.
- **Three-tier boundaries:** Set clear rules using always do, ask first, never do. Prevents destructive mistakes.

### Six agents worth building

1. **@docs-agent** - Writes documentation, reads code and generates API docs, function references, and tutorials
2. **@test-agent** - Writes tests, can write to tests but should never remove a failing test
3. **@lint-agent** - Fixes code style and formatting but shouldn't change logic
4. **@api-agent** - Builds API endpoints, can modify API routes but must ask before touching database schemas
5. **@dev-deploy-agent** - Handles builds and deployments to local dev environment only

### Starter template

```markdown
---
name: your-agent-name
description: [One-sentence description of what this agent does]
---

You are an expert [technical writer/test engineer/security analyst] for this project.

## Persona
- You specialize in [writing documentation/creating tests/analyzing logs/building APIs]
- You understand [the codebase/test patterns/security risks] and translate that into [clear docs/comprehensive tests/actionable insights]
- Your output: [API documentation/unit tests/security reports] that [developers can understand/catch bugs early/prevent incidents]

## Project knowledge
- **Tech Stack:** [your technologies with versions]
- **File Structure:**
  - `src/` – [what's here]
  - `tests/` – [what's here]

## Tools you can use
- **Build:** `npm run build` (compiles TypeScript, outputs to dist/)
- **Test:** `npm test` (runs Jest, must pass before commits)
- **Lint:** `npm run lint --fix` (auto-fixes ESLint errors)

## Standards

Follow these rules for all code you write:

**Naming conventions:**
- Functions: camelCase (`getUserData`, `calculateTotal`)
- Classes: PascalCase (`UserService`, `DataController`)
- Constants: UPPER_SNAKE_CASE (`API_KEY`, `MAX_RETRIES`)

**Code style example:**
```typescript
// ✅ Good - descriptive names, proper error handling
async function fetchUserById(id: string): Promise<User> {
  if (!id) throw new Error('User ID required');

  const response = await api.get(`/users/${id}`);
  return response.data;
}

// ❌ Bad - vague names, no error handling
async function get(x) {
  return await api.get('/users/' + x).data;
}
```

## Boundaries
- ✅ **Always:** Write to `src/` and `tests/`, run tests before commits, follow naming conventions
- ⚠️ **Ask first:** Database schema changes, adding dependencies, modifying CI/CD config
- 🚫 **Never:** Commit secrets or API keys, edit `node_modules/` or `vendor/`
```

### Key takeaways

Building an effective custom agent isn't about writing a vague prompt; it's about providing a specific persona and clear instructions.

The analysis shows that the best agents are given a clear persona and, most importantly, a detailed operating manual. This manual must include executable commands, concrete code examples for styling, explicit boundaries (like files to never touch), and specifics about your tech stack.

When creating your own agents.md cover the six core areas: Commands, testing, project structure, code style, git workflow, and boundaries. Start simple. Test it. Add detail when your agent makes mistakes. The best agent files grow through iteration, not upfront planning.
