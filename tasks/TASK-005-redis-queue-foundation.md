# TASK-005 — Redis Configuration & Queue Foundation

## Status
TODO

## Priority
P0

## Phase
Phase 0 — Foundation

## Depends On
- TASK-001
- TASK-002

## Objective
Establish the Redis connection management, caching helper abstractions, and the asynchronous job queue framework (e.g., Celery / BullMQ / RQ / ARQ) supporting named queues, idempotency, retry mechanisms with exponential backoff, and dead-letter queue (DLQ) handling.

## Source of Truth
- `docs/02-system-architecture.md` (Logical architecture, Scaling strategy)
- `docs/03-backend-architecture.md` (Workers, Idempotency)
- `docs/05-ingestion-pipeline.md` (Queue semantics)
- `docs/11-performance-scalability.md` (Worker scaling, Backpressure)

## Scope

### MUST
- Establish Redis connection pooling with automatic reconnection and keep-alive.
- Set up dedicated named queues according to architectural specifications:
  - `ingestion_queue`: feed polling and article retrieval jobs
  - `extraction_queue`: NLP / LLM extraction jobs
  - `geocoding_queue`: address resolution and geocoding jobs
  - `clustering_queue`: event candidate matching and clustering jobs
  - `summary_queue`: event summary and timeline generation jobs
  - `dead_letter_queue`: permanently failed or malformed jobs
- Standardize job payload schema:
  - `job_id`: unique string/UUID
  - `job_type`: enum matching pipeline stages
  - `entity_id`: targeted entity ID (e.g., `article_id`, `event_id`)
  - `attempt`: integer counter
  - `max_attempts`: integer limit
  - `created_at`: ISO 8601 UTC timestamp
  - `scheduled_at`: ISO 8601 UTC timestamp
  - `idempotency_key`: deterministic hash string
- Implement job deduplication/idempotency guard using Redis keys with configurable TTL.
- Provide a basic Redis cache abstraction with get, set, delete, and pattern invalidation helper functions.

### MUST NOT
- Allow synchronous user-facing API handlers to enqueue without validation.
- Allow endless job retry loops without exponential backoff and max attempt exhaustion.
- Expose Redis without authentication or bind it to public network interfaces.

## Architecture Constraints
- Conforms to `docs/02-system-architecture.md`: HTTP request handlers must never block on background worker jobs.
- Workers scale independently per queue based on queue depth metrics.

## Implementation Requirements
- Initialize queue broker and backend connection using `REDIS_URL`.
- Implement decorator or helper for scheduling asynchronous tasks with retries, exponential backoff (e.g. 5s, 15s, 45s, 120s), and random jitter.
- Implement DLQ handler when `attempt >= max_attempts`, recording failure details to database or queue log.
- Implement Redis health check (`PING`) for application readiness.

## Security Requirements
- Redis password authentication mandatory in staging and production.
- Key namespacing (`vnm:cache:`, `vnm:queue:`, `vnm:idempotency:`) to avoid key collision.
- No sensitive user or credential data serialized into queue payloads.

## Performance Requirements
- Redis queue push latency < 5ms.
- Connection pool reuse to avoid high socket churn under load.

## Testing Requirements
- Integration tests against a running Redis service:
  - Connect, push job to `ingestion_queue`, and pop job payload verifying schema integrity.
  - Test idempotency lock: attempting to enqueue the same `idempotency_key` within TTL is safely rejected or deduplicated.
  - Test retry failure progression until dead-letter queue routing.
  - Test Redis cache helper set, get with expiration, and invalidation.

## Expected Files / Modules
- `backend/app/common/queue/client.py`
- `backend/app/common/queue/schemas.py`
- `backend/app/common/queue/decorators.py`
- `backend/app/common/cache/redis.py`
- `tests/integration/test_queue_foundation.py`

## Acceptance Criteria
- [ ] 5 distinct named queues + DLQ are configured and functional.
- [ ] Standardized job envelope validated with strict schema.
- [ ] Idempotent enqueue prevents duplicate execution of the same task.
- [ ] Automated tests pass for job enqueuing, retries, and dead-letter routing.

## Completion Report
When completed, report:
1. Queue framework initialized.
2. Named queues created.
3. Job envelope and idempotency mechanism verified.
4. Test results for queue and cache helpers.

## Follow-up Tasks
- TASK-007 (Worker Runtime Foundation)
- TASK-019 (Article Ingestion Worker Pipeline)
- TASK-022 (Event Extraction Worker)
- TASK-025 (Geocoding Worker)
- TASK-028 (Clustering Worker)
- TASK-045 (Admin Processing Monitor API & UI)
