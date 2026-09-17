# Vibe Coding Workflow

## Goal

Keep AI coding agents bounded by explicit contracts.

## Before each task

Agent must answer:

```text
TASK:

SCOPE:

SOURCE-OF-TRUTH DOCS:

FILES LIKELY TO CHANGE:

API/DATA CONTRACTS:

SECURITY CONSIDERATIONS:

TESTS:

ACCEPTANCE CRITERIA:
```

## Implementation loop

```text
Read spec
  -> inspect current code
  -> propose minimal change
  -> implement
  -> run tests/lint/typecheck
  -> inspect diff
  -> update docs if needed
```

## Never ask AI to “build the whole project” in one prompt

Split into vertical slices.

Example:

### Slice 1

Source -> article -> DB.

### Slice 2

Article -> extraction -> event.

### Slice 3

Event -> map API -> marker.

### Slice 4

Marker -> event detail -> sources/timeline.

### Slice 5

Admin -> monitoring.

## Prompt template

```text
Read AGENTS.md first.
Then read these docs:
- docs/02-system-architecture.md
- docs/03-backend-architecture.md
- docs/09-api-contracts.md
- docs/10-security.md

Task:
[ONE SMALL TASK]

Constraints:
- do not redesign architecture
- do not add dependencies unless justified
- preserve existing API contracts
- write tests

Before editing, state:
1. files to change
2. approach
3. risks

Then implement and run the relevant tests.
```

## When agent must stop and not code

- requirements conflict;
- missing API contract;
- architecture change appears necessary;
- security-sensitive behavior is unclear;
- destructive migration has no rollback plan.

In those cases produce an ADR/proposal instead of inventing behavior.
