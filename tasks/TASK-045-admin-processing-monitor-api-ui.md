# TASK-045 — Admin Processing Queue Monitor API & UI

## Status
TODO

## Priority
P1

## Phase
Phase 1 — Trust & Operations

## Depends On
- TASK-005
- TASK-007
- TASK-010
- TASK-043

## Objective
Implement the processing queue monitoring API endpoints and admin UI dashboard providing visibility into Redis queue depths, active job states (pending, processing, completed, retry, dead-letter), failure inspection, and manual job retry capabilities.

## Source of Truth
- `docs/12-observability.md` (Metrics: Processing, Alerts)
- `docs/13-admin-operations.md` (Processing monitor, Inspect failed jobs)
- `prd.md` (Section 29.2: Processing monitor)

## Scope

### MUST
- Implement Processing Queue Monitor endpoints under `/api/v1/admin/queues`:
  - `GET /api/v1/admin/queues/stats`: returns real-time queue metrics:
    - Queue depths for `ingestion_queue`, `extraction_queue`, `geocoding_queue`, `clustering_queue`, `summary_queue`, `dead_letter_queue`.
    - Active worker count and consumer status.
    - 24-hour job throughput: processed count, failure count, average processing latency.
  - `GET /api/v1/admin/queues/dead-letter`: list failed jobs residing in the Dead-Letter Queue:
    - `jobId`, `jobType`, `entityId`, `attempt`, `errorMessage`, `failedAt`, `payload`.
  - `POST /api/v1/admin/queues/retry-job`: re-enqueue a dead-letter job back to its originating queue.
  - `POST /api/v1/admin/queues/purge-dlq`: clear resolved dead-letter jobs (with confirmation guard).
- Implement Admin Web UI (`/admin/queues`):
  - Dashboard cards showing real-time queue depths with color-coded backlog warning levels.
  - Throughput charts / sparklines for completed and failed jobs.
  - Dead-Letter Queue management table: inspect failed job error details and payload JSON.
  - "Retry Job" button allowing operators to reprocess failed items after resolving external issues (e.g. LLM quota restocked).

### MUST NOT
- Allow arbitrary command execution or unvalidated payload injection via retry endpoints.
- Expose queue monitoring or DLQ inspection publicly.
- Block worker consumers while querying queue depths.

## Architecture Constraints
- Conforms to `docs/13-admin-operations.md`: Show queues: pending, processing, success, retry, dead-letter.
- Interacts safely with Redis using non-blocking commands (`LLEN`, `SCARD`, `ZREVRANGE`).

## Implementation Requirements
- Backend router: `backend/app/api/v1/admin/queues.py`.
- Queue inspector service: `backend/app/modules/admin/queue_inspector.py`.
- Admin frontend components:
  - `frontend/src/admin/pages/QueueMonitorPage.tsx`
  - `frontend/src/admin/components/QueueDepthCard.tsx`
  - `frontend/src/admin/components/DeadLetterTable.tsx`

## Security Requirements
- Requires authenticated admin role (`OPERATOR` or `SUPERADMIN`).
- Purge and bulk retry operations require explicit confirmation and produce audit log entries.

## Performance Requirements
- Queue stats query executes in < 20ms without slowing down worker dequeuing.

## Testing Requirements
- API and component tests:
  - Querying queue stats returns accurate counts for all 5 queues + DLQ.
  - DLQ endpoint lists failed jobs with error messages and attempt counts.
  - Triggering retry moves job from DLQ back into target queue with reset attempt counter.
  - Access control test: non-admin gets 401/403.
  - Frontend test: renders queue depth cards and error message drawer.

## Expected Files / Modules
- `backend/app/api/v1/admin/queues.py`
- `backend/app/modules/admin/queue_inspector.py`
- `frontend/src/admin/pages/QueueMonitorPage.tsx`
- `frontend/src/admin/components/QueueDepthCard.tsx`
- `frontend/src/admin/components/DeadLetterTable.tsx`
- `tests/api/test_admin_queues_api.py`

## Acceptance Criteria
- [ ] Real-time queue depths and 24h throughput metrics are accessible via admin API and dashboard.
- [ ] Dead-letter queue inspection displays root-cause error messages and failure timestamps.
- [ ] Operators can safely retry failed jobs individually or in batch.
- [ ] All queue operations are protected by authentication and recorded in audit logs.

## Completion Report
When completed, report:
1. Queue inspector service implementation.
2. DLQ inspection and retry workflow.
3. Dashboard UI components.
4. Test execution results for queue metrics and job retries.

## Follow-up Tasks
- TASK-046 (Admin Review Queue & Audit Log)
- TASK-047 (Caching & Performance Optimization)
