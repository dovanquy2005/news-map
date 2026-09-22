# TASK-016 — RSS & Feed Adapter Implementation

## Status
DONE

## Priority
P0

## Phase
Phase 1 — News Ingestion

## Depends On
- TASK-013
- TASK-015

## Objective
Implement modular source adapters (starting with RSS 2.0 and Atom feeds) adhering to the standard adapter contract (`fetch()`, `normalize()`, `health()`), robust XML parsing, and source failure isolation.

## Source of Truth
- `docs/05-ingestion-pipeline.md` (Source adapter contract, Fetch policy)
- `docs/18-legal-content.md` (Source policy)
- `prd.md` (Section 6.1: News Source Management, Section 6.2: Article Ingestion)

## Scope

### MUST
- Implement base abstract adapter class `BaseSourceAdapter` exposing:
  - `async fetch(source: Source) -> RawFeedResult`
  - `async normalize(raw_item: Any, source: Source) -> RawArticleDTO`
  - `async health(source: Source) -> AdapterHealthStatus`
- Implement `RSSFeedAdapter` supporting standard RSS 2.0, Atom 1.0, and media RSS extensions:
  - Secure XML/HTML parsing (defending against XML External Entity - XXE attacks).
  - Extraction of standard feed items: `title`, `link`, `description` / `summary`, `pubDate` / `published`, `guid` / `id`, `author`, `enclosure` / `media:content` (image URL).
- Handle date parsing across common feed format variants (RFC 822, RFC 2822, ISO 8601) and timezones.
- Ensure strict failure isolation: an unparseable XML item or malformed date skips only that item and logs a warning; it does not abort the entire feed.

### MUST NOT
- Use vulnerable XML parsers with external entity resolution enabled (`resolve_entities=True`).
- Execute arbitrary JavaScript or scrape full website HTML beyond what the feed and excerpt provide.
- Fail silently without recording parse errors in the adapter result metadata.

## Architecture Constraints
- Conforms to `docs/05-ingestion-pipeline.md`: Every adapter exposes `fetch()`, `normalize()`, `health()`.
- Network fetching must be executed exclusively through the SSRF-safe HTTP client created in TASK-015.

## Implementation Requirements
- Create `backend/app/modules/sources/adapters/base.py` and `backend/app/modules/sources/adapters/rss.py`.
- Use secure parser (e.g. `defusedxml` or `lxml` with XXE/DTD disabled).
- Standardize output into `RawArticleDTO`:
  - `source_id`: UUID
  - `source_url`: string
  - `title`: string
  - `summary_raw`: Optional[str]
  - `published_at_raw`: Optional[str]
  - `author_raw`: Optional[str]
  - `image_url`: Optional[str]
  - `raw_metadata`: dict

## Security Requirements
- XXE protection: all XML entity expansion and external DTD resolution disabled.
- URLs extracted from feeds must be validated against basic URL format before passing downstream.

## Performance Requirements
- Parse 100 RSS items in < 50ms.
- Memory consumption < 20MB during XML parsing of a 1MB feed.

## Testing Requirements
- Unit tests with static XML/Atom fixtures:
  - Valid RSS 2.0 feed with RFC 822 dates.
  - Valid Atom feed with ISO 8601 dates.
  - Feed with missing optional fields (no author, no image).
  - Malformed XML feed with invalid tags (graceful error handling).
  - XXE exploit payload fixture: verify parser rejects external entity substitution without erroring or reading local files.

## Expected Files / Modules
- `backend/app/modules/sources/adapters/base.py`
- `backend/app/modules/sources/adapters/rss.py`
- `backend/app/modules/sources/adapters/registry.py`
- `tests/unit/test_rss_adapter.py`
- `tests/fixtures/feeds/sample_rss2.xml`
- `tests/fixtures/feeds/sample_atom.xml`
- `tests/fixtures/feeds/xxe_exploit.xml`

## Acceptance Criteria
- [x] RSS adapter successfully parses RSS 2.0 and Atom feeds into typed DTOs.
- [x] XXE security fixture proves entity injection is blocked.
- [x] Parse errors on single feed items are handled gracefully without failing the entire batch.
- [x] Date parser handles diverse Vietnamese and international feed date formats.

## Completion Report
When completed, report:
1. Adapter interface and RSS implementation details.
2. Verified XXE defense mechanism.
3. List of supported feed date variants.
4. Test execution results.

## Follow-up Tasks
- TASK-017 (Article Normalization & Sanitization)
- TASK-019 (Article Ingestion Worker Pipeline)
