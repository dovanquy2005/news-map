# TASK-046 — Admin Data Quality Review Queue & Audit Log

## Status
TODO

## Priority
P1

## Phase
Phase 1 — Trust & Operations

## Depends On
- TASK-004
- TASK-028
- TASK-029
- TASK-031
- TASK-043

## Objective
Implement the data quality review queue for human-in-the-loop oversight of suspicious, low-confidence, or conflicting events, along with manual correction and re-clustering capabilities and an immutable audit log recording all operator interventions.

## Source of Truth
- `docs/07-event-clustering.md` (Re-clustering)
- `docs/13-admin-operations.md` (Review queue, Audit log)
- `prd.md` (Section 29.3: Event review, Section 34: Should have)

## Scope

### MUST
- Implement Review Queue API endpoints under `/api/v1/admin/review`:
  - `GET /api/v1/admin/review`: retrieve prioritized events requiring operator inspection:
    - Low location confidence (`location_confidence < 0.50`).
    - Low clustering match score (`0.40 <= match_score <= 0.75` in `event_articles`).
    - High conflict flag (`is_conflicting = true` in `event_facts`).
    - Single source breaking news with high casualty claims.
  - `POST /api/v1/admin/review/{eventId}/correct-location`: override event coordinates or location label.
  - `POST /api/v1/admin/review/{eventId}/split-event`: detach specific articles from an incorrectly merged event into a new independent event.
  - `POST /api/v1/admin/review/{eventId}/merge-into`: manually merge two duplicate events into one.
  - `POST /api/v1/admin/review/{eventId}/reprocess`: re-enqueue event for re-extraction, re-clustering, or re-summarization.
- Implement immutable Audit Log:
  - Record table `audit_logs`:
    - `actor_id`: Admin UUID
    - `action`: string (`CORRECT_LOCATION`, `SPLIT_EVENT`, `MERGE_EVENT`, `REPROCESS`, `TOGGLE_SOURCE`)
    - `resource_type`: string (`EVENT`, `ARTICLE`, `SOURCE`)
    - `resource_id`: UUID
    - `changes`: JSONB (before and after state diff)
    - `result`: `SUCCESS` | `FAILURE`
    - `timestamp`: UTC (`TIMESTAMPTZ`)
    - `request_id`: correlation ID
  - Append-only; zero updates or deletions permitted on audit records.
- Implement Admin Web UI (`/admin/review`):
  - Review queue listing with filter by issue type (Low Location, Low Cluster, Fact Conflict).
  - Event comparison drawer: side-by-side view of attached articles and facts.
  - Split and merge interactive modal tools.

### MUST NOT
- Allow silent manual data edits without generating an audit log record.
- Store sensitive administrative credentials or secrets inside the audit log `changes` payload.
- Delete provenance history when splitting or merging events (record manual intervention reason in `event_articles.match_reason`).

## Architecture Constraints
- Conforms to `docs/13-admin-operations.md`: Review queue prioritizes low confidence, conflict, and extraction errors.
- Audit log conforms to `docs/13-admin-operations.md` audit schema and never stores secrets.

## Implementation Requirements
- Create `backend/app/api/v1/admin/review.py` and `audit.py`.
- Service layer `backend/app/modules/admin/review_service.py` and `audit_service.py`.
- Admin frontend components:
  - `frontend/src/admin/pages/ReviewQueuePage.tsx`
  - `frontend/src/admin/components/ReviewEventCard.tsx`
  - `frontend/src/admin/components/SplitMergeModal.tsx`
  - `frontend/src/admin/components/AuditLogTable.tsx`

## Security Requirements
- All review actions require role `OPERATOR` or `SUPERADMIN`.
- Audit logs write-protected via database triggers or table permission grants preventing `UPDATE` and `DELETE`.

## Performance Requirements
- Review queue query execution < 30ms with indexed review criteria.
- Audit logging adds < 5ms to administrative action latency.

## Testing Requirements
- Integration and API tests:
  - Events with low location confidence automatically appear in the review queue.
  - Splitting an event removes target article from original event, creates new event, and creates link with reason `"Manual admin split"`.
  - Merging two events moves all articles to surviving event and archives duplicate event.
  - Every administrative action generates an `audit_logs` record containing before/after diff and `actor_id`.
  - Database test: attempting to execute `UPDATE` or `DELETE` on `audit_logs` fails with database error.

## Expected Files / Modules
- `backend/app/api/v1/admin/review.py`
- `backend/app/api/v1/admin/audit.py`
- `backend/app/modules/admin/review_service.py`
- `backend/app/modules/admin/audit_service.py`
- `backend/app/modules/admin/models/audit_log.py`
- `frontend/src/admin/pages/ReviewQueuePage.tsx`
- `tests/api/test_admin_review_api.py`

## Acceptance Criteria
- [ ] Review queue correctly surfaces low-confidence, conflicting, and borderline event clusters.
- [ ] Manual location correction, event split, and event merge tools operate atomically.
- [ ] Every administrative action is immutably logged with actor, action, diff, and correlation ID.
- [ ] Automated tests verify split/merge logic and audit log immutability.

## Completion Report
When completed, report:
1. Review queue query filters and priority scoring.
2. Split and merge transaction implementation.
3. Audit log persistence and immutability safeguards.
4. Test execution results for operator actions.

## Follow-up Tasks
- TASK-047 (Caching & Performance Optimization)
- TASK-048 (Security Hardening & ASVS Verification)
