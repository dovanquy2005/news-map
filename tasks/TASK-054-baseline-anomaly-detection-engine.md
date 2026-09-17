# TASK-054 — Baseline Calculation & Anomaly Detection Engine

## Status
TODO

## Priority
P1

## Phase
Phase 2 — Trend Engine

## Depends On
- TASK-042
- TASK-051

## Objective
Implement statistical baseline modeling and anomaly detection algorithms (e.g. Z-score, moving average deviation, density spikes) across Vietnamese provinces, cities, and event categories to detect statistically significant surges in regional or thematic news activity.

## Source of Truth
- `docs/01-product-scope.md` (Phase 2: anomaly detection, hotspot/heatmap)
- `prd.md` (Section 25.1: Anomaly, Section 25.2: Historical baseline)

## Scope

### MUST
- Implement `BaselineModelingService`:
  - Computes historical moving average ($\mu$) and standard deviation ($\sigma$) of event occurrence rates:
    - Baseline per Province (e.g. typical number of reported events per day in Da Nang vs Hanoi).
    - Baseline per Category (e.g. typical frequency of fire or flood reports per season).
    - Baseline per Province + Category combination.
  - Updates baseline distributions on a weekly rolling schedule using data from `historical_snapshots`.
- Implement `AnomalyDetector`:
  - Computes Z-score for current activity: $Z = \frac{X - \mu}{\sigma}$ where $X$ is the current window's event/article volume.
  - Classifies anomaly status:
    - Normal ($Z < 2.0$): Expected baseline activity.
    - Elevated ($2.0 \le Z < 3.0$): Noticeable rise above typical levels.
    - Anomaly Spike ($Z \ge 3.0$): Highly unusual surge in activity warranting hotspot identification.
- Provide anomaly query API:
  - `get_regional_anomalies(time_window_hours: int = 24) -> list[RegionalAnomalyDTO]`
  - Returns affected provinces, observed vs baseline counts, Z-scores, and contributing events.

### MUST NOT
- Flag high volume in naturally busy metropolitan areas (e.g. TP.HCM or Hanoi) as an anomaly without accounting for their higher baseline mean ($\mu$).
- Require external machine learning microservices (pure statistical Python/SQL computation within the monolith).
- Overwrite historical baseline records.

## Architecture Constraints
- Conforms to `adr/001-modular-monolith.md`: Implemented within `backend/app/modules/analytics/`.
- Conforms to `prd.md` Section 25.1: Differentiates raw volume from statistical anomaly.

## Implementation Requirements
- Create `backend/app/modules/analytics/anomaly_detector.py` and `baseline_service.py`.
- Migration adding `regional_baselines` table storing `(province, category, day_of_week, mean_volume, stddev_volume, sample_count, updated_at)`.
- Scheduled worker job updating baseline statistics every Sunday night.

## Security Requirements
- Parameterized SQL queries for statistical aggregations.
- Numerical safety: protect against division by zero when $\sigma = 0$ (set minimum epsilon standard deviation).

## Performance Requirements
- Statistical anomaly calculation for all 63 provinces in < 50ms.

## Testing Requirements
- Unit and integration tests:
  - Statistical calculations: correctly computes $\mu$ and $\sigma$ for sample time-series data.
  - Sudden surge test: 15 flood events in a province with typical $\mu=1, \sigma=0.8$ produces $Z > 3.0$ -> Anomaly Spike.
  - Expected volume test: 10 events in a province with $\mu=12, \sigma=3$ produces $Z < 0$ -> Normal.
  - Division-by-zero protection: handles zero-variance historical data without crashing.

## Expected Files / Modules
- `backend/app/modules/analytics/anomaly_detector.py`
- `backend/app/modules/analytics/baseline_service.py`
- `backend/app/modules/analytics/models/regional_baseline.py`
- `tests/unit/test_anomaly_detector.py`
- `tests/integration/test_baseline_service.py`

## Acceptance Criteria
- [ ] Historical moving averages and standard deviations are computed per province and category.
- [ ] Anomaly detector identifies statistical surges ($Z \ge 3.0$) accurately while respecting regional baselines.
- [ ] Numerical safeguards prevent zero-division errors on sparse datasets.
- [ ] Unit and integration tests verify anomaly classifications.

## Completion Report
When completed, report:
1. Baseline calculation model and parameters.
2. Z-score anomaly classification thresholds.
3. Baseline persistence schema.
4. Test execution results for surge detection.

## Follow-up Tasks
- TASK-055 (Multi-Factor Trend Score Engine)
- TASK-056 (Trend & Hotspot UI Extension)
