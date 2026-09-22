# TASK-009 — Docker Development Environment

## Status
DONE

## Priority
P0

## Phase
Phase 0 — Foundation

## Depends On
- TASK-001
- TASK-002
- TASK-003
- TASK-005

## Objective
Create the local Docker Compose development environment orchestrating PostgreSQL (with PostGIS and pgvector), Redis, backend API, async worker, and frontend services with health checks and volume persistence.

## Source of Truth
- `docs/02-system-architecture.md` (Runtime topology)
- `docs/17-deployment.md` (Environments, Deployment units, Network)
- `adr/001-modular-monolith.md`
- `adr/002-postgres-postgis.md`

## Scope

### MUST
- Provide `docker-compose.yml` defining services:
  - `postgres`: image with PostGIS 3.x pre-installed (e.g. `postgis/postgis:16-3.4`), healthcheck, persistent volume.
  - `redis`: image `redis:7-alpine`, healthcheck, persistent volume.
  - `api`: backend container with hot reload mounted, healthcheck on `/healthz`.
  - `worker`: worker container with hot reload mounted, executing background queue dispatchers.
  - `frontend`: web development server with hot module replacement (HMR).
- Implement Docker network isolating backend datastores from host exposure where desired while enabling inter-service DNS resolution (`postgres:5432`, `redis:6379`).
- Ensure container startup dependency ordering using `depends_on` with `condition: service_healthy`.
- Include seed script hook for test/development data bootstrap.

### MUST NOT
- Expose production secrets in docker-compose environment blocks.
- Run containers as root in Dockerfiles; define unprivileged runtime user.
- Hardcode host paths outside the project repository.

## Architecture Constraints
- Conforms to `docs/17-deployment.md`: deployment units are web, api, worker, postgres, redis.
- Same container images can be promoted to staging with production entrypoint override.

## Implementation Requirements
- Dockerfiles:
  - `docker/Dockerfile.backend`: Multi-stage build (builder and slim runtime).
  - `docker/Dockerfile.worker`: Shared base with backend but distinct entrypoint (`runner.py`).
  - `docker/Dockerfile.frontend`: Node/Vite development server.
- Compose setup:
  - Named volumes for PostgreSQL data (`vnm_pgdata`) and Redis (`vnm_redisdata`).
  - Environment variables loaded from `.env`.

## Security Requirements
- Database and Redis ports exposed to host only for local debugging (bind to `127.0.0.1`).
- Non-root user `appuser` (UID 1001) used in Dockerfiles.
- `.dockerignore` files excluding `.git`, `.env*`, `node_modules`, `__pycache__`.

## Performance Requirements
- Local `docker compose up` starts all healthy services in < 45s from warm build cache.

## Testing Requirements
- Verification script / integration test:
  - Validates `docker compose config` syntax.
  - Executes container healthcheck probes verifying all 5 services report healthy.
  - Verifies database and redis persistence across container restart (`docker compose restart`).

## Expected Files / Modules
- `docker-compose.yml`
- `docker/Dockerfile.backend`
- `docker/Dockerfile.worker`
- `docker/Dockerfile.frontend`
- `docker/.dockerignore`
- `docker/seed/init.sql`

## Acceptance Criteria
- [x] Docker environment config validates cleanly via `docker compose config`.
- [x] Multi-service topology includes postgres, redis, api, and worker containers.
- [x] Code directories mount properly for live code reload without container rebuilds.
- [x] Healthchecks ensure proper startup ordering between database and applications.

## Completion Report
When completed, report:
1. Docker compose configuration created.
2. Verified Dockerfiles for backend, worker, and frontend.
3. Health check configurations.
4. Local startup and persistence verification.

## Follow-up Tasks
- TASK-011 (Testing Harness & QA Foundation)
- TASK-012 (CI/CD Pipeline & Quality Gates)
