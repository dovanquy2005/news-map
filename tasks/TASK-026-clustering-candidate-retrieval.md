# TASK-026 — Event Clustering: Candidate Retrieval Service

## Status
DONE

## Priority
P0

## Phase
Phase 1 — Intelligence Pipeline

## Depends On
- TASK-004
- TASK-021
- TASK-025

## Objective
Implement the fast spatial-temporal-categorical candidate retrieval service that queries a small, relevant subset of active existing events to compare against an incoming article, avoiding exhaustive O(N) comparisons as required by `docs/07-event-clustering.md`.

## Source of Truth
- `docs/04-data-architecture.md` (events indexes, PostGIS spatial index)
- `docs/07-event-clustering.md` (Candidate retrieval)
- `prd.md` (Section 9: Event Clustering)

## Scope

### MUST
- Implement `ClusteringCandidateRetriever` service that filters candidate events using multi-index database queries:
  - Temporal Window Filter: Event `occurred_at` or `last_updated_at` within +/- 72 hours of article `published_at` / `occurred_at`.
  - Spatial Proximity Filter (when location is available): PostGIS spatial query finding events within a configurable radius:
    - Street/POI level: within 2,000 meters (`ST_DWithin`).
    - Ward/District level: within 10,000 meters.
    - Province level: within same province name.
    - Unresolved location: falls back to non-spatial candidate search.
  - Category Filter: Events with matching category or related compatible category (e.g. `ACCIDENT` and `TRAFFIC`).
  - Active Status Filter: Events with status `NEW`, `DEVELOPING`, `UPDATED`, or recently `QUIET` (< 7 days). Exclude `ARCHIVED` events.
  - Result Cap: Bounded retrieval limit (max 25 most relevant candidates per article).
- Return typed candidate collection: `list[EventCandidateDTO]` with event metadata, summary, coordinates, entity list, and facts.

### MUST NOT
- Compare incoming articles against every historical event in the database (O(N) full table scan).
- Perform spatial distance calculations outside of PostGIS indexed spatial queries.
- Discard candidate search when location is absent (fall back to temporal + categorical + text matching).

## Architecture Constraints
- Conforms strictly to `docs/07-event-clustering.md`: Do not compare every article with every event.
- Queries must utilize PostGIS GiST indexes on `geom` and composite B-tree indexes on `(status, occurred_at, category)`.

## Implementation Requirements
- Create `backend/app/modules/clustering/candidate_retriever.py`.
- Implement parameterized SQL / ORM query utilizing `ST_DWithin(events.geom, ST_SetSRID(ST_MakePoint(lng, lat), 4326), radius_meters)`.
- Support configurable query parameters via settings (`CANDIDATE_TIME_WINDOW_HOURS`, `CANDIDATE_SPATIAL_RADIUS_METERS`, `MAX_CANDIDATES_LIMIT`).

## Security Requirements
- Parameterized SQL queries preventing spatial SQL injection.
- Safe default bounds on search radius and time windows to prevent resource exhaustion.

## Performance Requirements
- Candidate retrieval query execution < 25ms over 100,000 active events.

## Testing Requirements
- Integration tests against test database populated with events:
  - Events within 2km and 24h of target article are returned as candidates.
  - Events 50km away are excluded by spatial filter.
  - Events 10 days older than window are excluded by temporal filter.
  - Incompatible categories (e.g. `SPORTS` vs `FIRE`) are excluded by category filter.
  - Query returns at most configured `MAX_CANDIDATES_LIMIT` (e.g. 25).

## Expected Files / Modules
- `backend/app/modules/clustering/candidate_retriever.py`
- `backend/app/modules/clustering/schemas.py`
- `backend/app/modules/clustering/repository.py`
- `tests/integration/test_candidate_retrieval.py`

## Acceptance Criteria
- [ ] Candidate retrieval utilizes PostGIS spatial indexes and time bounds effectively.
- [ ] Non-matching distant or old events are filtered out before reaching similarity scoring.
- [ ] Fallback logic retrieves candidates when article location is coarse or unresolved.
- [ ] Integration tests verify query latency and filter accuracy.

## Completion Report
When completed, report:
1. Candidate retrieval query construction.
2. Spatial and temporal bounding rules.
3. Index utilization verification (`EXPLAIN ANALYZE`).
4. Test results for candidate filtering.

## Follow-up Tasks
- TASK-027 (Clustering Multi-Signal Similarity & Scoring)
- TASK-028 (Clustering Worker & Provenance Persistence)
