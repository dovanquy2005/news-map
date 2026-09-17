# TASK-051 — Historical Snapshot Analytics & Velocity Computation Engine

## Status
TODO

## Priority
P1

## Phase
Phase 2 — Trend Engine

## Depends On
- TASK-042
- TASK-050

## Objective
Implement the time-series analytics service that processes longitudinal data from `historical_snapshots` to compute article velocity and source velocity across rolling time windows (1-hour, 6-hour, 24-hour) for active events as specified in `prd.md` Section 25.2.

## Source of Truth
- `docs/01-product-scope.md` (Phase 2: article/source velocity)
- `docs/03-backend-architecture.md` (Module ownership: analytics)
- `docs/04-data-architecture.md` (Historical snapshots)
- `prd.md` (Section 25: Trend Engine — Phase 2, Section 25.2: Internal signals)

## Scope

### MUST
- Implement `VelocityAnalyticsService`:
  - Computes `Article Velocity`:
    - `dArticles / dt` over rolling windows: $V_{1h}$ (last 1 hour), $V_{6h}$ (last 6 hours), $V_{24h}$ (last 24 hours).
    - Measures acceleration (rate of change of article publication rate).
  - Computes `Source Velocity`:
    - `dSources / dt` over rolling windows: number of new independent news sources picking up the event within the window.
  - Normalizes velocity metrics:
    - Scales raw velocity to standard percentile / z-score against historical category distributions (e.g. an accident with 5 articles in 1h is much faster than an educational report).
- Store computed velocities in `event_trend_metrics` or cache in Redis for rapid retrieval by the Trend Score engine.
- Create background scheduled worker job (`VelocityComputationWorker`) executing every 15 minutes across active events.

### MUST NOT
- Conflate raw popularity (total historical article count) with velocity (rate of change over recent time).
- Overwrite historical snapshot records during velocity computation.
- Block public API queries with heavy on-demand window aggregation queries (pre-compute or cache in Redis).

## Architecture Constraints
- Conforms to `prd.md` Section 25.1: Find change / velocity / anomaly; do not use popularity alone.
- Conforms to `adr/001-modular-monolith.md`: Logic resides within `backend/app/modules/analytics/`.

## Implementation Requirements
- Create `backend/app/modules/analytics/velocity_service.py` and `workers/analytics/velocity_worker.py`.
- SQL window function query using PostgreSQL `LAG()` or time-bucket aggregates over `historical_snapshots`.
- Fast Redis hash storage for current event velocities: `vnm:trend:velocity:<event_id>`.

## Security Requirements
- All database queries strictly parameterized.
- Pre-computed metrics prevent computational denial-of-service on public endpoints.

## Performance Requirements
- Compute rolling velocities for 1,000 active events in < 2.5s.
- Velocity lookup from Redis cache < 2ms.

## Testing Requirements
- Unit and integration tests:
  - Event with 1 article published at T-2h and 9 articles at T-0h demonstrates sharp 1-hour article velocity spike.
  - Event with steady 1 article per day shows near-zero velocity.
  - Source velocity correctly measures only distinct new publisher additions over the window.
  - Re-running worker updates velocity metrics without duplicating historical data.

## Expected Files / Modules
- `backend/app/modules/analytics/velocity_service.py`
- `backend/app/modules/analytics/schemas_velocity.py`
- `workers/analytics/velocity_worker.py`
- `tests/unit/test_velocity_analytics.py`
- `tests/integration/test_velocity_computation.py`

## Acceptance Criteria
- [ ] Velocity service accurately computes 1h, 6h, and 24h article and source velocities.
- [ ] Acceleration and growth rates are properly derived from historical snapshot series.
- [ ] Background worker periodically updates velocity cache without impacting API latency.
- [ ] Unit and integration tests pass across steady, bursting, and quiet event patterns.

## Completion Report
When completed, report:
1. Velocity formulas and windowing parameters.
2. PostgreSQL window query and indexing verification.
3. Redis caching structure for computed velocity metrics.
4. Test execution results for velocity patterns.

## Follow-up Tasks
- TASK-052 (Search Trend Signal Integration)
- TASK-053 (Public Social & External Signals Adapter)
- TASK-054 (Baseline Calculation & Anomaly Detection Engine)
- TASK-055 (Multi-Factor Trend Score Engine)
