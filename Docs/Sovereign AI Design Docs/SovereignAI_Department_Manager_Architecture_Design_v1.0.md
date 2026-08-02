# SovereignAI -- Department Manager Architecture Design Document v1.0

**Status**: Draft -- approved for implementation  
**Date**: 2026-07-03  
**Author**: Architect  
**Depends on**: `../PRINCIPLES.md`, `../AGENTS.md`, `../DECISIONS.md`, `../AI_HANDOFF.md`, `SovereignAI_Skill_Agent_System_Design_v1.0.md`, `SovereignAI_LLM_Function_Calling_Design_v1.0.md`, `SovereignAI_Diff_Based_Editing_Design_v1.0.md`, `SovereignAI_Worker_Spawning_Design_v1.0.md`, `SovereignAI_Codebase_Indexing_Design_v1.0.md`

---

## 1. Context

**Gap**: #7 -- Department Managers  
**Problem**: The Orchestrator dispatches tasks to departments, but no department managers exist to receive them. The Coding Department spec describes a 6-stage pipeline, but we need a minimal viable manager that composes with the ratified infrastructure (ReAct loop, worker spawning, codebase indexing, diff editing).  
**Scope**: How department managers structure task execution without violating existing design decisions.

---

## 2. Design Decision

**DD-21.7.1**: Department manager architecture (Proposed, P5/AR1/P13-aligned): Manager is a deterministic pipeline. Three stages: (1) build context via `codebase_index.rank_for_task()` (deterministic), (2) spawn ONE ReAct Worker with task + context (Worker runs ReAct loop per DD-21.3.1, uses tools per DD-21.9.1), (3) validate result deterministically (e.g. run tests). Zero LLM calls at Manager level. All intelligence in the ReAct Worker's loop.

---

## 3. Abstraction Levels

Per design doc Section 1 and AR1 (Orchestrator → Manager → Worker chain):

| Level | Role | LLM? | ReAct? | Example |
|-------|------|------|--------|---------|
| **Manager** | Deterministic pipeline orchestrator | No | No | Build context, spawn worker, validate |
| **Worker** | ReAct agent | Yes | Yes | One per task. Uses tools via SkillRunner. |
| **Tool/Skill** | Single capability | No | No | file_read, file_edit, test_run |

**Critical distinction**: "Worker" means ReAct loop. Not "any code that does work." A deterministic file reader is a tool call, not a Worker.

---

## 4. Manager Pipeline

```python
class CodingManager:
    def execute_task(self, task: CodingTask) -> CodingDeliverable:
        # Stage 1: Build context (deterministic)
        context = self._codebase_index.rank_for_task(
            current_files=[],
            token_budget=1024
        )

        # Stage 2: Spawn ReAct Worker (one per task)
        worker_result = self._worker_pool.submit(
            task_id=task.id,
            worker=self._react_worker,
            task=task.with_context(context),
        ).result(timeout=task.timeout_seconds)

        # Stage 3: Validate deterministically
        if worker_result.success:
            test_result = self._test_runner.run(task.test_command)
            if not test_result.passed:
                return CodingDeliverable(
                    success=False,
                    worker_output=worker_result,
                    validation_failure=test_result,
                )

        return CodingDeliverable(
            success=worker_result.success and test_result.passed,
            worker_output=worker_result,
        )
```

---

## 5. Why Not C (Hybrid with PlanWorker/EditWorker Split)

### 5.1 Worker/Tool Confusion

C's pipeline: `ReadWorker → PlanWorker → EditWorker → TestWorker`

But per design doc Section 1:
- **Manager**: "plans work, assigns workers, no ReAct"
- **Worker**: "ReAct Loop" — explicitly the ReAct agent

By that definition:
- `ReadWorker` is NOT a Worker — it's a tool call (`file_read` skill)
- `PlanWorker` is NOT a Worker — it's an LLM call (the Manager's job per design doc)
- `EditWorker` IS a Worker (ReAct loop using `file_edit`)
- `TestWorker` is NOT a Worker — it's a tool call (test runner skill)

C conflates three abstraction levels. If `ReadWorker` is implemented as a ReAct Worker, it gets an LLM call to "decide" to read a file. That's an LLM call to do what deterministic code does for free. Token waste, latency waste, P5 violation.

### 5.2 Reintroduces DD-21.9.1's Drift Problem

DD-21.9.1 (ratified): Rejected line-range replacement because multi-step edits cause line drift. The fix was search/replace (A+) — content-based, self-locating.

C's `PlanWorker → EditWorker` split has the same drift at a higher level:
- `PlanWorker` emits plan: "edit auth.py, then edit utils.py"
- `EditWorker` executes edit 1 — auth.py changes
- `EditWorker` executes edit 2 — but plan was based on pre-edit-1 state
- If edit 1 invalidated edit 2's assumptions, edit 2 fails

The ReAct loop avoids this: think → act → observe → think. After each action, the model re-plans based on observed reality. No stale plan.

### 5.3 Token Efficiency

| Approach | LLM Calls | Notes |
|----------|-----------|-------|
| C | 2+ | PlanWorker (plan) + EditWorker (execute) |
| F | 1 | ReAct loop plans and executes in one stream |

---

## 6. Why Not Other Options

### 6.1 A -- Manager as LLM-Powered Planner
- **Why rejected**: P5 violation. Speculative LLM use when ReAct plans implicitly. Token-expensive, non-deterministic at the wrong layer.
- **Consequence**: Manager becomes a second LLM call before the Worker's LLM call. Double latency.

### 6.2 B -- Deterministic Router by task_type
- **Why rejected**: P5 violation. Speculative task taxonomy. New task types require code changes.
- **Consequence**: `if task_type == "bug_fix": ... elif task_type == "feature_add": ...` — rigid, unscalable.

### 6.3 D -- Event-Driven State Machine
- **Why rejected**: P5 violation. Verbose state machine for a linear pipeline. Existing `TaskStateMachine` handles task lifecycle; Manager doesn't need its own.
- **Consequence**: Two state machines (TaskStateMachine + ManagerStateMachine) = confusion.

---

## 7. ReAct Worker in Detail

```python
class ReActWorker:
    def process_task(self, task: Task) -> WorkerResult:
        session = SkillSession(task_id=task.id)

        for step in range(self.MAX_ITERATIONS):
            # 1. THINK: LLM reasons about current state
            thought = self.llm.generate(prompt=session.build_prompt(task))

            # 2. ACT: Parse tool call from response
            action = self.tool_parser.parse(thought)  # DD-21.3.1

            # 3. EXECUTE: Run skill via SkillRunner
            observation = self.skill_runner.execute(
                skill_id=action.skill_id,
                capability=action.capability,
                args=action.arguments,
                session=session
            )

            # 4. OBSERVE: Add to history
            session.add_turn(thought, action, observation)
            self.trace.emit(component="react_worker", level=DEBUG, ...)

            # 5. CHECK: Done?
            if self._is_complete(observation):
                return WorkerResult(success=True, output=observation)

        return WorkerResult(success=False, output="Max iterations reached")
```

The ReAct loop IS the planning mechanism. The model decomposes implicitly: "I need to read X, then edit Y, then test Z" — that's a plan, generated and revised every iteration.

---

## 8. Validation Stage

The Worker's ReAct loop MIGHT claim success without actually running tests. The Manager must verify:

```python
def _validate(self, task: CodingTask, worker_result: WorkerResult) -> ValidationResult:
    if not worker_result.success:
        return ValidationResult(passed=False, reason="worker_failed")

    # Deterministic validation: run tests
    test_result = self._test_runner.run(task.test_command)
    if not test_result.passed:
        return ValidationResult(
            passed=False,
            reason="tests_failed",
            details=test_result.failures,
        )

    return ValidationResult(passed=True)
```

**Manager is deterministic. Worker is ReAct. Validation is deterministic.** Three clean roles.

---

## 9. Cross-DD Consistency Check

F composes cleanly with ratified DDs:

| DD | How F Uses It |
|----|---------------|
| DD-21.0.1 (worker spawning) | `WorkerPool.submit()` spawns ReAct Worker in thread. ✓ |
| DD-21.3.1 (tool call generation) | ReAct Worker uses single-call structured output with retry. ✓ |
| DD-21.9.1 (diff-based editing) | ReAct Worker calls `file_edit` via search/replace with hint. ✓ |
| DD-21.10.1 (codebase indexing) | Manager calls `codebase_index.rank_for_task()` for context. ✓ |
| DD-20.10.7 (event delivery) | Manager emits `manager.task.started/completed`. Worker emits `worker.react.iteration`. ✓ |
| DD-20.10.8 (persistence) | All events persist to episodic memory via Librarian. ✓ |

No conflicts. F is the minimal Manager that composes with everything designed.

---

## 10. Rationale

| Principle | How F Honors It |
|-----------|----------------|
| P5 (no speculative contracts) | Minimal Manager: build context, spawn worker, validate. No speculative decomposition. |
| P9 (observability) | Per-ReAct-iteration traces (richer than per-stage). Manager emits lifecycle events. |
| P13 (strong and robust) | ReAct re-plans every iteration. Validation catches Worker false positives. |
| AR1 (Orchestrator→Manager→Worker) | Clean 3-tier separation. Manager deterministic, Worker ReActs. |
| Token efficiency | 1 LLM call stream (ReAct loop) vs 2+ in C. |

---

## 11. Data Structures

```python
@dataclass(frozen=True)
class CodingTask:
    task_id: UUID
    description: str
    project_path: Path
    test_command: str | None = None
    timeout_seconds: int = 600

@dataclass(frozen=True)
class CodingDeliverable:
    success: bool
    worker_output: WorkerResult
    validation_failure: ValidationResult | None = None

@dataclass(frozen=True)
class WorkerResult:
    success: bool
    output: Any
    iterations_used: int
    session: SkillSession

@dataclass(frozen=True)
class ValidationResult:
    passed: bool
    reason: str | None = None
    details: dict[str, Any] | None = None
```

---

## 12. Extension Points

| Extension | Trigger | Interface |
|-----------|---------|-----------|
| Multi-Worker Manager | Tasks hit MAX_ITERATIONS consistently | One LLM call to decompose, N ReAct Workers per subtask |
| Research Manager | Research brief tasks | Same pattern: context → ReAct Worker → validate |
| Education Manager | Training pipeline tasks | Context → ReAct Worker → validate (loss curves) |
| Human-in-the-loop | High-stakes changes | Manager pauses after Worker, awaits Owner approval |

---

## 13. Supersede Path

**Trigger**: Tasks consistently hit ReAct `MAX_ITERATIONS` before completing.

**Promotion**: Multi-Worker Manager
1. Manager makes ONE LLM call to decompose task into subtasks
2. Manager spawns N ReAct Workers, one per subtask
3. Manager integrates results deterministically

This is "C done right" — decomposition at Manager level (one LLM call), execution at Worker level (ReAct per subtask). Ship F first; promote when concrete need arrives.

---

## 14. Open Questions

| ID | Question | Status |
|----|----------|--------|
| Q-21.7.1 | Should Manager support human-in-the-loop for high-stakes changes? | Deferred |
| Q-21.7.2 | Should Manager retry with different Worker config on validation failure? | Deferred |
| Q-21.7.3 | Should Manager cache Worker results for identical tasks? | Deferred |

---

## 15. Implementation Plan

**Plan 21.7** (Department Managers -- new plan):
- S1: CodingManager class with deterministic pipeline
- S2: ReActWorker integration with WorkerPool
- S3: Validation stage (test runner)
- S4: Event emission (manager.task.started/completed)
- S5: Tests for pipeline, validation, failure modes

**Depends on**: Plan 21.0 (Worker Spawning), Plan 21.3 (ReAct Meta-Skill)

---

*End of document.*
