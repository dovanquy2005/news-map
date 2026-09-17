# Testing & QA

## Test pyramid

```text
        E2E
       /   \\
   API/integration
      /       \\
     Unit tests
```

## Unit tests

Test:

- dedup rules;
- location normalization;
- confidence calculation;
- event scoring;
- clustering thresholds;
- filter validation.

## Integration tests

Test real DB schema:

- PostGIS queries;
- event/article relationships;
- idempotent writes;
- transaction boundaries.

## API tests

Test:

- validation;
- pagination;
- bbox limits;
- authorization;
- rate limiting;
- error schema.

## AI contract tests

Use fixed fixture articles.

Verify:

- schema valid;
- no invented location when absent;
- uncertainty preserved;
- malformed model output handled.

## Security regression

Include cases for:

- SQLi;
- XSS;
- SSRF;
- broken admin authorization;
- excessive page/bbox limits;
- prompt injection;
- secret leakage.

## Frontend tests

At minimum:

- map filters;
- marker click;
- event panel;
- feed/map synchronization;
- mobile bottom-sheet flow.

## E2E critical flow

```text
article arrives
 -> event created
 -> map marker visible
 -> click marker
 -> detail loads
 -> source link exists
```
