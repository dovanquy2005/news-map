# Deployment & Environment Strategy

## Environments

```text
local
staging
production
```

Do not develop directly against production database.

## Deployment units

MVP:

```text
web
api
worker
scheduler
postgres
redis
```

Can share a repository and deploy independently.

## Network

```text
Public:
 CDN/WAF
 Web
 API edge

Private:
 API runtime
 Worker
 PostgreSQL
 Redis
 Secret manager
```

## CI/CD gates

Pull request:

- format/lint;
- typecheck;
- unit tests;
- integration tests where feasible;
- secret scan;
- dependency vulnerability scan.

Production:

- build immutable artifact;
- run migration safely;
- health checks;
- rollback plan;
- smoke tests.

## Database migration

Migrations must be backward compatible when rolling deployments can run old and new app versions concurrently.

Avoid destructive migration in the same release as code that still depends on the old schema.

## Health endpoints

Separate:

- liveness;
- readiness;
- dependency health.

Do not expose sensitive diagnostics publicly.
