# TASK-052 — Search Trend Signal Integration

## Status
TODO

## Priority
P1

## Phase
Phase 2 — Trend Engine

## Depends On
- TASK-050
- TASK-051

## Objective
Implement the external search trend signal adapter (e.g. Google Trends / search interest volume signal) that fetches, normalizes, and correlates public search volume metrics for key event keywords and entities in Vietnam, supplying an independent external signal to the Trend Engine.

## Source of Truth
- `docs/01-product-scope.md` (Phase 2: search trend signal)
- `prd.md` (Section 25.2: Internal signals, Section 34: Later - Google Trends integration)

## Scope

### MUST
- Implement `SearchTrendAdapter` interface with method:
  - `async get_interest_over_time(keywords: list[str], timeframe: str = "now 1-d", geo: str = "VN") -> SearchTrendSignalDTO`
- Implement provider implementation:
  - Official search trend API or compliant structured trend signal consumer.
  - Queries search volume index (0–100) for event keywords (e.g. event entity names, location + incident type).
  - Normalizes relative interest growth: detects sudden spike in search queries compared to baseline interest over 7 days.
- Implement rate limiting, circuit breaker, and caching:
  - Cache trend metrics in Redis (`vnm:trend:search:<keyword_hash>`) with a 6-hour TTL to respect strict quota limits.
  - Fail gracefully if search trend provider is unavailable, returning a neutral signal without disrupting internal velocity metrics.
- Produce standardized `SearchTrendSignal`:
  - `keyword`: string
  - `relative_growth`: float (-1.0 to +1.0)
  - `spike_detected`: bool
  - `signal_confidence`: float (0.0 to 1.0)

### MUST NOT
- Scrape or bypass anti-bot mechanisms of external search providers.
- Block the main event pipeline if external search trend APIs are slow or rate-limited.
- Treat missing search trend data as zero interest (must treat as "insufficient signal").

## Architecture Constraints
- Conforms to `docs/05-ingestion-pipeline.md` and `docs/10-security.md`: All external requests route through rate-limited, timeout-bounded safe HTTP clients.
- Trend signal is an auxiliary input to the Trend Score engine; never a hard dependency for event persistence.

## Implementation Requirements
- Create `backend/app/modules/analytics/signals/search_trend.py`.
- Keyword extractor helper: extracts top 2-3 most distinctive entity names from event to avoid generic noisy search terms like "tin tức" or "Việt Nam".
- Cache and retry configuration.

## Security Requirements
- External API keys stored in environment (`SEARCH_TRENDS_API_KEY`) and masked in logs.
- Search queries sanitized before outbound HTTP requests.

## Performance Requirements
- Outbound API timeout capped at 5s.
- Cached signal lookup < 5ms.

## Testing Requirements
- Unit tests:
  - Distinctive keyword extraction selects specific entities (e.g. "Vụ cháy chung cư X") over generic terms.
  - Mock provider returns search interest curve; spike detector correctly identifies sudden surge.
  - Cached search signal returns cached DTO without outbound network request.
  - Provider failure returns graceful fallback signal (`spike_detected: False`, `signal_confidence: 0.0`).

## Expected Files / Modules
- `backend/app/modules/analytics/signals/search_trend.py`
- `backend/app/modules/analytics/signals/keyword_extractor.py`
- `tests/unit/test_search_trend_signal.py`

## Acceptance Criteria
- [ ] Search trend adapter extracts distinctive keywords and fetches normalized interest signals for Vietnam.
- [ ] Spike detection identifies surge in search interest relative to 7-day baseline.
- [ ] Redis caching prevents quota exhaustion.
- [ ] Provider failure gracefully degrades without breaking pipeline execution.

## Completion Report
When completed, report:
1. Search trend provider implementation.
2. Keyword extraction heuristic.
3. Spike detection algorithm.
4. Test execution results.

## Follow-up Tasks
- TASK-054 (Baseline Calculation & Anomaly Detection Engine)
- TASK-055 (Multi-Factor Trend Score Engine)
