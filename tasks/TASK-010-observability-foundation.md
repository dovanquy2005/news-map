# TASK-010 — Observability Foundation (Structured Logging, Metrics & Tracing)

## Status
DONE

## Priority
P0

## Phase
Phase 0 — Foundation

## Depends On
- TASK-001
- TASK-002
- TASK-006
- TASK-007

## Objective
Establish the observability foundation across backend API and async worker runtimes, including structured JSON logging with automated secret redaction, OpenTelemetry / Prometheus metrics collection, and distributed trace/correlation ID propagation.

## Source of Truth
- `AGENTS.md` (Logging rule)
- `docs/10-security.md` (Logging security)
- `docs/12-observability.md` (Three pillars, Correlation, Metrics, Alerts)
- `prd.md` (Section 30: Observability)

## Scope

### MUST
- Implement structured JSON logger formatting log records with:
  - `timestamp`: ISO 8601 UTC
  - `level`: DEBUG, INFO, WARNING, ERROR, CRITICAL
  - `correlation_id`: extracted from HTTP request context or worker job context
  - `module`: originating code module
  - `message`: log description
  - `extra`: contextual structured dictionary
- Implement automatic data sanitizer redacting known sensitive patterns:
  - Auth tokens, API keys, passwords, bearer headers, credit cards.
- Implement metrics collector (Prometheus format) exposing `/metrics` (internal/privileged route):
  - API metrics: HTTP request counter by route/status, request duration histogram (P50, P95, P99).
  - Worker metrics: Job execution counter by queue/status, job processing duration histogram.
  - Queue metrics: Gauge of active queue depths across Redis queues.
- Standardize log error capture including exception class, handled error code, and correlation ID without spilling raw credentials.

### MUST NOT
- Log full API keys, database connection strings, passwords, or secret payloads.
- Expose the `/metrics` endpoint on the public unauthenticated edge.
- Use blocking, synchronous external HTTP log shippers in the critical request path.

## Architecture Constraints
- Conforms to `docs/12-observability.md`: every request and important background job carries a correlation/request ID.
- Logging and metrics collection must be non-blocking and safe for async event loops.

## Implementation Requirements
- Create `backend/app/common/logging/logger.py` with standard library logging / structlog / loguru configured for JSON output.
- Create Prometheus instrumentation middleware for HTTP routes.
- Integrate worker runner logging hooks to bind `job_id`, `job_type`, and `correlation_id` to logger context.

## Security Requirements
- Strict regex and key-name redactor for sensitive dictionary keys (`password`, `token`, `secret`, `authorization`, `api_key`, `key`).
- Access to `/metrics` restricted to localhost or authenticated monitoring IP range.

## Performance Requirements
- Logging overhead < 0.5ms per log statement.
- Prometheus scraping `/metrics` must respond in < 25ms.

## Testing Requirements
- Unit and integration tests:
  - Verify log outputs are valid JSON and contain `timestamp`, `level`, `correlation_id`.
  - Test secret sanitizer: passing a dictionary containing `"api_key": "secret123"` verifies the log output replaces it with `"[REDACTED]"`.
  - Test metrics endpoint: making sample requests increments HTTP request count and latency histograms appropriately.

## Expected Files / Modules
- `backend/app/common/logging/logger.py`
- `backend/app/common/logging/sanitizer.py`
- `backend/app/common/metrics/prometheus.py`
- `backend/app/api/metrics.py`
- `tests/unit/test_logging_sanitizer.py`
- `tests/integration/test_metrics.py`

## Acceptance Criteria
- [x] Structured logs emit in valid single-line JSON format with correlation/request IDs.
- [x] Secret masking filter removes passwords, tokens, and database credentials from log lines.
- [x] Prometheus-compatible metrics endpoint `/metrics` exports HTTP and queue metrics.
- [x] Automated tests verify secret redaction and metrics collection.

## Completion Report
When completed, report:
1. Structured JSON logger implementation details.
2. Secret redaction mechanism and verified patterns.
3. Prometheus metrics schema and endpoint verification.
4. Test execution results.

## Follow-up Tasks
- TASK-014 (Source Scheduler & Health Monitor)
- TASK-044 (Admin Source Monitor API & UI)
- TASK-045 (Admin Processing Monitor API & UI)
- TASK-048 (Security Hardening & ASVS Verification)
