# TASK-017 — Article Normalization & Sanitization

## Status
TODO

## Priority
P0

## Phase
Phase 1 — News Ingestion

## Depends On
- TASK-004
- TASK-016

## Objective
Implement the article data normalization and sanitization pipeline that cleans raw feed items, canonicalizes URLs (stripping tracking parameters), parses and converts timestamps to UTC, normalizes whitespace and Unicode text, strips HTML tags from excerpts, and generates content hashes.

## Source of Truth
- `AGENTS.md` (Security by default, Untrusted input)
- `docs/05-ingestion-pipeline.md` (Article normalization)
- `docs/10-security.md` (XSS)
- `docs/15-dev-conventions.md` (Time, Naming)
- `prd.md` (Section 6.2: Article Ingestion)

## Scope

### MUST
- Canonicalize article URLs:
  - Strip tracking and marketing query parameters (`utm_*`, `ref`, `fbclid`, `gclid`, `source`, `campaign`, etc.).
  - Normalize scheme to lowercase `https` and domain to lowercase FQDN.
  - Resolve relative URLs against the source base URL.
  - Strip URL hash fragments (`#...`).
- Normalize timestamps:
  - Parse diverse string timestamps and convert explicitly to timezone-aware UTC datetime.
  - Fall back to `fetched_at` only if published timestamp is completely missing or invalid, with a clear flag in metadata.
- Sanitize and normalize text:
  - Strip raw HTML markup from titles and excerpts using a secure sanitizer (e.g. `bleach` or `sanitize-html`).
  - Normalize Unicode to NFKC (handling Vietnamese accented characters properly).
  - Normalize whitespace (collapse multiple spaces, tabs, newlines into single spaces).
- Generate deterministic content hash:
  - Compute SHA-256 hash over normalized `(title + " " + (content_excerpt or ""))` for deduplication.
- Detect or tag language (default `'vi'` for Vietnamese sources).

### MUST NOT
- Allow unescaped HTML tags (such as `<script>`, `<iframe>`, `<img>`) to remain in normalized title or excerpt fields.
- Overwrite or discard the original raw URL (retain both `url` and `canonical_url`).
- Truncate Vietnamese multi-byte characters improperly.

## Architecture Constraints
- Conforms to `docs/05-ingestion-pipeline.md` normalization step.
- Follows the data model in `docs/04-data-architecture.md` (`Article` entity).

## Implementation Requirements
- Create `backend/app/modules/articles/normalizer.py`.
- URL cleaning utility with comprehensive parameter strip list.
- HTML tag stripping function using HTML parser rather than simple regex to prevent evasion.
- Output model: `NormalizedArticleDTO`:
  - `source_id`: UUID
  - `url`: string (original)
  - `canonical_url`: string (cleaned)
  - `title`: string (cleaned, max 500 chars)
  - `summary_raw`: Optional[str] (original snippet)
  - `content_excerpt`: Optional[str] (cleaned text, max 2000 chars)
  - `published_at`: datetime (UTC)
  - `content_hash`: string (SHA-256)
  - `language`: string (e.g. `'vi'`)
  - `raw_metadata`: dict

## Security Requirements
- XSS prevention: Excerpts and titles must contain zero executable HTML/JS.
- Defense against maliciously crafted Unicode sequences (normalization bypasses).

## Performance Requirements
- Normalize 1,000 raw article items in < 200ms.

## Testing Requirements
- Unit tests:
  - URL canonicalizer tests: stripping `utm_source=rss&utm_medium=feed` leaves clean canonical URL.
  - Timestamp converter tests: handles ICT (UTC+7), UTC, and malformed strings.
  - HTML sanitizer tests: strips `<script>alert(1)</script>`, `<b>test</b>`, `<a href="...">link</a>` down to plain text.
  - Vietnamese Unicode normalization tests: verifies tone marks and diacritics are preserved consistently.
  - Content hash test: verifies identical text produces identical SHA-256 hash.

## Expected Files / Modules
- `backend/app/modules/articles/normalizer.py`
- `backend/app/modules/articles/url_cleaner.py`
- `backend/app/modules/articles/schemas.py`
- `tests/unit/test_article_normalizer.py`

## Acceptance Criteria
- [ ] Tracking query parameters are completely stripped from canonical URLs.
- [ ] All article timestamps are accurately normalized to UTC.
- [ ] Raw HTML tags are safely stripped from titles and excerpts.
- [ ] Vietnamese diacritics and Unicode characters are preserved without corruption.
- [ ] Unit tests pass 100% of sanitization and canonicalization test cases.

## Completion Report
When completed, report:
1. Normalizer implementation components.
2. List of stripped tracking parameters.
3. Unicode and HTML sanitization results.
4. Unit test execution results.

## Follow-up Tasks
- TASK-018 (Article Deduplication Engine)
- TASK-019 (Article Ingestion Worker Pipeline)
