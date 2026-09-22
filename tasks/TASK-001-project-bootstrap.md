# TASK-001 — Repository Bootstrap & Monorepo Structure

## Status
DONE

## Priority
P0

## Phase
Phase 0 — Foundation

## Depends On
-

## Objective
Establish the project workspace directory layout, dependency management, root configurations, code formatting, and developer tooling conforming to the modular monolith architecture.

## Source of Truth
- `AGENTS.md`
- `docs/02-system-architecture.md`
- `docs/03-backend-architecture.md`
- `docs/15-dev-conventions.md`
- `adr/001-modular-monolith.md`

## Scope

### MUST
- Create the standard monorepo folder layout with separated `backend/`, `frontend/`, `workers/`, `docker/`, and `docs/`.
- Configure workspace-level tooling: Git ignore rules, editor settings, code formatters (Prettier, Black/Ruff, or ESLint depending on stack selection).
- Establish modular directory structure inside `backend/app/modules/` (`sources/`, `articles/`, `events/`, `locations/`, `clustering/`, `search/`, `analytics/`, `admin/`) and `backend/app/common/`.
- Establish `workers/` directory structure with worker categories (`ingestion/`, `extraction/`, `geocoding/`, `clustering/`, `summarization/`).
- Establish `frontend/` directory structure separating components, layouts, hooks, and services.
- Provide a root `Makefile` or package runner script for common developer commands (`build`, `test`, `lint`, `format`).

### MUST NOT
- Implement application business logic or domain models.
- Split the repository into separate git repositories or microservice network boundaries.
- Introduce extraneous build tools or non-standard directory structures.

## Architecture Constraints
- Conforms strictly to ADR-001: Modular Monolith + Async Workers.
- Enforce strict separation between API application runtime and worker process runtimes while sharing the core domain libraries.

## Implementation Requirements
- Initialize backend workspace root with configuration files.
- Initialize frontend workspace root.
- Ensure all modules documented in `docs/03-backend-architecture.md` have their directory scaffolding and placeholder exports in place.
- Ensure UTF-8 character encoding and consistent LF/CRLF normalization across environments.

## Security Requirements
- Ensure `.gitignore` explicitly prevents committing `.env`, `.env.*.local`, secret keys, credentials, local databases, and temporary artifacts.
- Verify npm/pip/poetry audit configuration to prevent check-in of known vulnerable packages.

## Performance Requirements
- Tooling setup must support fast incremental linting and testing (< 10s for baseline check).

## Testing Requirements
- Provide verification script checking that directory structure matches architectural specification.
- Lint and format check commands must execute and pass cleanly on empty project structure.

## Expected Files / Modules
- `backend/app/__init__.py` (or Node/TS equivalent)
- `backend/app/modules/sources/`
- `backend/app/modules/articles/`
- `backend/app/modules/events/`
- `backend/app/modules/locations/`
- `backend/app/modules/clustering/`
- `backend/app/modules/search/`
- `backend/app/modules/analytics/`
- `backend/app/modules/admin/`
- `backend/app/common/`
- `workers/ingestion/`
- `workers/extraction/`
- `workers/geocoding/`
- `workers/clustering/`
- `workers/summarization/`
- `frontend/src/`
- `.gitignore`
- `.editorconfig`
- `README.md`

## Acceptance Criteria
- [x] Directory layout matches `docs/03-backend-architecture.md` verbatim.
- [x] Running format and lint checks from project root succeeds.
- [x] `.gitignore` prevents staging sensitive local files and credentials.
- [x] Clean boundary between backend modular monolith, async workers, and frontend responsive web app.

## Completion Report
When completed, report:
1. Directory structure created.
2. Configuration files added.
3. Lint and format commands verified.
4. Assumptions made regarding runtime version pinning.

## Follow-up Tasks
- TASK-002 (Environment Configuration)
- TASK-003 (Database Foundation)
- TASK-006 (Backend Modular Monolith Foundation)
- TASK-008 (Frontend Responsive Foundation)
