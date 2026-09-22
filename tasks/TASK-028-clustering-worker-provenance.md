# TASK-028 — Event Clustering Worker & Provenance Persistence

## Status
DONE

## Priority
P0

## Phase
Phase 1 — Intelligence Pipeline

## Depends On
- TASK-004
- TASK-005
- TASK-007
- TASK-022
- TASK-025
- TASK-026
- TASK-027

## Objective
Implement the background clustering worker that consumes articles from `clustering_queue`, executes candidate retrieval and multi-signal scoring, merges the article into an existing event or initializes a new event, maintains full relational provenance (`event_articles`), updates article and source counters, and enqueues event summary and timeline tasks.

## Source of Truth
- `docs/04-data-architecture.md` (events, event_articles, Relationships)
- `docs/07-event-clustering.md` (Provenance, Safety principle, Re-clustering)
- `prd.md` (Section 4.1: Marker = Event, Section 10: Event Model, Section 23.1: Provenance)

## Scope

### MUST
- Implement `ClusteringWorker` consuming `ClusterEventJob` from `clustering_queue`:
  1. Retrieve article, extracted event metadata, and resolved location from database.
  2. Retrieve candidate events via `ClusteringCandidateRetriever`.
  3. Score candidates using `ClusteringScorer`.
  4. If Decision == `MERGE`:
     - Attach article to the target event by creating `event_articles` record:
       - `event_id`, `article_id`, `match_score`, `match_reason`, `created_at`.
     - Update target event counters:
       - Increment `article_count`.
       - Recalculate `source_count` (distinct count of sources covering this event).
       - Update `last_updated_at = GREATEST(last_updated_at, article.published_at)`.
       - Update event status: from `NEW` to `DEVELOPING` or `UPDATED`.
       - If new article has higher location confidence and precision, update canonical event coordinates and `location_confidence`.
  5. If Decision == `CREATE_NEW_EVENT` (or conservative fallback):
     - Insert new `Event` record:
       - `title`, `normalized_title`, `category`, `latitude`, `longitude`, `location_label`, `location_confidence`, `geom` (from resolved location).
       - `occurred_at` (from extraction or article publication time).
       - `first_reported_at = article.published_at`.
       - `last_updated_at = article.published_at`.
       - `status = 'NEW'`, `article_count = 1`, `source_count = 1`.
     - Create `event_articles` link with `match_score = 1.0`, `match_reason = "Initial event creator"`.
  6. Enqueue `GenerateEventSummaryJob` to `summary_queue` for the affected event.
- Ensure transaction atomicity: Event creation/update and `event_articles` linking must execute within a single database transaction.
- Support re-clustering idempotency: if an article is already linked to the event, skip duplicate link creation.

### MUST NOT
- Violate the primary rule: One marker represents one event; multiple articles must be clustered under a single event when evidence warrants.
- Lose match provenance: every `event_article` link MUST store `match_score` and `match_reason`.
- Overwrite a high-confidence street location with a lower-confidence province centroid during merge.

## Architecture Constraints
- Conforms to `docs/07-event-clustering.md`: Provenance retention is mandatory.
- Conforms to `docs/04-data-architecture.md`: Unique constraint `(event_id, article_id)` strictly enforced.

## Implementation Requirements
- Create `workers/clustering/worker.py` and `backend/app/modules/events/service.py`.
- Implement atomic update transaction using database locking (`SELECT ... FOR UPDATE` on target event) to prevent race conditions when multiple articles cluster into the same event concurrently.
- Enqueue summary task with debouncing: if summary was generated < 5 minutes ago and event has many updates, schedule summary update with brief delay.

## Security Requirements
- All database mutations execute via parameterized queries.
- Match reasons sanitized to prevent injection of unvalidated strings.

## Performance Requirements
- Complete clustering workflow (retrieval + scoring + DB transaction) in < 80ms per article.

## Testing Requirements
- Integration tests:
  - Ingest first article on an incident: verifies a new `Event` is created with `article_count=1`, `source_count=1`, and linked in `event_articles`.
  - Ingest second article from different source matching the same incident: verifies article attaches to the existing event, `article_count` becomes 2, `source_count` becomes 2, and `event_articles` records `match_score` and `match_reason`.
  - Ingest third article on a completely different incident: verifies a second distinct `Event` is created.
  - Concurrency test: Two workers processing related articles concurrently lock the event row cleanly and both links persist without deadlock.

## Expected Files / Modules
- `workers/clustering/worker.py`
- `workers/clustering/pipeline.py`
- `backend/app/modules/events/service.py`
- `backend/app/modules/events/repository.py`
- `tests/integration/test_clustering_worker.py`

## Acceptance Criteria
- [ ] Worker consumes from `clustering_queue` and executes merge or create logic cleanly.
- [ ] Provenance metadata (`match_score`, `match_reason`) is recorded for every article link.
- [ ] Event counters (`article_count`, `source_count`) and timestamps update accurately.
- [ ] Summary generation jobs are pushed to `summary_queue` for affected events.

## Completion Report
When completed, report:
1. Worker clustering workflow and transaction management.
2. Row locking mechanism for concurrent article ingestion.
3. Provenance persistence schema verification.
4. Test results for new event creation, merge, and concurrency.

## Follow-up Tasks
- TASK-029 (Event Facts & Timeline Extraction Worker)
- TASK-030 (Event Summary Generator)
- TASK-031 (Event Confidence Scoring Engine)
- TASK-032 (Public Events API)
