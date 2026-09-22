# TASK-003 — Database Foundation (PostgreSQL + PostGIS + pgvector Setup)

## Status
DONE

## Priority
P0

## Phase
Phase 0 — Foundation

## Depends On
- TASK-001
- TASK-002

## Objective
Configure the primary database connection, initialize PostgreSQL with required PostGIS and optional pgvector extensions, establish the database migration framework (e.g., Alembic or Flyway/Prisma), and implement connection pooling and health checks.

## Source of Truth
- `AGENTS.md` (Source of truth hierarchy, Architecture constraints)
- `docs/04-data-architecture.md` (Primary database, Geospatial)
- `docs/11-performance-scalability.md` (Database performance)
- `docs/17-deployment.md` (Database migration)
- `adr/002-postgres-postgis.md`

## Scope

### MUST
- Set up database migration tooling with support for forward and rollback migrations.
- Create initial migration that enables required PostgreSQL extensions:
  - `postgis` (mandatory for spatial queries and geometry types)
  - `pgcrypto` or `uuid-ossp` (for UUID generation)
  - `pgvector` (optional vector search extension setup for future embedding similarity)
- Implement database session manager and connection pooling with configurable pool size, max overflow, and connection timeout.
- Implement database liveness and readiness health check probe (`SELECT 1`).
- Enforce UTC timestamp storage convention for all upcoming tables.

### MUST NOT
- Bypass migrations using ad-hoc raw DDL scripts executed outside the migration runner.
- Expose direct database access to the public internet.
- Implement destructive migration steps without rollback safety.

## Architecture Constraints
- Conforms strictly to ADR-002: PostgreSQL + PostGIS as Primary Data Store.
- The modular monolith and all async workers share this PostgreSQL cluster in development/MVP.

## Implementation Requirements
- Initialize migration directory (`backend/migrations/` or `backend/alembic/`).
- Provide base migration script activating `postgis` and `uuid-ossp` extensions.
- Configure connection pool:
  - Default pool min: 5, max: 20 connections.
  - Connection recycling/keep-alive to avoid stale sockets.
  - Query execution timeout guards.
- Implement reusable DB session dependency for API request lifecycles.

## Security Requirements
- Database connection strings must be passed via environment variables (`DATABASE_URL`).
- Database user must follow least-privilege principles (separate migration user if applicable).
- SSL/TLS mode must be configurable (`sslmode=require` in production).

## Performance Requirements
- Connection acquisition latency < 10ms under normal pool load.
- Health check query must return in < 50ms.

## Testing Requirements
- Integration test executing against an active PostgreSQL + PostGIS container:
  - Runs forward migration and verifies extensions `postgis` and `uuid-ossp` are active.
  - Runs rollback migration and ensures clean state.
  - Tests database connection pool under concurrent simulated acquisition.
  - Tests DB health check returns healthy when DB is up and fails gracefully when DB is down.

## Expected Files / Modules
- `backend/app/common/db/connection.py` (or TS equivalent)
- `backend/app/common/db/health.py`
- `backend/alembic.ini` (or migration runner config)
- `backend/migrations/versions/0001_initial_extensions.py`
- `tests/integration/test_db_foundation.py`

## Acceptance Criteria
- [x] PostGIS extension is successfully loaded and verified via `SELECT PostGIS_Version()`.
- [x] Migration runner successfully applies and rolls back extension migration.
- [x] Database connection pool properly handles connection checkout and release.
- [x] Automated integration test against live PostgreSQL passes cleanly.

## Completion Report
When completed, report:
1. Migration runner configured.
2. Verified PostGIS and uuid extension activation.
3. Connection pool parameters established.
4. Test execution results.

## Follow-up Tasks
- TASK-004 (Base Database Entity Models & Repositories)
- TASK-006 (Backend Modular Monolith Foundation)
- TASK-009 (Docker Development Environment)
