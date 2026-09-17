# TASK-044 — Admin Source Monitor API & UI

## Status
TODO

## Priority
P1

## Phase
Phase 1 — Trust & Operations

## Depends On
- TASK-013
- TASK-014
- TASK-043

## Objective
Implement the admin source monitoring API endpoints and web interface allowing operations staff to inspect source health metrics, view crawl errors, toggle active status, and trigger manual test fetches.

## Source of Truth
- `docs/03-backend-architecture.md` (Module ownership: admin)
- `docs/13-admin-operations.md` (Source monitor, Admin capabilities MVP)
- `prd.md` (Section 29.1: Source monitor)

## Scope

### MUST
- Implement Admin Source Monitoring endpoints under `/api/v1/admin/sources`:
  - `GET /api/v1/admin/sources`: list all configured sources with health status:
    - `id`, `name`, `domain`, `sourceType`, `active`, `priority`
    - `lastSuccessAt`, `lastErrorAt`, `freshnessLagSeconds`
    - `totalArticlesFetched`, `consecutiveErrorCount`, `healthStatus` (`HEALTHY`, `DEGRADED`, `ERROR`, `PAUSED`)
  - `POST /api/v1/admin/sources/{sourceId}/toggle`: enable or disable source crawling.
  - `POST /api/v1/admin/sources/{sourceId}/test-fetch`: execute immediate test crawl and return parsed sample articles without saving to database.
  - `POST /api/v1/admin/sources`: create a new source configuration.
  - `PUT /api/v1/admin/sources/{sourceId}`: update source configuration (URL, priority, polling interval).
- Implement Admin Web UI (`/admin/sources`):
  - Table view of all sources with search and status filters.
  - Color-coded health badges (Green: Healthy, Yellow: Degraded, Red: Error, Gray: Paused).
  - Quick action switches: toggle active/inactive.
  - Source detail drawer: displays error history, last successful crawl timestamp, and test fetch trigger button.
- Record all status changes and configuration edits into the Admin Audit Log.

### MUST NOT
- Allow non-admin users to view or invoke source monitoring endpoints.
- Allow test fetch to bypass SSRF protections or domain allowlisting.
- Overwrite production source configuration without audit logging.

## Architecture Constraints
- Conforms to `docs/13-admin-operations.md`: Show source health separately from public UI.
- All endpoints protected by RBAC dependency created in TASK-043.

## Implementation Requirements
- Backend router: `backend/app/api/v1/admin/sources.py`.
- Admin frontend components:
  - `frontend/src/admin/pages/SourceMonitorPage.tsx`
  - `frontend/src/admin/components/SourceTable.tsx`
  - `frontend/src/admin/components/SourceDetailModal.tsx`
  - `frontend/src/admin/components/TestFetchModal.tsx`

## Security Requirements
- Requires authenticated admin role (`OPERATOR` or `SUPERADMIN`).
- Rate-limit test fetch endpoint to prevent abuse (max 5 requests per minute).

## Performance Requirements
- Admin source list query returns in < 50ms.

## Testing Requirements
- API and component tests:
  - Anonymous user receives 401 when accessing `/api/v1/admin/sources`.
  - Admin user receives list of sources with calculated freshness lag.
  - Toggling active status updates database and immediately reflects in source scheduler eligibility.
  - Test fetch executes safe crawl and returns preview payload.
  - Frontend component test: displays source status badges and handles active toggle click.

## Expected Files / Modules
- `backend/app/api/v1/admin/sources.py`
- `backend/app/modules/admin/source_monitor_service.py`
- `frontend/src/admin/pages/SourceMonitorPage.tsx`
- `frontend/src/admin/components/SourceTable.tsx`
- `tests/api/test_admin_sources_api.py`

## Acceptance Criteria
- [ ] Admin endpoints allow inspecting, adding, editing, and toggling source statuses.
- [ ] Source table displays health indicators, freshness lag, and error metrics clearly.
- [ ] Test fetch feature enables verification of feed URLs before activating.
- [ ] Automated tests verify access control and status mutation behavior.

## Completion Report
When completed, report:
1. Admin source endpoints and schemas.
2. Frontend source monitor UI components.
3. Health status computation logic.
4. Test execution results.

## Follow-up Tasks
- TASK-045 (Admin Processing Queue Monitor API & UI)
- TASK-046 (Admin Review Queue & Audit Log)
