# TASK-053 — Public Social & External Signals Adapter

## Status
TODO

## Priority
P2

## Phase
Phase 2 — Trend Engine

## Depends On
- TASK-050
- TASK-051

## Objective
Implement compliant adapters for gathering public social conversation volume and external broadcast signals when legally and technically viable, strictly adhering to terms of service and content aggregation constraints in `docs/18-legal-content.md`.

## Source of Truth
- `docs/01-product-scope.md` (Phase 2: social/public signals khi hợp pháp và khả thi)
- `docs/18-legal-content.md` (Source policy, Principles)
- `prd.md` (Section 25.2: Social mention signal, Section 32: Legal / Content Handling)

## Scope

### MUST
- Implement `PublicSignalAdapter` interface with methods:
  - `async get_public_volume_signal(event_entities: list[str], time_window_hours: int = 24) -> PublicSignalResultDTO`
- Ingest public aggregated mentions:
  - Official public social APIs or compliant public broadcast feeds (e.g. verified public pages, emergency alert channels).
  - Extract purely aggregate numeric metrics: mention volume count, velocity of public shares/reactions.
- Ensure strict legal and privacy compliance:
  - Collect zero private user messages, private posts, personal phone numbers, or private user IDs.
  - Comply with all platform terms of service and robots policies.
  - Provide immediate disable switch per signal source.
- Standardize output into `PublicSignalMetric`:
  - `signal_source`: string (e.g. `PUBLIC_BROADCAST_FEED`, `OFFICIAL_DISPATCH`)
  - `volume_count`: int
  - `growth_rate`: float
  - `signal_weight`: float (0.0 to 1.0)
  - `captured_at`: UTC timestamp

### MUST NOT
- Bypass anti-bot controls, scrape private user accounts, or harvest personal data.
- Collect private user location data.
- Introduce flaky or legally questionable third-party scraping libraries.

## Architecture Constraints
- Conforms to `docs/18-legal-content.md`: Public metadata only; respect terms and privacy laws.
- Conforms to `AGENTS.md` Rule 6: Input from third-party APIs is untrusted input.

## Implementation Requirements
- Create `backend/app/modules/analytics/signals/social_adapter.py`.
- Implement privacy filter ensuring extracted texts contain zero personal phone numbers or identification numbers before metric aggregation.
- Redis caching for signal results (TTL: 3 hours).

## Security Requirements
- All API authentication tokens stored in secret manager / environment variables.
- Data retention: raw social text discarded immediately after computing aggregated volume count.

## Performance Requirements
- External signal fetch timeout < 4s.
- Graceful timeout handling (returns empty metric on timeout without blocking Trend Engine).

## Testing Requirements
- Unit tests:
  - Privacy filter removes personal identifiers from incoming public payloads.
  - Aggregated volume metric calculates accurate growth rate over baseline.
  - Signal adapter handles empty response or rate-limit error gracefully.
  - Source toggle disabled switch immediately halts signal collection.

## Expected Files / Modules
- `backend/app/modules/analytics/signals/social_adapter.py`
- `backend/app/modules/analytics/signals/privacy_filter.py`
- `tests/unit/test_social_signal_adapter.py`

## Acceptance Criteria
- [ ] Adapter aggregates public mention volumes without harvesting personal private data.
- [ ] Privacy filtering rigorously strips personal identifiers prior to metric aggregation.
- [ ] Legal compliance switches allow disabling signal sources instantly.
- [ ] Unit tests verify graceful degradation when external signals are unavailable.

## Completion Report
When completed, report:
1. Public signal adapter interface and supported data classes.
2. Privacy filter implementation and verified regex patterns.
3. Legal compliance safeguards.
4. Test execution results.

## Follow-up Tasks
- TASK-054 (Baseline Calculation & Anomaly Detection Engine)
- TASK-055 (Multi-Factor Trend Score Engine)
