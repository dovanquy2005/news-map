# TASK-015 — SSRF-Safe HTTP Client & Fetch Policy

## Status
TODO

## Priority
P0

## Phase
Phase 1 — News Ingestion

## Depends On
- TASK-002
- TASK-010
- TASK-013

## Objective
Implement a hardened, centralized HTTP fetch client for news crawling and feed ingestion that rigorously defends against Server-Side Request Forgery (SSRF), DNS rebinding, infinite redirect loops, oversized responses, and slow-loris connection holding.

## Source of Truth
- `AGENTS.md` (Security by default)
- `docs/05-ingestion-pipeline.md` (Fetch policy, Never)
- `docs/10-security.md` (SSRF, Resource limits)

## Scope

### MUST
- Implement centralized HTTP fetch client wrapper (using `httpx`, `aiohttp`, or `urllib3`):
  - Strict HTTPS scheme enforcement (reject `http://` unless explicitly allowlisted in local dev).
  - Pre-request DNS resolution and IP address validation:
    - Reject all private IPv4/IPv6 ranges: `127.0.0.0/8`, `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `169.254.0.0/16` (cloud link-local metadata `169.254.169.254`), `::1`, `fc00::/7`, `fe80::/10`.
    - Mitigate DNS rebinding: verify the resolved IP immediately before connecting or pin socket connection to the verified IP.
  - Domain allowlisting: URL domain must match or be a subdomain of an active registered `Source` domain.
  - Redirect handling: manual redirect following (max 3 redirects) with re-validation of destination IP and domain on each redirect hop.
  - Timeouts: bounded connect timeout (<= 5s) and read timeout (<= 15s).
  - Response size limit: stream and abort if response body exceeds 5MB to prevent memory exhaustion.
  - Custom User-Agent identifying the Vietnam News Map bot with contact / info URL.
  - Concurrency limiter per domain (e.g. max 2 concurrent requests per publisher domain).

### MUST NOT
- Allow fetching arbitrary user-supplied URLs.
- Allow access to AWS/GCP/Azure instance metadata endpoints (`169.254.169.254`).
- Disable SSL/TLS certificate verification in staging or production.
- Permit infinite redirect chains or cross-protocol redirects (e.g. `https` -> `file` or `gopher`).

## Architecture Constraints
- Conforms to `docs/10-security.md` SSRF defense specifications.
- Every outgoing fetch from ingestion workers and adapters must route through this client.

## Implementation Requirements
- Create `backend/app/common/security/http_client.py` and `workers/common/safe_fetch.py`.
- Implement custom transport / resolver hook for IP validation.
- Implement token bucket or semaphore for per-domain concurrency throttling.
- Provide async method: `safe_fetch(url: str, source_domain: str, headers: Optional[dict] = None) -> SafeFetchResponse`.

## Security Requirements
- Tested against OWASP SSRF test cases and cloud metadata exfiltration vectors.
- Blocked SSRF attempts must be logged as high-priority security events with client IP and target URL.

## Performance Requirements
- DNS validation overhead < 15ms.
- Memory streaming footprint < 10MB per concurrent request.

## Testing Requirements
- Comprehensive security regression tests:
  - Attempt fetch to `http://localhost:8000` -> blocked with SSRF exception.
  - Attempt fetch to `http://169.254.169.254/latest/meta-data/` -> blocked.
  - Attempt fetch to internal IP `10.0.0.1` -> blocked.
  - Test domain mismatch: URL `https://attacker.com/rss` when expected domain is `vnexpress.net` -> blocked.
  - Test redirect to internal IP: external server redirecting to `http://127.0.0.1` -> blocked on second hop.
  - Test oversized payload: mock server returning 10MB payload -> aborted at 5MB threshold.
  - Test valid allowed external HTTPS request -> succeeds and returns content.

## Expected Files / Modules
- `backend/app/common/security/http_client.py`
- `backend/app/common/security/ip_validator.py`
- `workers/common/safe_fetch.py`
- `tests/security/test_ssrf_protection.py`

## Acceptance Criteria
- [ ] Centralized fetch client blocks all private, loopback, and cloud metadata IPs.
- [ ] Redirect validation prevents SSRF via redirect evasion.
- [ ] Domain allowlist checks enforce adherence to registered source domains.
- [ ] Automated security tests pass 100% of negative SSRF test cases.

## Completion Report
When completed, report:
1. HTTP client architecture and IP verification logic.
2. Redirect handling and limit configurations.
3. Domain concurrency limiter implementation.
4. Security test results for all SSRF attack vectors.

## Follow-up Tasks
- TASK-016 (RSS Feed Adapter Implementation)
- TASK-019 (Article Ingestion Worker Pipeline)
- TASK-048 (Security Hardening & ASVS Verification)
