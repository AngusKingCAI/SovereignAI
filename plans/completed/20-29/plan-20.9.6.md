Depends on: none
Vision principles: P9 (observability by default), P10 (no silent failures)
Open questions resolved: none

S0 -- Opening
S0.1: Run `/open`
S0.2: Read `AGENTS.md` in full
S0.3: Read `sovereignai/shared/trace_emitter.py` in full
S0.4: Read DEBT #10, #12 for context

S1 -- Implement BoundedTraceQueue
S1.1: Add `BoundedTraceQueue` class in `sovereignai/shared/trace_emitter.py`
S1.2: Use `queue.Queue(maxsize=1000)` with drain thread pattern
S1.3: Producer (emit) puts with timeout=0.1, drops oldest if full
S1.4: Consumer (drain thread) blocks on get, batches 50 items, fires callbacks
S1.5: On subscriber disconnect, drain thread exits gracefully (sentinel value)
S1.6: Run `/verify` after each edit

S2 -- Replace unbounded list in TraceEmitter
S2.1: Change `subscribe_callback` to use `BoundedTraceQueue` instead of `list.append`
S2.2: Add `max_queue_size` parameter to `subscribe_callback` (default: 1000)
S2.3: Add `queue_full_strategy` parameter: "drop_oldest" | "block" | "raise" (default: "drop_oldest")
S2.4: Run `/verify`

S3 -- Tests
S3.1: Add `test_trace_emitter_bounded_queue.py`
S3.2: Test: queue fills, drops oldest, subscriber still receives latest
S3.3: Test: subscriber disconnects, queue drains, no memory leak
S3.4: Test: multiple subscribers, each gets independent bounded queue
S3.5: Test: producer outruns consumer, queue never exceeds maxsize
S3.6: Run full test suite, verify no regressions

S4 -- Update DEBT
S4.1: Mark DEBT #10, #12 as resolved at prompt-20.9.6
S4.2: Run `/verify`

Closing: Run `/close`
