# TASK-047 — Caching Layer & Performance Optimization

## Status
TODO

## Priority
P0

## Phase
Phase 1 — Trust & Operations

## Depends On
- TASK-005
- TASK-032
- TASK-033
- TASK-034

## Objective
Implement multi-tier caching (HTTP/CDN cache headers, Redis response caching, query result caching) and optimize database queries using `EXPLAIN ANALYZE` to meet the MVP performance targets specified in `docs/11-performance-scalability.md` and `prd.md` Section 33.

## Source of Truth
- `AGENTS.md` (Performance rules)
- `docs/09-api-contracts.md` (Caching: public GET endpoints)
- `docs/11-performance-scalability.md` (Core principle, Read path, Database performance, Cache, Performance targets)
- `prd.md` (Section 33: Performance Requirements)

## Scope

### MUST
- Implement multi-tier caching architecture:
  - Tier 1 — HTTP / CDN Edge Caching:
    - Set standard `Cache-Control` and `ETag` headers on public GET endpoints:
      - `GET /api/v1/events`: `Cache-Control: public, max-age=60, s-maxage=120, stale-while-revalidate=30`
      - `GET /api/v1/events/{eventId}`: `Cache-Control: public, max-age=300, s-maxage=600`
      - `GET /api/v1/sources`: `Cache-Control: public, max-age=3600`
  - Tier 2 — Redis Response Cache:
    - Cache serialized responses for public viewport queries in Redis:
      - Cache key formula: `vnm:cache:events:<query_params_hash>`
      - Key includes all active filter parameters: `bbox`, `from`, `to`, `category`, `status`, `minSources`, `page`.
      - TTL: 60 seconds.
    - Cache event detail responses in Redis (TTL: 5 minutes).
  - Cache Invalidation / Purge:
    - When a significant event update or newly merged article occurs, publish invalidation message to clear related Redis cache keys.
- Database Query Optimization:
  - Run `EXPLAIN ANALYZE` across all public API queries with 50,000+ simulated events.
  - Verify that viewport bounding box queries utilize PostGIS GiST index scan (`Index Scan using idx_events_geom`).
  - Verify that search queries utilize GIN index scan (`Bitmap Index Scan using idx_events_search_vector`).
  - Verify that date and category filters use composite B-tree index (`idx_events_status_category_occurred`).
  - Eliminate any remaining sequential scans on large tables.

### MUST NOT
- Cache admin endpoints or responses containing privileged data in the shared public Redis cache or CDN edge.
- Return stale event details indefinitely without time-to-live or invalidation.
- Cache queries with unbounded memory growth in Redis (set `maxmemory-policy: allkeys-lru`).

## Architecture Constraints
- Conforms to `docs/11-performance-scalability.md`: Scale by removing expensive work from synchronous requests; cache popular viewports and static source metadata.
- Conforms to `docs/09-api-contracts.md`: Cache keys must incorporate all relevant filter parameters.

## Implementation Requirements
- Create `backend/app/common/cache/decorators.py` and `cache_service.py`.
- Implement FastAPI/ASGI caching middleware with `ETag` computation (e.g. using MD5/SHA-256 of response body).
- Redis LRU eviction configuration in `docker/redis.conf` or environment settings.
- Index benchmark report script: `scripts/benchmark_queries.py`.

## Security Requirements
- Ensure `Set-Cookie` or `Authorization` headers are NEVER combined with `Cache-Control: public` (prevents shared cache poisoning).
- Cache key hashing uses deterministic sorting of query parameters to prevent cache bypass via parameter reordering.

## Performance Requirements
- Target: Cached viewport API response P95 < 50ms.
- Target: Uncached/indexed database event API response P95 < 500ms (PRD target < 800ms).
- Target: Search API response P95 < 600ms (PRD target < 1s).
- Cache hit ratio target > 75% for simulated normal browsing traffic.

## Testing Requirements
- Integration and performance tests:
  - Request to `GET /api/v1/events` returns HTTP 200 with `ETag` and `Cache-Control` headers.
  - Second identical request returns HTTP 304 Not Modified when passing `If-None-Match` header.
  - Second request hits Redis cache (verified via Redis counter or response header `X-Cache: HIT`).
  - Updating an event invalidates the specific event detail cache in Redis.
  - Run `scripts/benchmark_queries.py`: asserts 100% of public queries use index scans and execute within target budgets.

## Expected Files / Modules
- `backend/app/common/cache/decorators.py`
- `backend/app/common/cache/service.py`
- `backend/app/common/middleware/http_cache.py`
- `scripts/benchmark_queries.py`
- `tests/integration/test_caching.py`

## Acceptance Criteria
- [ ] Redis caching serves repeat viewport queries in < 50ms.
- [ ] HTTP `Cache-Control`, `ETag`, and 304 Not Modified mechanisms operate correctly.
- [ ] Cache invalidation triggers upon event state changes.
- [ ] `EXPLAIN ANALYZE` benchmarks prove index utilization on spatial, search, and category queries.
- [ ] Response latency meets all PRD Section 33 targets.

## Completion Report
When completed, report:
1. Multi-tier cache implementation details.
2. Redis cache key structure and invalidation hooks.
3. `EXPLAIN ANALYZE` query plan summary.
4. Benchmark latency results (P50, P95, P99) comparing cached vs uncached requests.

## Follow-up Tasks
- TASK-048 (Security Hardening & ASVS Verification)
- TASK-049 (End-to-End Critical Flow Validation)
- TASK-050 (Phase 1 Production Readiness & Runbook)
