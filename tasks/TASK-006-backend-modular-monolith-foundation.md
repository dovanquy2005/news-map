# TASK-006 — Backend Modular Monolith Foundation

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
Implement the backend application runtime framework (e.g. FastAPI / NestJS) with strict module routing, standardized response envelopes, centralized error handling, correlation ID middleware, CORS policies, and healthcheck endpoints according to `docs/03-backend-architecture.md` and `docs/09-api-contracts.md`.

## Source of Truth
- `docs/02-system-architecture.md` (Modular monolith, Trust boundaries)
- `docs/03-backend-architecture.md` (Style, Layering, Error handling)
- `docs/09-api-contracts.md` (Base /api/v1, Response rules)
- `docs/10-security.md` (CORS, Security headers)
- `docs/15-dev-conventions.md` (Errors, IDs, Time)
- `adr/001-modular-monolith.md`

## Scope

### MUST
- Initialize the application server with modular routing under prefix `/api/v1`.
- Implement Correlation ID / Request ID middleware attaching `X-Request-ID` to request context and response headers.
- Implement standardized JSON error response schema:
  ```json
  {
    "error": {
      "code": "ERROR_CODE",
      "message": "Human-readable explanation",
      "details": {}
    }
  }
  ```
- Implement centralized exception handlers for validation errors (422/400), authentication/authorization errors (401/403), resource not found (404), rate limit exceeded (429), and unhandled server errors (500).
- Strip internal exception details and stack traces from production error responses.
- Implement CORS middleware with explicit domain allowlisting from environment configuration.
- Implement `/healthz` (liveness) and `/readyz` (readiness checking DB and Redis connections).

### MUST NOT
- Put business logic inside API controllers or route handlers; delegate to domain/application services.
- Expose internal database stack traces or SQL error text to clients.
- Allow wildcard `*` CORS origin when credentials or admin cookies are involved.

## Architecture Constraints
- Conforms to ADR-001: Modular Monolith architecture.
- Follows the layering model: `Controller -> Application Service -> Domain Rules -> Repository`.

## Implementation Requirements
- Set up application factory with route mounting for all modules:
  - `/api/v1/events`
  - `/api/v1/sources`
  - `/api/v1/admin`
- Ensure all timestamps returned by endpoints are formatted in ISO 8601 UTC.
- Enforce JSON body parser limits (< 2MB) to prevent memory denial-of-service.

## Security Requirements
- Add standard HTTP security headers: `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin`.
- Restrict allowed HTTP methods per endpoint.
- Mask sensitive header values (Authorization, Cookie) from logs.

## Performance Requirements
- Middleware processing overhead < 2ms per request.
- Healthcheck endpoint `/healthz` responds in < 5ms.

## Testing Requirements
- API unit and integration tests:
  - Verify `/healthz` returns 200 OK.
  - Verify `/readyz` checks DB and Redis status accurately.
  - Verify `X-Request-ID` is generated when omitted and preserved when provided.
  - Verify custom business exceptions produce the standardized error JSON schema with appropriate HTTP status codes.
  - Verify unhandled server errors return generic 500 error without exposing stack traces.
  - Verify CORS middleware headers for allowed vs forbidden origins.

## Expected Files / Modules
- `backend/app/main.py`
- `backend/app/common/errors/exceptions.py`
- `backend/app/common/errors/handlers.py`
- `backend/app/common/middleware/correlation.py`
- `backend/app/common/middleware/security_headers.py`
- `backend/app/api/router.py`
- `backend/app/api/health.py`
- `tests/api/test_app_foundation.py`

## Acceptance Criteria
- [x] Application successfully initializes with modular routing prefix `/api/v1`.
- [x] Correlation ID middleware correctly propagates `X-Request-ID` across inbound requests and outbound responses.
- [x] Centralized error handlers format all errors into the standardized JSON envelope.
- [x] `/healthz` and `/readyz` endpoints return correct status codes matching subsystem health.

## Completion Report
When completed, report:
1. Application router setup.
2. Middleware chain configured.
3. Standardized error structure verified.
4. Test results for foundational endpoints.

## Follow-up Tasks
- TASK-010 (Observability Foundation)
- TASK-032 (Public Events API)
- TASK-043 (Admin Authentication & Authorization)
