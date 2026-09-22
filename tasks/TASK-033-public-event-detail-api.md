# TASK-033 — Public Event Detail API (GET /api/v1/events/{eventId})

## Status
DONE

## Priority
P0

## Phase
Phase 1 — Product

## Depends On
- TASK-004
- TASK-006
- TASK-028
- TASK-029
- TASK-030
- TASK-031

## Objective
Implement the public `GET /api/v1/events/{eventId}` endpoint returning full event details, AI-synthesized summary, location metadata, source article provenance links, chronological timeline, facts, confidence breakdown, and related events in compliance with `docs/09-api-contracts.md` and `prd.md` Section 16.

## Source of Truth
- `docs/09-api-contracts.md` (GET /events/{eventId}, Response rules)
- `docs/15-dev-conventions.md` (IDs, Errors)
- `docs/18-legal-content.md` (Source attribution)
- `prd.md` (Section 12: Source & Verification View, Section 13: Timeline, Section 16: Event Detail Panel)

## Scope

### MUST
- Implement `GET /api/v1/events/{eventId}` returning the complete event schema:
  - `id`: Event UUID
  - `title`: string
  - `category`: string
  - `status`: string
  - `summary`: string (AI-generated summary with uncertainty notes)
  - `location`: object (`latitude`, `longitude`, `label`, `resolvedAddress`, `confidence`, `isApproximate`)
  - `occurredAt`: ISO 8601 UTC timestamp
  - `firstReportedAt`: ISO 8601 UTC timestamp
  - `lastUpdatedAt`: ISO 8601 UTC timestamp
  - `confidence`: object (`score`, `level`, `factors`, `explanations`)
  - `sources`: list of reporting source articles:
    - `sourceName`: string (e.g. `VnExpress`, `Tuổi Trẻ`)
    - `articleTitle`: string
    - `originalUrl`: string (direct link to original article)
    - `publishedAt`: ISO 8601 UTC timestamp
    - `updatedAt`: Optional[str]
    - `sourceType`: string (`MAJOR_NEWS`, `LOCAL_NEWS`, `OFFICIAL`, `OTHER`)
  - `timeline`: list of chronological milestones sorted ascending by timestamp:
    - `timestamp`: ISO 8601 UTC
    - `type`: `OCCURRED` | `FIRST_REPORTED` | `SOURCE_UPDATE` | `OFFICIAL_STATEMENT`
    - `text`: description string
    - `sourceName`: Optional[str]
  - `facts`: list of agreed and conflicting facts (`key`, `value`, `confidence`, `isConflicting`)
  - `relatedEvents`: list of nearby/thematic events (max 5) that were evaluated during clustering but not merged.
- Handle non-existent event IDs with standardized HTTP 404 response:
  ```json
  {
    "error": {
      "code": "EVENT_NOT_FOUND",
      "message": "The requested event could not be found."
    }
  }
  ```

### MUST NOT
- Cause N+1 database queries when fetching attached articles, timeline entries, facts, and sources (use eager loading / joins).
- Expose full copyrighted body text of source articles; provide original external URL and brief excerpt only.
- Expose internal administrative review flags or system prompts.

## Architecture Constraints
- Conforms to `AGENTS.md` Rule 9: No N+1 queries in event detail endpoint.
- Conforms to `docs/09-api-contracts.md`: Strict contract adherence with camelCase response fields.

## Implementation Requirements
- Create `backend/app/api/v1/events/detail.py` and `schemas_detail.py`.
- Query optimization:
  - Use `selectinload` or joined queries to fetch `event_articles`, `sources`, `event_timeline`, and `event_facts` in a single efficient query execution plan.
- Related events lookup:
  - Fast query retrieving events in same province/category within +/- 24 hours (excluding the current event).

## Security Requirements
- Validate UUID format before database execution to prevent unhandled format exceptions.
- Output encoding on all source titles, timeline texts, and external URLs to prevent XSS.

## Performance Requirements
- P95 response time < 100ms for event detail retrieval.
- Zero N+1 queries confirmed via test query profiling.

## Testing Requirements
- API integration tests:
  - Fetching an existing event returns 200 OK with complete schema (event, summary, location, confidence, sources, timeline).
  - Verifies source list includes direct external article links.
  - Verifies timeline entries are in strict chronological order.
  - Query profiling test: asserts total database queries executed <= 3.
  - Invalid UUID or non-existent event ID returns 404 `EVENT_NOT_FOUND`.

## Expected Files / Modules
- `backend/app/api/v1/events/detail.py`
- `backend/app/api/v1/events/schemas_detail.py`
- `backend/app/modules/events/detail_service.py`
- `tests/api/test_event_detail_api.py`

## Acceptance Criteria
- [ ] Endpoint `/api/v1/events/{eventId}` returns complete detail payload matching contract.
- [ ] Eager loading prevents N+1 query performance degradation.
- [ ] Direct links to original publisher articles are included for source transparency.
- [ ] Timeline entries are chronologically sorted.
- [ ] Non-existent events return standardized 404 error envelope.

## Completion Report
When completed, report:
1. Detail endpoint implementation.
2. Query optimization and join strategy.
3. Contract schema compliance check.
4. Test execution results and query count profiling.

## Follow-up Tasks
- TASK-037 (Event Quick Popup & Bottom Sheet)
- TASK-038 (Event Detail Panel Component)
- TASK-047 (Caching & Performance Optimization)
