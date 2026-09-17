# TASK-032 — Public Events API (GET /api/v1/events)

## Status
TODO

## Priority
P0

## Phase
Phase 1 — Product

## Depends On
- TASK-004
- TASK-006
- TASK-028
- TASK-031

## Objective
Implement the public `GET /api/v1/events` endpoint conforming to `docs/09-api-contracts.md`, supporting spatial bounding box filtering, date ranges, categories, statuses, minimum source/article counts, pagination, and strict server-side resource limits.

## Source of Truth
- `AGENTS.md` (API contract first, Performance rules)
- `docs/04-data-architecture.md` (Required indexes: events, Geospatial)
- `docs/09-api-contracts.md` (GET /events, Required server-side limits)
- `docs/10-security.md` (Resource limits)
- `docs/11-performance-scalability.md` (Public map query)
- `prd.md` (Section 21.1: Get events)

## Scope

### MUST
- Implement `GET /api/v1/events` supporting query parameters:
  - `from`: ISO 8601 UTC timestamp (default: 24 hours ago)
  - `to`: ISO 8601 UTC timestamp (default: now)
  - `province`: optional string filter (e.g. `TP. Hồ Chí Minh`)
  - `category`: optional enum filter or comma-separated list
  - `status`: optional enum filter (`NEW`, `DEVELOPING`, `UPDATED`, `QUIET`, `ARCHIVED`)
  - `minSources`: integer (minimum independent sources, default: 1)
  - `minArticles`: integer (minimum articles, default: 1)
  - `bbox`: bounding box format `minLng,minLat,maxLng,maxLat`
  - `page`: integer (default: 1)
  - `limit`: integer (default: 50, max: 100)
- Enforce strict server-side resource bounds:
  - Maximum date window: 30 days maximum for anonymous queries.
  - Maximum bounding box area: query rejected with `INVALID_BBOX` if area exceeds national/regional threshold without higher zoom.
  - Maximum page limit: capped at 100 items per response.
- Execute PostGIS spatial filter:
  - `ST_MakeEnvelope(minLng, minLat, maxLng, maxLat, 4326)` matching against `events.geom`.
- Return standardized paginated envelope:
  ```json
  {
    "data": [
      {
        "id": "uuid",
        "title": "...",
        "category": "ACCIDENT",
        "latitude": 10.7769,
        "longitude": 106.7009,
        "locationLabel": "...",
        "locationConfidence": 0.85,
        "isApproximate": false,
        "occurredAt": "...",
        "firstReportedAt": "...",
        "lastUpdatedAt": "...",
        "status": "DEVELOPING",
        "confidenceScore": 86,
        "articleCount": 12,
        "sourceCount": 7
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 50,
      "totalItems": 142,
      "totalPages": 3
    }
  }
  ```

### MUST NOT
- Return the entire dataset of events in Vietnam in a single unpaginated response.
- Allow SQL injection through unvalidated filter or bbox parameters.
- Expose private database columns, internal review flags, or admin notes.

## Architecture Constraints
- Conforms strictly to `docs/09-api-contracts.md` field naming (camelCase in JSON responses) and error schemas.
- Conforms to `AGENTS.md` Rule 9: Query DB with spatial and composite indexes; no unindexed scans on public endpoints.

## Implementation Requirements
- Create `backend/app/api/v1/events/router.py`, `service.py`, `schemas.py`.
- Query builder utilizing SQLAlchemy / SQLModel with indexed filters.
- Support HTTP caching headers (`ETag`, `Cache-Control: public, max-age=60`).

## Security Requirements
- Validate bbox coordinates: -180 <= lng <= 180, -90 <= lat <= 90, minLng <= maxLng, minLat <= maxLat.
- Rate limiting middleware applied (anonymous limit: 30 requests/min).

## Performance Requirements
- P95 response time < 300ms for indexed viewport and date queries.
- Query execution plans (`EXPLAIN ANALYZE`) must show index scan on `geom` and B-tree indexes.

## Testing Requirements
- API integration tests:
  - Query with valid `bbox` returns only events inside the bounding box.
  - Query with date range filters correctly out-of-range events.
  - Query with `minSources=3` returns only events with >= 3 sources.
  - Excessively wide bbox (> permitted area limit) returns HTTP 400 `INVALID_BBOX`.
  - Date window exceeding 30 days returns HTTP 400 `DATE_WINDOW_EXCEEDED`.
  - Pagination works accurately and page size cannot exceed 100.

## Expected Files / Modules
- `backend/app/api/v1/events/router.py`
- `backend/app/api/v1/events/schemas.py`
- `backend/app/api/v1/events/service.py`
- `tests/api/test_events_api.py`

## Acceptance Criteria
- [ ] Endpoint `/api/v1/events` handles all documented query filters with strict validation.
- [ ] PostGIS spatial queries efficiently filter events within client viewports.
- [ ] Server-side guards enforce maximum limits on date range, bbox, and page size.
- [ ] Automated tests pass for all positive filtering and negative boundary cases.

## Completion Report
When completed, report:
1. Endpoint router and schema implementation.
2. Spatial query builder and bbox validation.
3. Guard rail enforcement results.
4. API test execution results and query execution plan.

## Follow-up Tasks
- TASK-033 (Public Event Detail API)
- TASK-034 (Public Events Search API)
- TASK-035 (Google Maps Web Integration)
- TASK-040 (Event Feed View & Map Sync)
- TASK-047 (Caching & Performance Optimization)
