# TASK-007 — Worker Runtime Foundation

## Status
DONE

## Priority
P0

## Phase
Phase 0 — Foundation

## Depends On
- TASK-002
- TASK-003
- TASK-004
- TASK-005

## Objective
Establish the independent background worker execution runtime, process supervision, graceful shutdown handling, distributed job locking, and queue consumer dispatchers for all processing stages.

## Source of Truth
- `docs/02-system-architecture.md` (Workers, Scaling strategy, Request rule)
- `docs/03-backend-architecture.md` (Workers, Idempotency)
- `docs/05-ingestion-pipeline.md` (Queue semantics)
- `docs/11-performance-scalability.md` (Worker scaling, Backpressure)
- `adr/001-modular-monolith.md`

## Scope

### MUST
- Create worker entrypoint CLI/process capable of running single or multiple queue consumers (`ingestion`, `extraction`, `geocoding`, `clustering`, `summarization`).
- Implement graceful shutdown on `SIGINT` and `SIGTERM`: allow in-flight tasks to complete within a configurable grace period (e.g., 30s) before terminating.
- Implement distributed execution lock helper (Redis-based) to ensure single-worker exclusivity for periodic or singleton tasks (e.g. source polling scheduler).
- Propagate correlation/request IDs across queued jobs to maintain end-to-end trace context.
- Record worker execution metrics (job start, finish, latency, failure) and structured log entries per job execution.
- Implement database session lifecycle management per job to guarantee clean connection release and prevent leaked transactions.

### MUST NOT
- Run worker tasks synchronously within the web API process in production.
- Keep open database transactions while waiting on external network calls or LLM endpoints.
- Drop jobs silently upon unexpected crashes.

## Architecture Constraints
- Conforms to ADR-001: Modular Monolith + Async Workers.
- Workers can be scaled horizontally and independently per queue type without affecting web API pods.

## Implementation Requirements
- Worker runner script (`workers/runner.py` or equivalent).
- Queue registration mapping each named queue to its designated task handler.
- Concurrency control configuration (number of concurrent greenlets/threads/processes per worker).
- Transaction boundary safety wrapper: helper context manager ensuring DB commit happens strictly after external operations succeed.

## Security Requirements
- Worker process runs under unprivileged system user.
- Secrets accessed only through environment variables.
- External API calls made within worker tasks must enforce connection and read timeouts.

## Performance Requirements
- Worker process start overhead < 1s.
- Clean process shutdown without orphaned Redis jobs or hanging DB connections within grace period.

## Testing Requirements
- Integration and lifecycle tests:
  - Verify worker consumes a test job from `ingestion_queue` and executes handler.
  - Test graceful shutdown signal: worker finishes current job before stopping.
  - Test distributed lock: second worker instance skips job when locked by first instance.
  - Test job exception handling: failing job triggers retry and logs error with correlation ID.

## Expected Files / Modules
- `workers/runner.py`
- `workers/common/dispatcher.py`
- `workers/common/lock.py`
- `workers/common/context.py`
- `tests/integration/test_worker_runtime.py`

## Acceptance Criteria
- [x] Background worker runner script consumes jobs across distinct named queues.
- [x] Graceful shutdown traps SIGINT/SIGTERM and terminates without in-flight task corruption.
- [x] Failed jobs record failure details and trigger backoff retries.
- [x] Database connections release cleanly back to connection pool after every job.
- [x] Automated tests verify job execution, retries, and clean shutdown.

## Completion Report
When completed, report:
1. Worker runner implementation details.
2. Queue-to-handler dispatching mechanism.
3. Graceful shutdown verification.
4. Test results for worker runtime.

## Follow-up Tasks
- TASK-014 (Source Scheduler & Health Monitor)
- TASK-019 (Article Ingestion Worker Pipeline)
- TASK-022 (Event Extraction Worker)
- TASK-025 (Geocoding Worker)
- TASK-028 (Clustering Worker)
