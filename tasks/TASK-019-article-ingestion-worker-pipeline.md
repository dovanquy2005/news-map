# TASK-019 — Article Ingestion Worker & Pipeline Integration

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
- TASK-014
- TASK-015
- TASK-016
- TASK-017
- TASK-018

## Objective
Assemble and orchestrate the end-to-end asynchronous ingestion pipeline: consume source crawl jobs from `ingestion_queue`, fetch feeds via safe adapters, normalize and deduplicate articles, persist unique articles to PostgreSQL, update source crawl statistics, and enqueue unique articles to `extraction_queue`.

## Source of Truth
- `docs/03-backend-architecture.md` (Module ownership: articles)
- `docs/05-ingestion-pipeline.md` (Pipeline, Queue semantics)
- `docs/11-performance-scalability.md` (Write/processing path, Backpressure)
- `prd.md` (Section 6.2: Article Ingestion, Section 19.1: Logical Pipeline)

## Scope

### MUST
- Implement `IngestSourceWorker` consuming `IngestSourceJob` from `ingestion_queue`:
  1. Retrieve active `Source` configuration.
  2. Instantiate appropriate adapter (`RSSFeedAdapter`).
  3. Fetch raw feed items via SSRF-safe HTTP client.
  4. Iterate items: normalize and sanitize each item into `NormalizedArticleDTO`.
  5. Run deduplication check against database/cache.
  6. Insert new unique articles into the `articles` database table in batch.
  7. For each newly inserted article, enqueue `ExtractEventJob` into `extraction_queue` with deterministic `job_id` and payload.
  8. Update `Source` metrics: `last_success_at`, `articles_fetched_count`, reset consecutive error counter.
- Catch and handle fetch/parse exceptions per source:
  - If source fails, record `last_error_at`, increment failure counter, log structured warning with correlation ID.
- Ensure pipeline idempotency: re-running ingestion for the same feed does not duplicate articles or flood the extraction queue.

### MUST NOT
- Block web API processes with feed fetching or article persistence.
- Roll back successfully persisted articles if the extraction queue publish temporarily fails (retry queue publish independently).
- Drop articles when downstream LLM quotas are exhausted; raw articles must remain safely stored in the database.

## Architecture Constraints
- Conforms to `docs/05-ingestion-pipeline.md`: `Source Scheduler -> Source Adapter -> Fetch -> Normalize -> Validate -> Deduplicate -> Store Article -> Queue Extraction`.
- Conforms to `docs/02-system-architecture.md`: Worker scales independently by queue depth.

## Implementation Requirements
- Create `workers/ingestion/worker.py` and `workers/ingestion/pipeline.py`.
- Implement batch persistence using database transaction:
  - Bulk insert unique articles (`ON CONFLICT (canonical_url) DO NOTHING`).
  - Return created article records with their generated IDs.
- Enqueue extraction jobs in batch to Redis:
  - Job payload: `{"job_type": "EXTRACT_EVENT", "entity_id": str(article.id), "attempt": 1}`.
- Emit ingestion metrics: `articles_ingested_total`, `fetch_duration_seconds`, `dedup_ratio`.

## Security Requirements
- All article inputs treated as untrusted; titles and snippets stored cleanly without executable scripts.
- Source errors logged without internal credentials.

## Performance Requirements
- Process a 50-item RSS feed (fetch, parse, normalize, dedup, persist, enqueue) in < 2.5s.
- DB write batching to minimize round-trips.

## Testing Requirements
- Integration test for the full ingestion slice:
  - Push `IngestSourceJob` for mock RSS source into `ingestion_queue`.
  - Worker runs job: verifies articles are created in PostgreSQL `articles` table.
  - Verifies corresponding `ExtractEventJob` items are pushed to `extraction_queue`.
  - Verifies `Source` entity's `last_success_at` is updated.
  - Re-run identical job: verifies zero duplicate articles created and zero extraction jobs re-enqueued.

## Expected Files / Modules
- `workers/ingestion/worker.py`
- `workers/ingestion/pipeline.py`
- `backend/app/modules/articles/service.py`
- `backend/app/modules/articles/repository.py`
- `tests/integration/test_ingestion_pipeline.py`

## Acceptance Criteria
- [x] End-to-end ingestion flow executes successfully from queue trigger to article database persistence.
- [x] Deduplication successfully suppresses duplicate articles in real pipeline execution.
- [x] Unique articles immediately produce extraction jobs in `extraction_queue`.
- [x] Source health statistics update accurately upon completion.
- [x] Re-ingestion of the same feed is fully idempotent.

## Completion Report
When completed, report:
1. Ingestion worker and pipeline implementation.
2. Batch insertion and extraction enqueue logic.
3. Source statistics update flow.
4. Integration test results demonstrating end-to-end execution.

## Follow-up Tasks
- TASK-020 (NLP Extraction Prompt Engineering & Client)
- TASK-021 (Event & Entity Extraction Schema Validation)
- TASK-022 (Event Extraction Worker)
- TASK-044 (Admin Source Monitor API & UI)
