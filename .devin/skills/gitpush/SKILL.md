---
name: gitpush
authority: AGENTS.md
description: Automated git tagging and push. Creates semantic version tag and pushes all changes to remote repository.
argument-hint: "[major|minor|patch]"
triggers: ["user", "model"]
allowed-tools:
  - read
  - exec
  - skill
---

Operational Rules: See AGENTS.md
- Universal: Gate A10 (Git push blocked without user confirmation)
- Push-specific: User confirmation required, safety checks, semantic versioning

Run `/gitpush` workflow. Creates semantic version tag and pushes all changes including tags to remote repository.

## Safety Checks (per Gate A10)
1. **Uncommitted changes check**: Aborts if uncommitted changes detected
2. **Remote availability check**: Aborts if no git remote configured
3. **User confirmation**: Requires explicit "yes" confirmation before push
4. **Tag conflict prevention**: Checks for existing tags before creating new ones

## Version Management
- Tag format: v{major}.{minor}.{patch}
- Default increment: patch (unless specified: major, minor)
- Automatic version calculation based on existing tags
- Semantic versioning: major (breaking changes), minor (new features), patch (bug fixes)

## Workflow Steps
1. Check for uncommitted changes (abort if found)
2. Check git remote availability (abort if missing)
3. Get current branch and version
4. Calculate new version based on increment type
5. Display push summary (branch, remote, version change, commits)
6. Request user confirmation (Gate A10)
7. Create annotated tag with release message
8. Push commits to remote
9. Push tags to remote
10. Display success confirmation

## Usage Examples
- `/gitpush` - Increment patch version (v1.0.0 → v1.0.1)
- `/gitpush patch` - Increment patch version (v1.0.0 → v1.0.1)
- `/gitpush minor` - Increment minor version (v1.0.0 → v1.1.0)
- `/gitpush major` - Increment major version (v1.0.0 → v2.0.0)

## Error Handling
- Uncommitted changes: Aborts with error message
- No remote configured: Aborts with error message
- Invalid increment type: Aborts with error message
- Tag creation failure: Aborts with error message
- Push failure: Aborts with error message
- User cancellation: Graceful exit with cancellation message