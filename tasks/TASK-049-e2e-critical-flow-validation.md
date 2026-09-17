# TASK-049 — End-to-End Critical Flow Validation

## Status
TODO

## Priority
P0

## Phase
Phase 1 — Trust & Operations

## Depends On
- TASK-012
- TASK-019
- TASK-022
- TASK-025
- TASK-028
- TASK-029
- TASK-030
- TASK-031
- TASK-032
- TASK-033
- TASK-035
- TASK-036
- TASK-037
- TASK-038
- TASK-040
- TASK-041

## Objective
Implement and execute automated end-to-end (E2E) integration test suites (using Playwright or Cypress) validating the complete critical path from feed ingestion through AI extraction, clustering, API responses, map marker rendering, user interaction, detail loading, and external source link verification conforming to `docs/14-testing-qa.md` and `prd.md` Section 35.

## Source of Truth
- `AGENTS.md` (Definition of done)
- `docs/14-testing-qa.md` (E2E critical flow)
- `prd.md` (Section 35: MVP Acceptance Criteria)

## Scope

### MUST
- Implement automated E2E test verifying the 16-step MVP Critical Flow defined in `prd.md` Section 35:
  1. Article arrives via mock news feed.
  2. System fetches and stores article metadata.
  3. Deduplication pipeline processes the article.
  4. NLP extraction extracts event title, location, time, and facts.
  5. Geocoder resolves location text to spatial coordinates.
  6. Clustering queries similar candidates and creates new event or merges into existing event.
  7. Event counters (`article_count`, `source_count`) update accurately.
  8. Summary and timeline are synthesized.
  9. Public API returns event in viewport query `GET /api/v1/events?bbox=...`.
  10. Map displays marker at resolved coordinates with correct category visual pin.
  11. User clicks marker on map -> Quick popup opens with accurate title and counts.
  12. User clicks "Xem chi tiết →" -> Event Detail Panel opens.
  13. User inspects Summary, Confidence Card, Verification Metrics, and Timeline.
  14. User inspects Source List and verifies direct external article link exists (`href`, `target="_blank"`).
  15. User clicks source article link -> opens publisher URL in new tab.
- Test multi-article clustering flow:
  - Ingest second article from different publisher covering the same incident -> verifies map retains exactly ONE event marker, with `article_count` incremented to 2 and `source_count` to 2.
- Execute automated E2E tests in both desktop (1280x800) and mobile (375x667) viewport emulation.

### MUST NOT
- Rely on manual testing alone; the critical path must be automated in CI.
- Mock the entire pipeline in E2E tests (real database, real Redis, and real backend running against fixture HTTP/LLM mocks).
- Mark MVP as complete until this suite passes 100%.

## Architecture Constraints
- Conforms to `docs/14-testing-qa.md`: E2E critical flow is mandatory.
- Uses mock HTTP server for external news feeds and mock LLM provider to ensure test determinism and zero external API costs.

## Implementation Requirements
- Set up Playwright test framework: `frontend/e2e/` or root `e2e/`.
- Test environment orchestrator (`scripts/run_e2e.sh`):
  - Starts backend API, worker, PostgreSQL, Redis, and frontend development server with test configurations.
  - Seeds initial test source.
  - Serves static mock RSS feed on local test server.
  - Serves deterministic mock LLM responses.
  - Runs Playwright tests headlessly.
  - Cleans up processes and containers.

## Security Requirements
- E2E tests run with sandboxed test credentials and clean test database.

## Performance Requirements
- Complete E2E test suite executes in < 3 minutes.

## Testing Requirements
- Playwright test specs:
  - `e2e/critical_path_desktop.spec.ts`: Complete 16-step flow on desktop split layout.
  - `e2e/critical_path_mobile.spec.ts`: Complete flow on mobile: marker tap -> bottom sheet preview -> full-screen detail panel -> source link.
  - `e2e/multi_article_merge.spec.ts`: Verifies 2 articles from 2 sources produce 1 marker with 2 sources in popup.
  - `e2e/filter_synchronization.spec.ts`: Verifies filtering by category or time updates both map and feed.

## Expected Files / Modules
- `e2e/playwright.config.ts`
- `e2e/critical_path_desktop.spec.ts`
- `e2e/critical_path_mobile.spec.ts`
- `e2e/multi_article_merge.spec.ts`
- `e2e/filter_synchronization.spec.ts`
- `e2e/mocks/mock_llm_server.py`
- `e2e/mocks/mock_rss_server.py`
- `scripts/run_e2e.sh`

## Acceptance Criteria
- [ ] Automated Playwright test executes all 16 steps of the MVP acceptance criteria from end to end.
- [ ] Multi-article clustering test proves 2 articles produce 1 marker with updated counts.
- [ ] Tests pass cleanly on both desktop (1280px) and mobile (375px) viewports.
- [ ] Test runs reproducibly in CI without flaky timeouts.

## Completion Report
When completed, report:
1. Playwright E2E configuration and mock server setup.
2. Verified test scenarios across desktop and mobile.
3. Test execution results and recorded trace artifacts.
4. Confirmation that all 16 steps in `prd.md` Section 35 pass.

## Follow-up Tasks
- TASK-050 (Phase 1 MVP Production Readiness & Runbook)
- TASK-051 (Phase 2 Trend Engine initiation)
