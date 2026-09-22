# TASK-018 — Article Deduplication Engine

## Status
DONE

## Priority
P0

## Phase
Phase 1 — News Ingestion

## Depends On
- TASK-004
- TASK-017

## Objective
Implement the multi-stage article deduplication engine that identifies and suppresses duplicate articles across feeds before database insertion or event extraction according to the deduplication hierarchy specified in `docs/05-ingestion-pipeline.md` and `prd.md` Section 6.3.

## Source of Truth
- `docs/04-data-architecture.md` (Required indexes: articles)
- `docs/05-ingestion-pipeline.md` (Dedup order)
- `prd.md` (Section 6.3: Deduplication)

## Scope

### MUST
- Implement tiered deduplication hierarchy:
  1. Level 1 — Exact Canonical URL: Check database unique constraint / index on `canonical_url`. If exists, classify as DUPLICATE_URL.
  2. Level 2 — Content Hash: Check index on `content_hash`. If exists, classify as DUPLICATE_CONTENT.
  3. Level 3 — Title & Time Proximity Heuristic: Query articles with identical normalized title or high Levenshtein / Jaccard title similarity (>= 0.90) published within a 24-hour window from the same source or syndicated wire services.
- Provide `ArticleDeduplicator` service with method:
  - `evaluate_article(article: NormalizedArticleDTO) -> DedupDecision`
    - `is_duplicate: bool`
    - `matched_article_id: Optional[UUID]`
    - `dedup_level: Optional[str]` (`EXACT_URL`, `CONTENT_HASH`, `TITLE_TIME_HEURISTIC`)
    - `confidence: float`
- When duplicate is detected, update existing article's `updated_at` or `fetched_at` if new metadata is present, without inserting a new article row.
- Support batch deduplication for feeds containing multiple items.

### MUST NOT
- Drop articles from different sources that simply cover the same event (cross-source same-event matching is the responsibility of Event Clustering in TASK-027, not Article Deduplication).
- Perform unindexed database table scans during duplicate checks.
- Treat minor title updates or edits from the same publisher as separate articles.

## Architecture Constraints
- Conforms to `docs/05-ingestion-pipeline.md`: Dedup order is exact canonical URL -> content hash -> normalized title/time heuristic.
- High-throughput check: Must leverage Redis cache or database indexes effectively.

## Implementation Requirements
- Create `backend/app/modules/articles/deduplicator.py`.
- Fast-path checking:
  - Redis set/bloom filter or fast index lookup on `canonical_url` and `content_hash`.
  - Database fallback lookup via repository.
- Title comparison utility using string distance / token set ratio without requiring heavy NLP models.

## Security Requirements
- Safe string similarity comparisons that prevent CPU-exhaustion DoS (e.g. bounding string length to max 500 chars).
- No SQL injection in candidate lookup queries.

## Performance Requirements
- Single article deduplication decision < 5ms (cache hit) or < 20ms (database lookup).
- Batch deduplication of 50 items in < 150ms.

## Testing Requirements
- Unit tests:
  - Exact canonical URL match triggers Level 1 duplicate.
  - Different URL with identical content text triggers Level 2 content hash duplicate.
  - Slight title variation with identical publication time within 24h triggers Level 3 duplicate.
  - Legitimate distinct articles with different titles and content are correctly marked `is_duplicate: False`.
  - Articles from different sources covering the same topic are NOT deduplicated at the article stage.

## Expected Files / Modules
- `backend/app/modules/articles/deduplicator.py`
- `backend/app/modules/articles/similarity.py`
- `tests/unit/test_article_deduplicator.py`
- `tests/integration/test_dedup_queries.py`

## Acceptance Criteria
- [x] Tiered deduplication logic strictly follows the 3-level order.
- [x] Duplicate articles are recognized and suppressed before triggering downstream extraction.
- [x] Articles with matching content hashes or canonical URLs are correctly resolved to the existing article ID.
- [x] Cross-source articles on the same event are preserved for the clustering pipeline.

## Completion Report
When completed, report:
1. Deduplication pipeline implementation.
2. Similarity metrics and threshold values.
3. Cache optimization strategy.
4. Unit and integration test pass results.

## Follow-up Tasks
- TASK-019 (Article Ingestion Worker Pipeline)
- TASK-021 (Event & Entity Extraction Schema Validation)
