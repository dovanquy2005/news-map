# TASK-029 — Event Facts & Timeline Extraction Worker

## Status
TODO

## Priority
P0

## Phase
Phase 1 — Intelligence Pipeline

## Depends On
- TASK-004
- TASK-028

## Objective
Implement the domain logic and background tasks that aggregate factual claims and construct the structured chronological timeline for clustered events, strictly distinguishing between event occurrence time, initial reporting time, and subsequent source updates as required by `prd.md` Section 13.

## Source of Truth
- `docs/04-data-architecture.md` (event_facts, event_timeline)
- `prd.md` (Section 13: Timeline, Section 20.5: event_facts, Section 20.6: event_timeline, Section 23.4: Conflicting information)

## Scope

### MUST
- Implement `EventTimelineService`:
  - Extract and maintain chronological milestones for an event:
    - `OCCURRED`: Timestamp when the incident physically happened.
    - `FIRST_REPORTED`: Timestamp when the first publisher broke the story.
    - `SOURCE_UPDATE`: Subsequent articles or official statements published over time.
    - `OFFICIAL_STATEMENT`: Milestone when government or police statement is detected.
  - Store timeline items in `event_timeline` table:
    - `event_id`, `timestamp` (UTC), `timeline_type`, `text`, `source_article_id`, `created_at`.
  - Maintain timeline sorted chronologically.
- Implement `EventFactsService`:
  - Aggregate factual claims extracted from all attached articles.
  - Store claims in `event_facts` table:
    - `event_id`, `fact_key`, `fact_value`, `fact_confidence`, `supporting_article_count`.
  - Detect conflicting facts across sources:
    - E.g. Source A says "2 injured", Source B says "5 injured".
    - Flag conflicting facts with status `CONFLICTING` / `UNCERTAIN` rather than picking one arbitrarily.
- Re-compute timeline and fact aggregations whenever a new article attaches to an existing event.

### MUST NOT
- Conflate `occurred_at` with `published_at` or `updated_at`; keep the three timestamps strictly distinguished.
- Arbitrarily decide which conflicting fact is "true" without verifiable multi-source consensus.
- Retain duplicate timeline entries for identical reports from the same source.

## Architecture Constraints
- Conforms to `prd.md` Section 13: Never mix the three types of timestamps into one.
- Persist structured facts and timeline events into their designated relational tables from `docs/04-data-architecture.md`.

## Implementation Requirements
- Create `backend/app/modules/events/timeline_service.py` and `facts_service.py`.
- Implement conflict detection algorithm:
  - Cluster similar fact keys (e.g., casualty numbers, cause of incident).
  - If values diverge, record divergence and lower `fact_confidence`.

## Security Requirements
- Timeline text and fact values sanitized to eliminate raw HTML or executable scripts.
- Foreign key constraints ensure timeline entries are purged if parent event is deleted.

## Performance Requirements
- Timeline and fact update execution < 20ms per attached article.

## Testing Requirements
- Unit and integration tests:
  - Test timeline construction: correctly distinguishes `OCCURRED`, `FIRST_REPORTED`, and `SOURCE_UPDATE` milestones.
  - Test fact conflict detection: two articles claiming different numbers of casualties result in separate fact records flagged with conflict state.
  - Database persistence: verifies inserting timeline and facts records for an event and retrieving them ordered by timestamp.

## Expected Files / Modules
- `backend/app/modules/events/timeline_service.py`
- `backend/app/modules/events/facts_service.py`
- `backend/app/modules/events/models/event_fact.py`
- `backend/app/modules/events/models/event_timeline.py`
- `tests/unit/test_timeline_facts.py`
- `tests/integration/test_timeline_persistence.py`

## Acceptance Criteria
- [ ] Timeline entries cleanly separate event time from article published and updated times.
- [ ] Conflicting facts between sources are detected, attributed, and flagged without arbitrary resolution.
- [ ] Timeline and facts persist in dedicated relational tables with full source article attribution.
- [ ] Automated tests verify chronological ordering and conflict detection.

## Completion Report
When completed, report:
1. Timeline milestone classification implementation.
2. Fact aggregation and conflict detection logic.
3. Database persistence schema verification.
4. Test execution results for timeline and fact scenarios.

## Follow-up Tasks
- TASK-030 (Event Summary Generator)
- TASK-031 (Event Confidence Scoring Engine)
- TASK-033 (Public Event Detail API)
- TASK-038 (Event Detail Panel)
