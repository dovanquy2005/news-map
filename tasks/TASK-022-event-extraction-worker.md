# TASK-022 — Event & Entity Extraction Worker

## Status
TODO

## Priority
P0

## Phase
Phase 1 — Intelligence Pipeline

## Depends On
- TASK-005
- TASK-007
- TASK-010
- TASK-019
- TASK-020
- TASK-021

## Objective
Implement the asynchronous background worker that consumes articles from `extraction_queue`, executes the LLM extraction prompt, validates the structured output, stores raw extraction metadata, and routes the validated data into the downstream geocoding and clustering queues.

## Source of Truth
- `docs/02-system-architecture.md` (Workers, Scaling strategy)
- `docs/03-backend-architecture.md` (Module ownership: events)
- `docs/06-ai-nlp-pipeline.md` (Pipeline, Structured output)
- `prd.md` (Section 7: Event Extraction)

## Scope

### MUST
- Implement `ExtractionWorker` consuming `ExtractEventJob` from `extraction_queue`:
  1. Retrieve article from database by `article_id`.
  2. Call LLM client to perform structured extraction on title and cleaned excerpt.
  3. Validate LLM response using `EventExtractionSchema` and validation pipeline.
  4. If validation succeeds:
     - Store extracted fields in article metadata / intermediate processing state.
     - Enqueue `GeocodeLocationJob` into `geocoding_queue` with extracted location text and hierarchy.
     - Enqueue `ClusterEventJob` into `clustering_queue` with extracted event representation.
  5. If validation fails or LLM errors:
     - Retry with exponential backoff up to `max_attempts` (default: 3).
     - Upon exhausting attempts, push job to `dead_letter_queue` and record failure in `ProcessingJob` log.
- Handle external LLM provider rate limits (HTTP 429) gracefully: pause queue consumption or re-schedule job with delayed timestamp without crashing the worker.
- Record structured metrics: `extraction_duration_seconds`, `extraction_success_total`, `extraction_failure_total`.

### MUST NOT
- Block or fail silently when LLM response is malformed.
- Write directly into final `events` or `locations` tables before geocoding and clustering are completed.
- Lose article data or drop jobs when LLM service is temporarily unreachable.

## Architecture Constraints
- Conforms to `docs/06-ai-nlp-pipeline.md`: Raw model output never touches canonical event tables without passing validation.
- Worker process runs independently and can be scaled according to queue depth.

## Implementation Requirements
- Create `workers/extraction/worker.py` and `workers/extraction/service.py`.
- Ensure DB transaction is scoped strictly to updating article metadata and processing job status (no open DB transactions during LLM network call).
- Emit structured log with `correlation_id`, `article_id`, and token usage.

## Security Requirements
- Prompt injection protection enforced through the client abstraction from TASK-020.
- LLM API keys and model parameters securely retrieved without appearing in logs.

## Performance Requirements
- Processing throughput: Process up to 5 concurrent extraction jobs per worker process.
- Job queue latency: Extraction job starts within 5s of being enqueued under normal load.

## Testing Requirements
- Integration tests:
  - Push `ExtractEventJob` with mock article into `extraction_queue`.
  - Worker runs job using mock LLM client: verifies structured validation succeeds.
  - Verifies downstream jobs appear in `geocoding_queue` and `clustering_queue`.
  - Simulates LLM provider 500 error: verifies retry counter increments and job is re-scheduled.
  - Simulates permanently invalid model response: verifies job routes to DLQ after 3 failed attempts.

## Expected Files / Modules
- `workers/extraction/worker.py`
- `workers/extraction/service.py`
- `workers/extraction/schemas.py`
- `tests/integration/test_extraction_worker.py`

## Acceptance Criteria
- [ ] Worker processes jobs from `extraction_queue` end-to-end.
- [ ] Validated extraction results correctly enqueue subsequent geocoding and clustering jobs.
- [ ] Rate limits and temporary LLM outages trigger safe retries with backoff.
- [ ] Invalid model outputs are routed to DLQ after exhausting configured retries.

## Completion Report
When completed, report:
1. Worker implementation and queue bindings.
2. Error handling and retry strategy.
3. Queue handoff to geocoding and clustering.
4. Test execution results for success and failure scenarios.

## Follow-up Tasks
- TASK-023 (Location Extraction & Hierarchical Normalization)
- TASK-024 (Geocoding Adapter & Spatial Resolution)
- TASK-025 (Geocoding Worker & Persistence)
- TASK-026 (Clustering Candidate Retrieval)
