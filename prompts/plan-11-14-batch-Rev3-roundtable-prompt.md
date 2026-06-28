# Round Table — Re-Review Prompt (Plan 11–14 Batch, Rev3)

**Copy everything below the line into your message to the Round Table, along with the 4 Rev3 plan files + the Rev3 adjudication log.**

---

You are reviewing **Rev3** of the SovereignAI Plans 11–14 batch. Rev2 received 23 new findings (2 CRITICAL, 9 HIGH, 10 MEDIUM) from 4 panelists. The Architect has adjudicated every finding and produced Rev3. Your job is to verify the Rev3 fixes are correct and complete, and to flag any NEW issues introduced.

## Files to review

1. `plan-11-Rev3.md` — Memory backends + Librarian + crash recovery
2. `plan-12-Rev3.md` — Versioning + Negotiator + compatibility matrix
3. `plan-13-Rev3.md` — Conformance + contract + property tests
4. `plan-14-Rev3.md` — Education department + Teacher worker + self-correction
5. `plan-11-14-batch-Rev3-adjudication.md` — Full reasoning for all 23 new findings (reference)

## What changed in Rev3 (summary)

**CRITICAL fixes:**
- **N1**: Conformance runner moved from `tests/conformance/` to `sovereignai/conformance/` (runtime-safe package shipped in production). Gate imports from `sovereignai/conformance/`, never `tests/`. Fail-open if no tests found.
- **N2**: `TraceMemoryBackend.store()` signature unified to standard `store(data: dict, metadata: dict) -> str`. TraceEvent constructed internally.

**HIGH fixes:**
- **N3**: GPU lock scoped to in-process only. Misleading Ollama claim removed. DEBT.md entry for cross-process lock.
- **N4**: Compatibility matrix entries now include `content_hash_a`/`content_hash_b`. Entries invalidated if current hash differs.
- **N5**: Shutdown marker file (`~/.sovereignai/.shutdown_marker`). Recovery skipped if marker exists (clean shutdown).
- **N6**: Property test samples from `TraceLevel`, not `TaskState`.
- **N7**: `FatalIncompatibilityError` exits immediately if `sys.stdin.isatty()` is False or `--no-wait` flag passed. 30s timeout only in interactive mode.
- **N8**: Procedural memory lock never force-acquired. On timeout, `store()` raises and caller skips the write.
- **N9**: Crash recovery wrapped in `try/except`. On failure, logs to stderr and continues startup.
- **N10**: `core = true` manifest field for core components. Negotiator classifies by this field.
- **N11**: `DIContainer.remove()` method added. Disabled plugins removed from both graph AND container.
- **N12**: Conformance gate is fail-open. Third-party tests discovered via Python entry points.

**MEDIUM fixes (10):** See adjudication log for N13–N22.

## Your job

1. **Verify the 2 CRITICAL + 9 HIGH fixes** are correct and complete.
2. **Hunt for NEW bugs** introduced by Rev3 changes (conformance runner relocation, shutdown marker, `container.remove()`, `core = true` field, fail-open gate, unified trace store signature, non-interactive detection).
3. **Do not re-litigate** findings already rejected in the Rev2→Rev3 adjudication (DeepSeek hallucinations: `_recursion_depth`, `teacher_notify`, `os.rename`, exponential backoff — these do not exist in the plans).
4. **Pre-mortem frame**: Assume Rev3 fails in 6 months. List the most plausible reasons.

## Anti-sycophancy

- "No issues found" is valid if fixes are correct.
- Each issue MUST cite a concrete failure scenario + evidence from Rev3 text.
- Ban style/formatting comments.
- **Verify cited evidence exists in the actual Rev3 files before raising a finding.** Do not hallucinate text.

## Answer format

```
## 1. Fixes verified
- N-<n>: <verified fixed / incomplete / wrong> — <one-line reasoning>

## 2. New issues found
### <severity> — <title>
- Failure scenario: <paragraph>
- Evidence: <Rev3 plan + section — QUOTE THE ACTUAL TEXT>
- Suggested fix: <one sentence>

## 3. Other concerns
<open field>

## 4. Clean pass?
<YES / NO — if NO, list blocking findings>

**Panelist**: <name/model>
```

End with `**Panelist**: <name/model>`. Named preferred.
