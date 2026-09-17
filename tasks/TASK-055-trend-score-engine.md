# TASK-055 — Multi-Factor Trend Score Engine

## Status
TODO

## Priority
P1

## Phase
Phase 2 — Trend Engine

## Depends On
- TASK-031
- TASK-051
- TASK-052
- TASK-054

## Objective
Implement the multi-factor Trend Score engine that combines recent growth, source velocity, search growth, and historical anomaly into a normalized 0–100 Trend Score, maintaining strict independence from the event's Confidence Score in compliance with `prd.md` Section 25.3 and Section 25.4.

## Source of Truth
- `docs/01-product-scope.md` (Phase 2: Trend Score)
- `prd.md` (Section 25.3: Trend Score, Section 25.4: Trend vs Confidence)

## Scope

### MUST
- Implement `TrendScoringEngine`:
  - Input signals:
    1. Article Velocity Score ($S_{article}$, weight: 35%): normalized from recent 1h and 6h article growth.
    2. Source Growth Score ($S_{source}$, weight: 30%): normalized rate of new independent news organizations reporting the event.
    3. Anomaly Surge Score ($S_{anomaly}$, weight: 20%): normalized from regional/categorical Z-score.
    4. External Search Trend Signal ($S_{search}$, weight: 15%): relative search spike score (defaults to neutral baseline if external signal unavailable).
  - Compute composite `trend_score` (integer 0 to 100):
    $$\text{Trend Score} = \min(100, \max(0, \sum w_i \cdot S_i))$$
  - Classify qualitative trend level:
    - `EXPLODING` (85–100): Breaking nationwide event with massive article and source acceleration.
    - `TRENDING` (65–84): Significant multi-source growth above baseline.
    - `STEADY` (35–64): Normal news coverage rate.
    - `COOLING` (0–34): Decelerating or archive status.
- Strictly maintain Trend Score vs Confidence Score independence:
  - An event can have `Trend: 95, Confidence: 42` (rapidly developing breaking rumor with high velocity but only 1-2 sources).
  - An event can have `Trend: 15, Confidence: 96` (fully verified historical event with zero recent activity).
  - Never conflate "high trend" with "verified truth".
- Store computed scores in database and cache top trending events in Redis for rapid public API retrieval.
- Provide `GET /api/v1/events/trending`: public endpoint returning top trending events with trend breakdown.

### MUST NOT
- Overwrite or merge the Trend Score into `confidence_score` (they are two completely separate dimensions).
- Lower the trend score of a rapidly breaking story just because it hasn't gathered multi-source verification yet.
- Hardcode weights without configurable settings (`TREND_WEIGHT_ARTICLE_VELOCITY`, `TREND_WEIGHT_SOURCE_VELOCITY`, etc.).

## Architecture Constraints
- Conforms strictly to `prd.md` Section 25.4: Trend = attention growth; Confidence = evidence strength.
- Evaluated asynchronously and cached; never calculated on-the-fly during user map requests.

## Implementation Requirements
- Create `backend/app/modules/analytics/trend_scorer.py` and `backend/app/api/v1/events/trending.py`.
- Migration adding `trend_score`, `trend_status`, `trend_updated_at` columns to `events` table with index on `(trend_score DESC, occurred_at DESC)`.
- Scheduled worker task recalculating trend scores for active events every 15 minutes.

## Security Requirements
- Parameterized queries and bounded floating point calculations.
- Rate limiting on public `/api/v1/events/trending` endpoint.

## Performance Requirements
- Re-scoring 1,000 active events completes in < 3s.
- `GET /api/v1/events/trending` response latency < 50ms from Redis cache.

## Testing Requirements
- Unit and integration tests:
  - Breaking event with 8 new articles and 4 new sources in 1 hour produces `trend_score >= 85` (EXPLODING).
  - Verifies that breaking unverified event has high Trend (> 85) and low Confidence (< 50) without validation errors.
  - Verifies that verified old event has high Confidence (> 90) and low Trend (< 30).
  - Missing search trend signal defaults gracefully and normalizes remaining internal weights.
  - API test: `GET /api/v1/events/trending` returns events sorted strictly descending by `trend_score`.

## Expected Files / Modules
- `backend/app/modules/analytics/trend_scorer.py`
- `backend/app/modules/analytics/schemas_trend.py`
- `backend/app/api/v1/events/trending.py`
- `workers/analytics/trend_worker.py`
- `tests/unit/test_trend_scorer.py`
- `tests/api/test_trending_api.py`

## Acceptance Criteria
- [ ] Trend score combines article velocity, source velocity, anomaly, and search growth into a 0-100 score.
- [ ] Trend Score and Confidence Score operate as mutually independent dimensions.
- [ ] Top trending events are queryable via `GET /api/v1/events/trending`.
- [ ] Unit and API tests verify score independence and calculation formulas.

## Completion Report
When completed, report:
1. Trend scoring formula and weight distribution.
2. Verified test cases demonstrating Trend vs Confidence independence.
3. Redis caching and scheduled recalculation worker.
4. Trending API endpoint verification.

## Follow-up Tasks
- TASK-056 (Trend & Hotspot UI Extension)
