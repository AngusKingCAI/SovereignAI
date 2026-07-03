Depends on: none
Vision principles: P2 (everything pluggable), P10 (no silent failures)
Open questions resolved: none

S0 -- Opening
S0.1: Run `/open`
S0.2: Read `AGENTS.md` in full
S0.3: Read `sovereignai/shared/types.py` and `sovereignai/shared/event_bus.py` in full
S0.4: Read DEBT #11, #13 for context

S1 -- Break circular import in types.py
S1.1: Extract `UUID` type alias and `CorrelationId` newtype to `sovereignai/shared/types_base.py`
S1.2: `types_base.py` has zero dependencies on other sovereignai modules
S1.3: Update `types.py` to import from `types_base.py`
S1.4: Update `event_bus.py` to import `CorrelationId` from `types_base.py`
S1.5: Change `correlation_id: str` to `correlation_id: CorrelationId` (UUID wrapper) in all event bus methods
S1.6: Run `/verify`

S2 -- Update all correlation_id usages
S2.1: Search all `sovereignai/` for `correlation_id` string usage
S2.2: Update each to use `CorrelationId` type
S2.3: Ensure `uuid.uuid4()` generation still works (wrapped in `CorrelationId()`)
S2.4: Run `/verify`

S3 -- Wire VersionNegotiator disable option
S3.1: Read `sovereignai/shared/version_negotiator.py` and `sovereignai/main.py`
S3.2: Add `version_negotiation_enabled: bool` to config schema
S3.3: In `main.py`, check config before instantiating `VersionNegotiator`
S3.4: If disabled, skip negotiation, use default version
S3.5: Run `/verify`

S4 -- Tests
S4.1: Add `test_correlation_id_typing.py` -- verify UUID type, not string
S4.2: Add `test_version_negotiator_disable.py` -- verify skip when disabled
S4.3: Run full test suite, verify no regressions

S5 -- Update DEBT
S5.1: Mark DEBT #11, #13 as resolved at prompt-20.9.8
S5.2: Run `/verify`

Closing: Run `/close`
