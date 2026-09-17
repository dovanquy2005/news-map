# Security Architecture

## Security baseline

Use OWASP ASVS 5.0 as the application-security verification baseline. OWASP describes ASVS as a requirements basis for secure development and verification. 

Use the OWASP API Security Top 10 as a threat checklist, especially broken authorization, unrestricted resource consumption, SSRF, security misconfiguration, inventory management and unsafe third-party API consumption.

## Edge protection

```text
Internet
  -> CDN
  -> WAF
  -> TLS termination
  -> rate limiting
  -> application
```

Use CDN caching for public GET traffic to reduce origin load.

## API security

### Rate limiting

Separate limits by class:

- anonymous read API;
- search API;
- expensive endpoints;
- admin API;
- authentication endpoints.

Use IP + route + account/API identity when available.

### Resource limits

Always bound:

- page size;
- date range;
- bbox size;
- search length;
- request body size;
- concurrent expensive jobs;
- LLM input tokens;
- crawler concurrency.

## Authentication / authorization

- admin requires authenticated identity;
- role checks server-side;
- object-level authorization for admin resources;
- deny by default;
- least privilege.

Do not trust frontend role flags.

## SSRF

The system processes URLs from news/source configuration. Protect every server-side fetch:

- allowlist known source domains;
- validate URL scheme (`https` only unless explicitly required);
- block localhost/private/link-local/reserved targets;
- re-check resolved IP to prevent DNS rebinding;
- disable arbitrary redirect chains or validate every redirect;
- strict connect/read timeouts;
- bounded response size.

User-supplied URLs must never become arbitrary backend fetch targets.

## XSS

Treat article titles, excerpts and external metadata as untrusted.

- output encode by context;
- avoid raw HTML injection;
- sanitize rich text if ever required;
- use strict CSP where compatible.

## SQL injection

Use parameterized queries/ORM safely.

Never build SQL by string concatenation from user filters.

## Secrets

- environment variables in development only;
- production secret manager;
- never commit keys;
- no secrets in client bundle except intentionally public restricted browser credentials;
- rotate exposed/compromised credentials.

## Google Maps key

For browser Maps usage, use a browser-restricted key limited to the required APIs and authorized web origins. Separate client/browser keys from server-side keys. Google recommends restricting keys, using separate keys per application, monitoring usage and keeping web-service secrets server-side. citeturn179242search0

## CORS

Allow only known production/dev origins.

Do not use wildcard CORS for authenticated/admin APIs.

## Browser security headers

At minimum evaluate:

- HSTS;
- CSP;
- X-Content-Type-Options;
- Referrer-Policy;
- Permissions-Policy;
- frame/embedding restrictions as appropriate.

## Cookies/session

If cookie-based auth is used:

- Secure;
- HttpOnly;
- SameSite appropriate to architecture;
- CSRF protection for state-changing requests.

## AI security

Article content is untrusted input. Never allow article text to override system/developer instructions.

LLM output must pass schema and business validation.

Do not expose internal prompts, secrets or tool credentials to the model context.

## Supply chain

- lock dependency versions where practical;
- automated dependency scanning;
- review high-risk packages;
- no random abandoned packages for simple functions.

## Logging

Log security events without secrets.

Examples:

- auth failure;
- admin access;
- rate-limit trigger;
- blocked SSRF;
- invalid LLM schema output;
- source adapter failure.

## Security testing

Before production:

- SAST;
- dependency audit;
- API authorization tests;
- SSRF tests;
- XSS tests;
- rate-limit tests;
- secret scanning;
- basic DAST/security regression.

“Chống tấn công” là mục tiêu phòng thủ nhiều lớp, không phải cam kết hệ thống không thể bị tấn công.
