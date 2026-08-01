# Rule-Adherence-First Harness for Devin CLI

A comprehensive governance harness that enforces rules through deterministic hooks rather than probabilistic prompts.

## Architecture

This harness implements a six-layer architecture:

1. **Layer 1: Constitutional Principles** - 4-tier precedence hierarchy (safety > ethics > compliance > helpfulness)
2. **Layer 2: Policy Cards** - Machine-readable rules in YAML with JSON Schema validation
3. **Layer 3: Enforcement Hooks** - Policy Decision Points that evaluate every tool call
4. **Layer 4: Validation Pipeline** - CI validators and pre-commit hooks
5. **Layer 5: Audit & Feedback Loop** - Violation logging and weekly review reports
6. **Layer 6: Rigorous Testing** - Unit, integration, property-based, and mutation tests

## Quick Start

### Installation

```bash
# Install dependencies
pip install pyyaml jsonschema pytest pytest-cov
```

### Configuration

The harness is configured via `.devin/hooks.v1.json` for Devin CLI hooks.

**Important:** Hooks will not take effect until you restart your Devin CLI session.

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=scripts/enforcement --cov=scripts/validation --cov=scripts/audit

# Run validators
python scripts/validation/validate_policy_cards.py
python scripts/validation/lint_ssot_duplicates.py
python scripts/validation/run_rule_tests.py
```

### Current Policy Cards

- **SHARED-S01**: Blocks destructive commands (rm -rf, DROP TABLE, git push --force)
- **SHARED-001**: Requires YAML frontmatter on governance .md files
- **SHARED-002**: Enforces file placement rules (governance files in governance/ directory)

## Directory Structure

```
project-root/
├── .devin/                      # Devin CLI configuration
│   ├── hooks.v1.json           # Hook registration
│   ├── agents/                 # Agent definitions
│   └── skills/                 # Progressive-disclosure skills
├── governance/                 # SSOT for all governance
│   ├── constitution.yaml       # 4-tier precedence hierarchy
│   ├── rule-index.yaml         # Auto-generated compact index
│   ├── policy-cards/           # Machine-readable rules
│   │   └── shared/             # Cross-agent rules
│   └── schemas/                # JSON Schemas for validation
├── scripts/                    # Executable scripts
│   ├── enforcement/            # Hook scripts (PDPs)
│   ├── validation/             # CI validators
│   └── audit/                  # Audit pipeline
├── tests/                      # Test suite
│   ├── unit/                   # Fast, isolated tests
│   ├── integration/            # Cross-layer tests
│   └── e2e/                    # End-to-end canary sessions
└── .github/workflows/          # CI pipelines
```

## Key Features

- **Deterministic Enforcement**: Rules are enforced by hooks, not prompts
- **Machine-Readable Rules**: YAML Policy Cards with JSON Schema validation
- **Token Efficiency**: Progressive disclosure keeps session-start tokens under 1,000
- **Closed Feedback Loop**: Audit logs drive continuous improvement
- **Comprehensive Testing**: Unit, integration, property-based, and mutation tests

## Token Optimization

The harness uses three-tier progressive disclosure:

- **Tier 1**: Constitution (~500 tokens) - always loaded
- **Tier 2**: Rule index (~300 tokens) - always loaded  
- **Tier 3**: Full Policy Cards - loaded on-demand via skills

Total session-start budget: approximately 800 tokens (94% reduction from prose-based approaches)

## Compliance with Design Blueprint

This implementation follows the design blueprint in `Rule_Adherence_First_Harness_Design.md`, implementing:

- Phase 1: Foundation (completed)
- Phase 2: Validation (completed)
- Phase 3: Audit Loop (completed)
- Phase 4: Optimization (completed)
- Phase 5: Rigorous Testing (completed)

## Next Steps

To activate the harness:

1. Restart your Devin CLI session (hooks load on startup)
2. Test by running: `echo '{"tool":"exec","input":{"command":"rm -rf tests/"}}' | python scripts/enforcement/pre_tool_pdp.py`
3. Run the test suite: `pytest tests/`
4. Generate the rule index: `python scripts/validation/generate_rule_index.py`

## License

This harness is designed for Devin CLI and follows the Rule-Adherence-First design principles.
