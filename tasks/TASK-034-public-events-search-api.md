# TASK-034 — Public Events Search API (GET /api/v1/events/search)

## Status
DONE

## Priority
P0

## Phase
Phase 1 — Product

## Depends On
- TASK-004
- TASK-006
- TASK-032

## Objective
Implement the public `GET /api/v1/events/search` endpoint providing full-text search across event titles, summaries, facts, and locations with Vietnamese diacritic support, category/temporal filters, and pagination.

## Source of Truth
- `docs/04-data-architecture.md` (events indexes)
- `docs/09-api-contracts.md` (GET /events/search)
- `docs/10-security.md` (Rate limiting: search API, Resource limits)
- `docs/11-performance-scalability.md` (Performance targets: search P95 < 1s)
- `prd.md` (Section 17.3: Search, Section 21.3: Search events)

## Scope

### MUST
- Implement `GET /api/v1/events/search` accepting parameters:
  - `q`: search query string (required, 2 to 100 characters)
  - `province`: optional string filter
  - `category`: optional category filter
  - `from`: optional ISO 8601 UTC timestamp
  - `to`: optional ISO 8601 UTC timestamp
  - `page`: integer (default: 1)
  - `limit`: integer (default: 20, max: 50)
- Implement PostgreSQL Full-Text Search (FTS) or trigram similarity:
  - Create full-text search vector column (`search_vector` `tsvector`) or generated expression indexing `events.title`, `events.summary`, and `events.location_label`.
  - Use Vietnamese-aware text search dictionary or unaccent configuration (`unaccent` extension) to support both accented and unaccented searches (e.g. searching "chay" matches "cháy", "Da Nang" matches "Đà Nẵng").
  - Rank results using `ts_rank` weighted by title relevance > location relevance > summary relevance.
- Return standardized paginated response containing matching event cards.

### MUST NOT
- Allow unbounded wildcards or empty queries that force full-table scans.
- Accept search strings exceeding 100 characters (reject with HTTP 400 `QUERY_TOO_LONG`).
- Introduce external search clusters (Elasticsearch/OpenSearch) prematurely before PostgreSQL FTS reaches measured limits.

## Architecture Constraints
- Conforms to PRD Section 37: Start with PostgreSQL Full-Text Search for MVP.
- Conforms to `docs/10-security.md`: Dedicated rate-limiting on search endpoint to prevent resource exhaustion attacks.

## Implementation Requirements
- Migration script adding `tsvector` column and GIN index on `events(search_vector)`.
- Backend router `backend/app/api/v1/events/search.py` and search repository.
- Vietnamese text query pre-processor: sanitizes query string, normalizes whitespace, formats into websearch tsquery or plainto_tsquery.

## Security Requirements
- Sanitization of user query `q` using parameterized full-text query syntax to prevent SQL injection or FTS syntax manipulation.
- Search rate limit: max 20 requests per minute per IP.

## Performance Requirements
- P95 search latency < 800ms (PRD benchmark target < 1s).
- GIN index scan verified on query plan.

## Testing Requirements
- API integration tests:
  - Search "cháy" returns relevant fire events.
  - Search without diacritics "da nang" returns events located in "Đà Nẵng".
  - Search with combined filters (query + category + province) applies all criteria correctly.
  - Short query (< 2 chars) returns 400 `QUERY_TOO_SHORT`.
  - Overly long query (> 100 chars) returns 400 `QUERY_TOO_LONG`.
  - Rate-limit test: rapid bursts trigger HTTP 429 after exceeding limit.

## Expected Files / Modules
- `backend/app/api/v1/events/search.py`
- `backend/app/modules/search/service.py`
- `backend/app/modules/search/repository.py`
- `backend/migrations/versions/0003_event_fts_index.py`
- `tests/api/test_events_search_api.py`

## Acceptance Criteria
- [ ] Full-text search returns relevant events ranked by relevance score.
- [ ] Diacritic-insensitive matching enables searching with or without Vietnamese accent marks.
- [ ] Server-side input bounds and rate-limiting protect search resources.
- [ ] GIN index ensures fast query execution meeting PRD latency budget.

## Completion Report
When completed, report:
1. Full-text search implementation and dictionary configuration.
2. GIN index creation and unaccent support.
3. Query sanitization and rate-limiting setup.
4. API test results for Vietnamese queries and edge cases.

## Follow-up Tasks
- TASK-039 (Filter & Search UI Component)
- TASK-040 (Event Feed View & Map Sync)
- TASK-047 (Caching & Performance Optimization)
