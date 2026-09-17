# TASK-042 — Historical Snapshot Collection Worker

## Status
TODO

## Priority
P1

## Phase
Phase 1 — Trust & Operations

## Depends On
- TASK-004
- TASK-005
- TASK-007
- TASK-028

## Objective
Implement the periodic historical snapshot worker that captures time-series metrics (`article_count`, `source_count`, `last_seen_at`) for active events at regular intervals, preserving longitudinal data from MVP to provide the statistical baseline required by the Phase 2 Trend Engine.

## Source of Truth
- `docs/04-data-architecture.md` (Historical snapshots, Required baseline fields)
- `prd.md` (Section 26: Historical Data)

## Scope

### MUST
- Implement `HistoricalSnapshotWorker` running on a periodic schedule (e.g. hourly cron):
  - Queries active and developing events that received updates or were created within the last 30 days.
  - Takes a point-in-time snapshot of metrics:
    - `event_id`: Event UUID
    - `captured_at`: Current UTC timestamp (`TIMESTAMPTZ`)
    - `article_count`: Current count of attached articles
    - `source_count`: Current count of distinct reporting news sources
    - `last_seen_at`: Timestamp of the most recent article published on this event
  - Bulk inserts records into the `historical_snapshots` table.
- Implement partition or retention policy helper:
  - Keep hourly snapshots for 30 days, roll older data into daily snapshots, or retain according to data class rules in `docs/04-data-architecture.md`.
- Ensure write idempotency: composite unique index on `(event_id, date_trunc('hour', captured_at))` prevents duplicate hourly snapshots if job is re-run.

### MUST NOT
- Overwrite existing historical records (snapshots must be append-only time series).
- Execute individual single-row inserts in a loop (use bulk insert).
- Block the main event ingestion or public API database connections.

## Architecture Constraints
- Conforms to `prd.md` Section 26: From MVP, longitudinal data must be captured so that after weeks/months normal baselines can be computed.
- Schema aligns strictly with `HistoricalSnapshot` model defined in `docs/04-data-architecture.md`.

## Implementation Requirements
- Create `workers/analytics/snapshot_worker.py` and `backend/app/modules/analytics/repository.py`.
- Migration script adding composite unique constraint on `(event_id, captured_at)`.
- Schedule worker task via cron or Redis queue scheduler.

## Security Requirements
- Snapshots record purely aggregated statistical counts; no personally identifiable information (PII) or secrets.

## Performance Requirements
- Snapshot job completes in < 5s for 10,000 active events using batch SQL `INSERT INTO ... SELECT`.

## Testing Requirements
- Integration tests:
  - Worker runs snapshot task: verifies rows are created in `historical_snapshots` matching event counts.
  - Verifies re-running snapshot in the same hour does not duplicate rows.
  - Queries historical series for an event: verifies chronological progression over simulated snapshots.

## Expected Files / Modules
- `workers/analytics/snapshot_worker.py`
- `backend/app/modules/analytics/snapshot_service.py`
- `backend/app/modules/analytics/repository.py`
- `tests/integration/test_snapshot_worker.py`

## Acceptance Criteria
- [ ] Snapshot worker runs periodically and captures `article_count`, `source_count`, `last_seen_at` per active event.
- [ ] Historical snapshots append cleanly without overwriting past history.
- [ ] Batch execution ensures minimal database load.
- [ ] Automated tests verify snapshot accuracy and uniqueness constraints.

## Completion Report
When completed, report:
1. Snapshot worker implementation and schedule frequency.
2. Batch SQL insertion query.
3. Retention and indexing strategy.
4. Test execution results.

## Follow-up Tasks
- TASK-051 (Phase 2 Historical Snapshot Analytics & Velocity Engine)
- TASK-054 (Phase 2 Baseline & Anomaly Detection Engine)
