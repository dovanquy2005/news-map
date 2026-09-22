# TASK-014 — Source Polling Scheduler & Health Monitor

## Status
DONE

## Priority
P0

## Phase
Phase 1 — News Ingestion

## Depends On
- TASK-005
- TASK-007
- TASK-010
- TASK-013

## Objective
Implement the periodic source polling scheduler that dispatches fetch jobs to the ingestion queue at configured intervals (5–15 minutes) with distributed locking, jitter, source-level error tracking, and circuit-breaker behavior.

## Source of Truth
- `docs/05-ingestion-pipeline.md` (Pipeline, Fetch policy)
- `docs/11-performance-scalability.md` (Worker scaling, Backpressure)
- `docs/12-observability.md` (Metrics: Ingestion, Alerts)
- `prd.md` (Section 22: Data Freshness, Section 29.1: Source Monitor)

## Scope

### MUST
- Implement the periodic scheduler loop (cron or background periodic task) running every minute:
  - Queries active sources eligible for crawl based on `last_success_at` / `last_error_at` and source polling interval.
  - Distributes jobs with random jitter (e.g. +/- 30s) to prevent simultaneous bursts ("thundering herd").
  - Dispatches `IngestSourceJob` to `ingestion_queue` via Redis.
- Use distributed Redis lock to ensure only one scheduler instance dispatches jobs in a multi-pod deployment.
- Implement source health metrics calculation:
  - Freshness lag = `NOW() - last_success_at`
  - Failure counter: consecutive failed crawl attempts.
- Implement circuit breaker:
  - If a source fails consecutively 5 times (configurable threshold), automatically mark source health as DEGRADED or PAUSED, log alert, and back off polling interval exponentially (e.g. 1h, 4h, 24h).
- Provide health status query service: `get_sources_health_status()`.

### MUST NOT
- Fetch feeds synchronously inside the scheduler loop; scheduler only enqueues lightweight job descriptors.
- Hammer failing sources with high-frequency retries without exponential backoff.
- Drop healthy sources from polling cycle when other sources fail.

## Architecture Constraints
- Conforms to `docs/05-ingestion-pipeline.md`: Source failures must be isolated per source; one broken source must never impede others.
- Conforms to `docs/02-system-architecture.md`: Ingestion jobs execute asynchronously in worker processes.

## Implementation Requirements
- Create `workers/ingestion/scheduler.py`.
- Implement scheduling logic using Redis distributed lock (`vnm:lock:source_scheduler`) with 50s TTL.
- Store source health states in database and update cache metrics.
- Expose health summary contract consumed by Admin APIs.

## Security Requirements
- Scheduler enforces domain rate caps to prevent unintentional denial-of-service against publisher feeds.
- Source errors logged with sanitization to avoid leaking credentials if query parameters contain tokens.

## Performance Requirements
- Scheduler dispatch loop completes in < 500ms for up to 500 configured sources.
- Redis lock acquisition and release overhead < 10ms.

## Testing Requirements
- Unit tests:
  - Verify eligible source calculation based on timestamps and intervals.
  - Verify circuit breaker triggers backoff after consecutive failures.
  - Verify random jitter distribution prevents simultaneous dispatch.
- Integration tests:
  - Test scheduler running with mock sources: verifies jobs appear in `ingestion_queue` with correct job payload.
  - Test distributed lock: concurrent scheduler execution results in exactly one dispatch pass.

## Expected Files / Modules
- `workers/ingestion/scheduler.py`
- `workers/ingestion/health.py`
- `backend/app/modules/sources/health_service.py`
- `tests/unit/test_source_scheduler.py`
- `tests/integration/test_scheduler_queue.py`

## Acceptance Criteria
- [x] Scheduler runs periodically and pushes jobs to `ingestion_queue` without blocking.
- [x] Jitter correctly disperses job schedule times.
- [x] Consecutive failures trigger the circuit breaker backoff mechanism.
- [x] Distributed locking prevents duplicate job dispatch when multiple worker pods run.

## Completion Report
When completed, report:
1. Scheduler implementation and loop interval.
2. Circuit breaker state machine and thresholds.
3. Queue dispatch payload format.
4. Test execution results.

## Follow-up Tasks
- TASK-015 (SSRF-Safe HTTP Client)
- TASK-016 (RSS Feed Adapter)
- TASK-019 (Article Ingestion Worker Pipeline)
- TASK-044 (Admin Source Monitor API & UI)
