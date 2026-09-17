# TASK-043 — Admin Authentication & Authorization Module

## Status
TODO

## Priority
P0

## Phase
Phase 1 — Trust & Operations

## Depends On
- TASK-002
- TASK-004
- TASK-006
- TASK-010

## Objective
Implement secure authentication and role-based access control (RBAC) protecting the `/api/v1/admin/*` API namespace, featuring secure token/cookie session handling, password hashing via Argon2/Bcrypt, brute-force rate limiting, and server-side authorization checks conforming to `docs/10-security.md`.

## Source of Truth
- `AGENTS.md` (Security by default: broken authorization)
- `docs/03-backend-architecture.md` (Module ownership: admin, Layering)
- `docs/09-api-contracts.md` (Admin APIs: /api/v1/admin/*)
- `docs/10-security.md` (Authentication / authorization, API security)

## Scope

### MUST
- Implement admin user entity and repository:
  - `AdminUser`: `id`, `username`, `email`, `password_hash`, `role` (`SUPERADMIN`, `OPERATOR`, `REVIEWER`), `is_active`, `last_login_at`, `created_at`, `updated_at`.
- Implement secure password hashing using Argon2id or Bcrypt (cost factor >= 12).
- Implement admin authentication endpoints:
  - `POST /api/v1/admin/auth/login`: verifies credentials, issues secure JWT token or `HttpOnly; Secure; SameSite=Lax/Strict` session cookie.
  - `POST /api/v1/admin/auth/logout`: invalidates session token via Redis denylist.
  - `GET /api/v1/admin/auth/me`: returns authenticated admin profile and role.
- Implement server-side authorization dependency (`require_admin_role(...)`):
  - Check role server-side on every admin request; reject unauthorized requests with HTTP 403 `FORBIDDEN`.
  - Enforce deny-by-default on all routes mounted under `/api/v1/admin/`.
- Protect login endpoint against brute-force attacks:
  - IP and username-based rate limiting (max 5 failed attempts per 15 minutes, followed by lockout).
  - Constant-time password comparison to prevent timing attacks.
- Log security events: login success, login failure, unauthorized access attempts (with IP and correlation ID, zero passwords logged).

### MUST NOT
- Trust frontend role flags or client-side permission claims.
- Use insecure JWT algorithms (e.g. `none`) or weak secrets.
- Allow wildcard CORS origins for admin endpoints.
- Return password hashes or internal security tokens in user profiles.

## Architecture Constraints
- Conforms to `docs/10-security.md`: Deny by default, role checks server-side, least privilege.
- Admin APIs strictly isolated under `/api/v1/admin/*`.

## Implementation Requirements
- Create `backend/app/modules/admin/auth/`
  - `models.py`
  - `schemas.py`
  - `service.py`
  - `dependencies.py`
  - `router.py`
- Password hashing utility using `passlib` / `argon2-cffi`.
- Redis token revocation denylist with TTL matching token expiry.

## Security Requirements
- JWT signed with asymmetric key (RS256) or strong HMAC (HS256 with 256-bit secret from `ADMIN_JWT_SECRET`).
- Short access token lifetime (15-30 minutes); refresh tokens stored securely in Redis.
- Rate limiter middleware bound to `POST /api/v1/admin/auth/login`.

## Performance Requirements
- Token verification overhead < 2ms per request.
- Password hashing computation calibrated to ~250ms (Argon2 / Bcrypt).

## Testing Requirements
- Security and API tests:
  - Successful login returns valid token and sets secure cookie.
  - Incorrect password fails with 401 `INVALID_CREDENTIALS`.
  - 5 consecutive failed logins trigger 429 `ACCOUNT_LOCKED`.
  - Accessing `/api/v1/admin/sources` without token returns 401 `UNAUTHORIZED`.
  - Accessing superadmin route with `REVIEWER` role returns 403 `FORBIDDEN`.
  - Logout invalidates token; subsequent requests with the same token are rejected.
  - Timing attack test: failed attempt with non-existent username takes approximately the same time as existing username.

## Expected Files / Modules
- `backend/app/modules/admin/auth/models.py`
- `backend/app/modules/admin/auth/schemas.py`
- `backend/app/modules/admin/auth/service.py`
- `backend/app/modules/admin/auth/dependencies.py`
- `backend/app/modules/admin/auth/router.py`
- `backend/app/common/security/password.py`
- `tests/api/test_admin_auth.py`

## Acceptance Criteria
- [ ] Admin authentication and RBAC guard `/api/v1/admin/*` endpoints strictly.
- [ ] Passwords stored using modern Argon2id or Bcrypt hashes.
- [ ] Brute-force rate limiting locks out attackers after consecutive failures.
- [ ] Token revocation on logout prevents token reuse.
- [ ] Automated security tests verify all access control and authentication boundaries.

## Completion Report
When completed, report:
1. Admin authentication architecture and token handling.
2. RBAC dependency structure and role matrix.
3. Brute-force protection and lockout thresholds.
4. Security test results for auth boundaries.

## Follow-up Tasks
- TASK-044 (Admin Source Monitor API & UI)
- TASK-045 (Admin Processing Monitor API & UI)
- TASK-046 (Admin Review Queue & Audit Log)
- TASK-048 (Security Hardening & ASVS Verification)
