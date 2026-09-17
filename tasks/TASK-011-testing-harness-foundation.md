# TASK-011 — Testing Harness & QA Foundation

## Status
TODO

## Priority
P0

## Phase
Phase 0 — Foundation

## Depends On
- TASK-001
- TASK-003
- TASK-004
- TASK-005
- TASK-006

## Objective
Establish the automated testing infrastructure across backend, workers, and frontend, including unit test runners, test database fixtures with isolated rollbacks, Redis mocking/fixtures, and API test clients conforming to the testing pyramid defined in `docs/14-testing-qa.md`.

## Source of Truth
- `AGENTS.md` (Rule 10: Tests)
- `docs/14-testing-qa.md` (Test pyramid, Unit, Integration, API)
- `docs/15-dev-conventions.md` (Testing conventions)

## Scope

### MUST
- Configure test frameworks:
  - Backend: `pytest` (with `pytest-asyncio`, `pytest-cov`, `pytest-env`) or Jest/Vitest.
  - Frontend: `vitest` / `jest` with `@testing-library/react` and `jsdom`.
- Implement isolated test database fixture:
  - Spins up or attaches to dedicated test database instance (`vnm_test`).
  - Automatically runs migrations before test suite.
  - Rolls back transactions after each integration test to maintain state isolation.
- Implement Redis test fixture:
  - Clean namespace/flushdb on teardown to isolate test queue state.
- Implement API test client fixture with helper methods for authenticated and anonymous requests.
- Provide sample news article and event test fixtures (`tests/fixtures/articles.json`, `tests/fixtures/events.json`).
- Configure code coverage reporting with minimum baseline thresholds.

### MUST NOT
- Run automated integration tests against production or shared staging databases.
- Allow tests to produce side effects or leave persistent mock rows in test datastores.
- Mark tests as passed without actual execution.

## Architecture Constraints
- Conforms to `docs/14-testing-qa.md` test pyramid: Unit -> Integration -> API -> E2E.
- Test suites must run cleanly both locally and in automated CI pipelines.

## Implementation Requirements
- Set up root `pytest.ini` / `vitest.config.ts`.
- `tests/conftest.py` providing fixtures:
  - `db_session`: isolated database transaction fixture.
  - `redis_client`: isolated Redis test client.
  - `api_client`: ASGI/HTTP test client with bound dependencies.
  - `sample_article_data`: standardized fixture dictionary.
  - `sample_event_data`: standardized fixture dictionary.
- Test runner scripts: `make test`, `make test-unit`, `make test-integration`.

## Security Requirements
- Test configurations must use separate, non-production test credentials.
- Test fixtures must not include real personal private data or proprietary tokens.

## Performance Requirements
- Unit test suite execution < 5s.
- Total integration test suite execution < 30s.

## Testing Requirements
- Self-test of the test harness:
  - Verify database fixture creates clean isolated table rows and rolls them back after test completion.
  - Verify mock Redis client enqueues and flushes without affecting host Redis keys.
  - Verify coverage report generator outputs valid coverage metrics.

## Expected Files / Modules
- `pytest.ini`
- `tests/conftest.py`
- `tests/fixtures/articles.json`
- `tests/fixtures/events.json`
- `tests/fixtures/sources.json`
- `frontend/vitest.config.ts`
- `tests/frontend/setup.ts`

## Acceptance Criteria
- [ ] Running test command executes test suite without syntax errors or environment conflicts.
- [ ] Database test fixtures guarantee transactional isolation between tests.
- [ ] Fixtures provide valid mock entities matching `docs/04-data-architecture.md`.
- [ ] Code coverage reports generate correctly in terminal and HTML formats.

## Completion Report
When completed, report:
1. Test runner configuration.
2. Fixture implementation and isolation verification.
3. Test suite execution command and output.
4. Baseline coverage report.

## Follow-up Tasks
- TASK-012 (CI/CD Pipeline & Quality Gates)
- TASK-018 (Article Deduplication Engine)
- TASK-027 (Clustering Similarity Scoring)
- TASK-049 (End-to-End Critical Flow Validation)
