# TASK-048 — Security Hardening & OWASP ASVS Verification

## Status
TODO

## Priority
P0

## Phase
Phase 1 — Trust & Operations

## Depends On
- TASK-006
- TASK-010
- TASK-015
- TASK-020
- TASK-043
- TASK-047

## Objective
Execute end-to-end security hardening, verify compliance against the OWASP ASVS 5.0 baseline and OWASP API Security Top 10 checklist, configure strict Content Security Policy (CSP) and HTTP security headers, and implement automated security regression tests across SQLi, XSS, SSRF, broken authorization, prompt injection, and rate limiting.

## Source of Truth
- `AGENTS.md` (Security by default)
- `docs/10-security.md` (Security baseline, Edge protection, API security, SSRF, XSS, SQL injection, Secrets, Google Maps key, Security testing)
- `docs/14-testing-qa.md` (Security regression)

## Scope

### MUST
- Implement multi-class rate limiting using Redis token bucket:
  - Class 1: Anonymous public read API (`GET /api/v1/events`): 60 req/min per IP.
  - Class 2: Search API (`GET /api/v1/events/search`): 20 req/min per IP.
  - Class 3: Admin auth (`POST /api/v1/admin/auth/login`): 5 failed attempts per 15 min per IP/username.
  - Class 4: Admin API (`/api/v1/admin/*`): 120 req/min per admin identity.
  - Return standardized 429 response envelope with `Retry-After` header.
- Enforce strict browser security headers:
  - `Content-Security-Policy`:
    - `default-src 'self'`;
    - `script-src 'self' https://maps.googleapis.com`;
    - `style-src 'self' 'unsafe-inline' https://fonts.googleapis.com`;
    - `img-src 'self' data: https://maps.gstatic.com https://*.googleapis.com`;
    - `connect-src 'self' https://maps.googleapis.com`;
    - `frame-ancestors 'none'`;
  - `Strict-Transport-Security: max-age=63072000; includeSubDomains; preload`
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `Referrer-Policy: strict-origin-when-cross-origin`
  - `Permissions-Policy: geolocation=(), camera=(), microphone=()`
- Request body and header size bounds:
  - Request body max size: 2MB for general APIs, 5MB for feed parser.
  - Header size max: 16KB to mitigate HTTP Request Smuggling.
- Comprehensive security test suite covering:
  - SQL Injection: Automated injection payloads on all filter parameters (`bbox`, `province`, `category`, `status`, `from`, `to`).
  - Cross-Site Scripting (XSS): Malicious payloads in article titles, location names, and fact texts must not execute or render unescaped in responses.
  - SSRF Protection: Verified test suite from TASK-015 incorporated into main CI security gate.
  - Broken Object-Level Authorization (BOLA): Attempting to modify another admin user or unauthorized resource.
  - Prompt Injection: Adversarial injection payloads into LLM extraction and summarization prompts.
  - Secret Scanning: Zero secrets committed in repo or leaked in API responses.

### MUST NOT
- Use permissive `unsafe-eval` in Content Security Policy.
- Disable SSL/TLS validation or rate-limiting in production environments.
- Trust client-supplied IP headers (`X-Forwarded-For`) unless validated against trusted proxy IP CIDRs.

## Architecture Constraints
- Conforms strictly to `docs/10-security.md`: OWASP ASVS 5.0 as baseline; OWASP API Security Top 10 threat checklist.
- Security defense-in-depth: Edge + API middleware + domain sanitization + database query parameterization.

## Implementation Requirements
- Create `backend/app/common/security/rate_limiter.py` and `backend/app/common/middleware/security.py`.
- Configure trusted proxy middleware: accurately extracts client IP from `X-Forwarded-For` only when direct peer is an allowlisted reverse proxy / CDN CIDR.
- Security test suite: `tests/security/`.

## Security Requirements
- All ASVS Level 1 & Level 2 applicable requirements satisfied.
- Vulnerability scans (SAST + dependency scan) must report 0 High or Critical vulnerabilities.

## Performance Requirements
- Rate limiter middleware check overhead < 1.5ms using atomic Redis pipeline (`INCR` + `EXPIRE`).
- Security header injection adds < 0.1ms to response processing.

## Testing Requirements
- Automated security regression test suite (`tests/security/`):
  - `test_sqli.py`: 50+ standard SQL injection vectors tested against `/api/v1/events` and `/api/v1/events/search`.
  - `test_xss.py`: Payload `<script>alert(1)</script>` in article text is sanitized.
  - `test_rate_limits.py`: Sending 65 rapid requests to public API results in HTTP 429 on the 61st request with valid `Retry-After`.
  - `test_security_headers.py`: All responses contain HSTS, CSP, X-Content-Type-Options, X-Frame-Options.
  - `test_admin_bola.py`: Low-privilege admin cannot modify higher-privilege admin accounts.

## Expected Files / Modules
- `backend/app/common/security/rate_limiter.py`
- `backend/app/common/middleware/security.py`
- `backend/app/common/security/trusted_proxy.py`
- `tests/security/test_sqli.py`
- `tests/security/test_xss.py`
- `tests/security/test_rate_limits.py`
- `tests/security/test_security_headers.py`
- `tests/security/test_admin_bola.py`

## Acceptance Criteria
- [ ] Multi-class rate limiting correctly enforces IP and identity-based quotas.
- [ ] Strict CSP and modern HTTP security headers present on all responses.
- [ ] Trusted proxy middleware accurately parses client IPs without spoofing vulnerability.
- [ ] 100% of automated security regression tests (SQLi, XSS, SSRF, BOLA, rate-limits) pass cleanly.

## Completion Report
When completed, report:
1. Rate limiting architecture and quotas per endpoint class.
2. Content Security Policy and HTTP security header configuration.
3. Trusted proxy IP validation mechanism.
4. Security test execution results across all OWASP attack vectors.

## Follow-up Tasks
- TASK-049 (End-to-End Critical Flow Validation)
- TASK-050 (Phase 1 Production Readiness & Runbook)
