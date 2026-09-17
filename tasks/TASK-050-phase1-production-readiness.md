# TASK-050 — Phase 1 MVP Production Readiness & Operational Runbook

## Status
TODO

## Priority
P0

## Phase
Phase 1 — Trust & Operations

## Depends On
- TASK-012
- TASK-041
- TASK-044
- TASK-045
- TASK-047
- TASK-048
- TASK-049

## Objective
Finalize Phase 1 MVP production deployment configurations, database connection pool tuning, automated backup/restore validation, health check probes, smoke tests, and the operational incident response runbook.

## Source of Truth
- `AGENTS.md` (Definition of done)
- `docs/11-performance-scalability.md` (Worker scaling, Backpressure)
- `docs/17-deployment.md` (Production deployment, Health endpoints, Rollback plan)
- `prd.md` (Section 34: MVP Scope Definition, Section 35: MVP Acceptance Criteria)

## Scope

### MUST
- Production container build configuration:
  - Multi-stage minimal production Dockerfiles (`api`, `worker`, `web`) with non-root runtime users.
  - Production static frontend asset build with cache-busting content hashes.
- Database and Cache Production Hardening:
  - Connection pool sizing tuned to worker and API replica counts (`pool_size=20`, `max_overflow=10`).
  - Automated database backup script (`pg_dump` with encryption and S3/object storage upload).
  - Validated restore procedure documented and tested against a blank staging database.
- Health Probes and Alerting Configuration:
  - Independent liveness (`/healthz`) and readiness (`/readyz`) probes.
  - Alert definitions for Prometheus / Alertmanager:
    - Source stale > 6 hours.
    - Redis queue depth > 1,000 for > 15 minutes.
    - 5xx error rate > 1% over 5 minutes.
    - PostGIS query P95 latency > 1,000ms.
- Production Deployment Smoke Tests:
  - Automated smoke test script verifying post-deployment health, database connectivity, and sample API queries before switching traffic.
- Operational Runbook:
  - Document procedures for:
    - Adding/disabling a news source.
    - Handling external LLM API outages or rate limits (backpressure management).
    - Recovering from failed database migrations with zero-downtime rollback.
    - Purging and reprocessing the Dead-Letter Queue.

### MUST NOT
- Deploy to production without verified and tested database restore procedures.
- Expose diagnostic endpoints or internal metrics to unauthenticated public traffic.
- Mark Phase 1 complete without validating the operational runbook.

## Architecture Constraints
- Conforms strictly to `docs/17-deployment.md`: deployment units are web, api, worker, scheduler, postgres, redis.
- Zero microservice extraction needed; modular monolith topology is fully production ready.

## Implementation Requirements
- Create production deployment configs:
  - `docker/docker-compose.prod.yml` or Kubernetes / cloud deployment manifests.
  - `scripts/backup_db.sh` and `scripts/restore_db.sh`.
  - `scripts/smoke_test.sh`.
- Create operational runbook: `docs/ops/RUNBOOK.md`.

## Security Requirements
- Secret rotation policy and secret injection verified for production runtime.
- Least-privilege PostgreSQL user credentials configured for API vs Migration runners.

## Performance Requirements
- Smoke test execution < 30 seconds.
- Database restore from snapshot verified in < 5 minutes for MVP dataset.

## Testing Requirements
- Operational verification:
  - Execute backup script -> produces encrypted dump.
  - Execute restore script against test instance -> verifies 100% data integrity and table counts.
  - Execute smoke test script against production build -> verifies 200 OK across public endpoints.
  - Test liveness probe: terminating Redis temporarily causes readiness probe to fail while liveness probe remains alive.

## Expected Files / Modules
- `docker/docker-compose.prod.yml`
- `scripts/backup_db.sh`
- `scripts/restore_db.sh`
- `scripts/smoke_test.sh`
- `docs/ops/RUNBOOK.md`
- `docs/ops/alert_rules.yml`

## Acceptance Criteria
- [ ] Production build configurations pass all security, non-root, and optimization checks.
- [ ] Database backup and restore procedures are tested and documented.
- [ ] Smoke test script validates deployment health automatically.
- [ ] Operational runbook covers all standard incident management procedures.
- [ ] Phase 1 MVP is officially production-ready and fully operational.

## Completion Report
When completed, report:
1. Production container images and build optimization.
2. Verified database backup and restore test run.
3. Smoke test script results.
4. Operational runbook location and covered incident workflows.

## Follow-up Tasks
- TASK-051 (Phase 2 Trend Engine initiation)
