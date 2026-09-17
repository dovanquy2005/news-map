# TASK-013 — Source Management Domain & Registry

## Status
TODO

## Priority
P0

## Phase
Phase 1 — News Ingestion

## Depends On
- TASK-004
- TASK-006

## Objective
Implement the news source domain model, registry service, and management APIs allowing administrators to configure, inspect, enable, disable, and prioritize news publisher sources in compliance with `docs/03-backend-architecture.md` and `prd.md` Section 6.1.

## Source of Truth
- `docs/03-backend-architecture.md` (Module ownership: sources)
- `docs/05-ingestion-pipeline.md` (Source adapter contract)
- `docs/18-legal-content.md` (Source policy)
- `prd.md` (Section 6.1: News Source Management, Section 20.1: Sources)

## Scope

### MUST
- Implement the `sources` module within backend domain:
  - Source domain entity and DTO schemas: `source_id`, `name`, `domain`, `source_type` (`RSS`, `SITEMAP`, `API`, `CRAWLER`), `rss_url`, `parser_type`, `active` (boolean), `priority` (1-100), `rate_limit_rpm`, `terms_url`, `last_success_at`, `last_error_at`, `created_at`, `updated_at`.
- Provide Source Management Service with methods:
  - `register_source(data)`
  - `update_source(source_id, data)`
  - `toggle_source_status(source_id, active: bool)`
  - `get_active_sources()`
  - `get_source_by_id(source_id)`
  - `record_source_crawl_result(source_id, success: bool, error_msg: Optional[str])`
- Implement legal/compliance switch: disabling a source immediately halts all pending and scheduled fetch jobs for that source domain.
- Provide initial database seed with compliant Vietnamese news RSS feeds (e.g. major national news outlets with publicly accessible RSS).

### MUST NOT
- Allow unregistered or arbitrary user-provided sources to be ingested.
- Permit bypassing the `active = false` disable switch under any circumstance.
- Hardcode source list in memory without persistent database backing.

## Architecture Constraints
- Conforms to `docs/03-backend-architecture.md`: Source management belongs to `app/modules/sources/`.
- Repository access must use the base database repository pattern established in TASK-004.

## Implementation Requirements
- Create `backend/app/modules/sources/models.py`, `schemas.py`, `service.py`, `repository.py`.
- Implement domain validation:
  - Domain must be valid FQDN (e.g. `vnexpress.net`, `tuoitre.vn`).
  - RSS URL must be valid HTTPS URL matching source domain.
  - Priority must be between 1 (lowest) and 100 (highest).
- Seed file: `backend/app/modules/sources/seed.py`.

## Security Requirements
- Domain validation prevents injection of private IP ranges or localhost into source registry.
- Source configuration updates restricted to administrative roles (to be guarded by admin auth in TASK-043).

## Performance Requirements
- `get_active_sources()` query execution < 10ms with cached index on `(active, priority DESC)`.

## Testing Requirements
- Unit tests:
  - Validation tests for FQDN domain and HTTPS RSS URLs.
  - Verification that disabling a source updates status and prevents retrieval in `get_active_sources()`.
- Integration tests:
  - Database persistence of new sources, updates, and status toggles.
  - Verification of `record_source_crawl_result` updating `last_success_at` or `last_error_at`.

## Expected Files / Modules
- `backend/app/modules/sources/__init__.py`
- `backend/app/modules/sources/models.py`
- `backend/app/modules/sources/schemas.py`
- `backend/app/modules/sources/service.py`
- `backend/app/modules/sources/repository.py`
- `backend/app/modules/sources/seed.py`
- `tests/unit/test_sources_service.py`
- `tests/integration/test_sources_repo.py`

## Acceptance Criteria
- [ ] Source domain model and CRUD service fully implemented and unit-tested.
- [ ] Disabling a source immediately excludes it from active source queries.
- [ ] Database seed populates verified Vietnamese news sources.
- [ ] Timestamps for success and error correctly update upon crawl result reporting.

## Completion Report
When completed, report:
1. Source domain service implemented.
2. Verified schema validation rules.
3. Seeded news sources.
4. Test results for repository and service methods.

## Follow-up Tasks
- TASK-014 (Source Scheduler & Health Monitor)
- TASK-015 (SSRF-Safe HTTP Client)
- TASK-016 (RSS Feed Adapter)
- TASK-044 (Admin Source Monitor API & UI)
