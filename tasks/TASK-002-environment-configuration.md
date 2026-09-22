# TASK-002 — Environment Configuration & Secret Management Scheme

## Status
DONE

## Priority
P0

## Phase
Phase 0 — Foundation

## Depends On
- TASK-001

## Objective
Implement a unified, typed configuration management layer across backend and workers that reads environment variables, validates required parameters at startup, supports distinct environments (local, staging, production), and prevents secret leakage.

## Source of Truth
- `AGENTS.md` (Security by default, Logging)
- `docs/10-security.md` (Secrets management)
- `docs/15-dev-conventions.md` (Configuration conventions)
- `docs/17-deployment.md` (Environment strategy)

## Scope

### MUST
- Create typed configuration schemas for backend, workers, and frontend.
- Support runtime environment switching: `local`, `staging`, `production`.
- Provide `.env.example` templates documenting all required and optional environment keys with descriptive comments and placeholder values.
- Enforce strict fail-fast validation at application startup: if required secrets (e.g. database credentials, Redis URL) are missing or malformed, the process exits with an informative error.
- Redact secrets from configuration dumps, debug prints, and structured logging.

### MUST NOT
- Commit real secrets, credentials, production tokens, or private API keys into version control.
- Hard-code fallback secrets for production environments.
- Expose server-side configuration variables to the client-side frontend bundle.

## Architecture Constraints
- Conforms to 12-factor application configuration principles.
- Server-side and worker runtimes read directly from process environment; client-side variables must be explicitly prefixed (e.g., `NEXT_PUBLIC_` or `VITE_`) and limited to browser-safe parameters (e.g., `MAPS_BROWSER_KEY`).

## Implementation Requirements
- Define configuration variables:
  - Database: `DATABASE_URL`, `DB_POOL_MIN`, `DB_POOL_MAX`, `DB_TIMEOUT_MS`
  - Redis: `REDIS_URL`, `REDIS_MAX_CONNECTIONS`
  - Maps: `MAPS_BROWSER_KEY` (public), `MAPS_SERVER_KEY` (private)
  - LLM / NLP: `LLM_API_KEY`, `LLM_MODEL_NAME`, `LLM_TIMEOUT_MS`, `LLM_MAX_TOKENS`
  - App / Server: `APP_ENV`, `PORT`, `LOG_LEVEL`, `CORS_ALLOWED_ORIGINS`
  - Security / Rate Limiting: `RATE_LIMIT_ANONYMOUS_RPS`, `RATE_LIMIT_SEARCH_RPS`, `RATE_LIMIT_ADMIN_RPS`
  - Admin Auth: `ADMIN_JWT_SECRET`, `ADMIN_SESSION_TTL_HOURS`
- Implement custom string masking for sensitive variables when stringified or logged (e.g., `db_password` -> `******`).

## Security Requirements
- All secret fields must be non-empty and non-default when `APP_ENV=production`.
- Browser configuration must strictly exclude `MAPS_SERVER_KEY`, `DATABASE_URL`, `REDIS_URL`, and `LLM_API_KEY`.
- No sensitive configuration may appear in logs or error traces.

## Performance Requirements
- Configuration parsing and validation must complete in < 50ms during application startup.

## Testing Requirements
- Unit tests verifying:
  - Startup succeeds with valid `.env` configuration.
  - Startup fails with informative validation errors when required variables are missing.
  - Config string representation automatically masks passwords, tokens, and keys.
  - Production mode blocks insecure or default secret strings.

## Expected Files / Modules
- `backend/app/common/config.py` (or TypeScript equivalent)
- `backend/.env.example`
- `frontend/.env.example`
- `workers/.env.example`
- `tests/unit/test_config.py`

## Acceptance Criteria
- [x] Application fails fast on launch if required configuration keys are missing.
- [x] `.env.example` covers 100% of required runtime variables with clear instructions.
- [x] Secrets masking functions properly mask passwords and keys in log outputs.
- [x] Frontend config schema strictly prevents server-only secrets from bundling.

## Completion Report
When completed, report:
1. Configuration schema files created.
2. Verified fail-fast validation behavior.
3. List of documented variables in `.env.example`.
4. Tests executed and test pass output.

## Follow-up Tasks
- TASK-003 (Database Foundation)
- TASK-005 (Redis & Queue Foundation)
- TASK-006 (Backend Modular Monolith Foundation)
