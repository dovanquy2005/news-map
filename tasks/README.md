# Vietnam News Map — Implementation Task Registry

Welcome to the task-management system for the Vietnam News Map project. This task registry translates the project specification (`prd.md`), architecture documents (`docs/*.md`), and architectural decision records (`adr/*.md`) into a dependency-aware, independently verifiable execution sequence.

---

## Status Legend

| Status | Meaning |
| :--- | :--- |
| **TODO** | Ready to be picked up; prerequisites satisfied or in progress. |
| **IN_PROGRESS** | Currently being implemented by a coding agent or engineer. |
| **BLOCKED** | Waiting on unresolved dependencies or upstream tasks. |
| **IN_REVIEW** | Implemented; undergoing validation, testing, or human review. |
| **DONE** | Fully implemented, tested, and verified against acceptance criteria. |

---

## Priority Definitions

- **P0 (Critical / Blocker)**: Core architecture, data persistence, essential pipeline, and MVP user features. Must be completed for MVP launch.
- **P1 (High)**: Operational monitoring, audit trails, analytics, and Phase 2 Trend Engine core features.
- **P2 (Medium / Extension)**: Phase 2 secondary signals and Phase 3 Text-to-Speech (TTS) capabilities.

---

## Phase Overview

```text
Phase 0: Foundation (12 tasks)
    ↓
Phase 1: News Ingestion (7 tasks)
    ↓
Phase 1: Intelligence Pipeline (12 tasks)
    ↓
Phase 1: Product — APIs & Responsive UI (10 tasks)
    ↓
Phase 1: Trust & Operations (9 tasks)
    ↓ [Phase 1 MVP Complete & Stable]
Phase 2: Trend Engine (6 tasks)
    ↓
Phase 3: Text-to-Speech (TTS) (5 tasks)
```

**Total Tasks:** 61 tasks

---

## Master Task Table

| ID | Task Title | Phase | Priority | Depends On | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| [TASK-001](file:///d:/news-map/tasks/TASK-001-project-bootstrap.md) | Repository Bootstrap & Monorepo Structure | Phase 0 — Foundation | P0 | - | TODO |
| [TASK-002](file:///d:/news-map/tasks/TASK-002-environment-configuration.md) | Environment Configuration & Secret Management Scheme | Phase 0 — Foundation | P0 | TASK-001 | TODO |
| [TASK-003](file:///d:/news-map/tasks/TASK-003-database-foundation.md) | Database Foundation (PostgreSQL + PostGIS + pgvector Setup) | Phase 0 — Foundation | P0 | TASK-001, TASK-002 | TODO |
| [TASK-004](file:///d:/news-map/tasks/TASK-004-database-entities-repositories.md) | Base Database Entity Models & Repositories | Phase 0 — Foundation | P0 | TASK-003 | TODO |
| [TASK-005](file:///d:/news-map/tasks/TASK-005-redis-queue-foundation.md) | Redis Configuration & Queue Foundation | Phase 0 — Foundation | P0 | TASK-001, TASK-002 | TODO |
| [TASK-006](file:///d:/news-map/tasks/TASK-006-backend-modular-monolith-foundation.md) | Backend Modular Monolith Foundation | Phase 0 — Foundation | P0 | TASK-001, TASK-002, TASK-003, TASK-005 | TODO |
| [TASK-007](file:///d:/news-map/tasks/TASK-007-worker-runtime-foundation.md) | Worker Runtime Foundation | Phase 0 — Foundation | P0 | TASK-002, TASK-003, TASK-004, TASK-005 | TODO |
| [TASK-008](file:///d:/news-map/tasks/TASK-008-frontend-responsive-foundation.md) | Frontend Application Foundation (Responsive Web Shell) | Phase 0 — Foundation | P0 | TASK-001, TASK-002 | TODO |
| [TASK-009](file:///d:/news-map/tasks/TASK-009-docker-development-environment.md) | Docker Development Environment | Phase 0 — Foundation | P0 | TASK-001, TASK-002, TASK-003, TASK-005 | TODO |
| [TASK-010](file:///d:/news-map/tasks/TASK-010-observability-foundation.md) | Observability Foundation (Structured Logging & Metrics) | Phase 0 — Foundation | P0 | TASK-001, TASK-002, TASK-006, TASK-007 | TODO |
| [TASK-011](file:///d:/news-map/tasks/TASK-011-testing-harness-foundation.md) | Testing Harness & QA Foundation | Phase 0 — Foundation | P0 | TASK-001, TASK-003, TASK-004, TASK-005, TASK-006 | TODO |
| [TASK-012](file:///d:/news-map/tasks/TASK-012-cicd-pipeline-gates.md) | CI/CD Pipeline & Quality Gates | Phase 0 — Foundation | P0 | TASK-001, TASK-009, TASK-010, TASK-011 | TODO |
| [TASK-013](file:///d:/news-map/tasks/TASK-013-source-management-domain.md) | Source Management Domain & Registry | Phase 1 — News Ingestion | P0 | TASK-004, TASK-006 | TODO |
| [TASK-014](file:///d:/news-map/tasks/TASK-014-source-scheduler-health-monitor.md) | Source Polling Scheduler & Health Monitor | Phase 1 — News Ingestion | P0 | TASK-005, TASK-007, TASK-010, TASK-013 | TODO |
| [TASK-015](file:///d:/news-map/tasks/TASK-015-ssrf-safe-http-client.md) | SSRF-Safe HTTP Client & Fetch Policy | Phase 1 — News Ingestion | P0 | TASK-002, TASK-010, TASK-013 | TODO |
| [TASK-016](file:///d:/news-map/tasks/TASK-016-rss-feed-adapter.md) | RSS & Feed Adapter Implementation | Phase 1 — News Ingestion | P0 | TASK-013, TASK-015 | TODO |
| [TASK-017](file:///d:/news-map/tasks/TASK-017-article-normalization-sanitization.md) | Article Normalization & Sanitization | Phase 1 — News Ingestion | P0 | TASK-004, TASK-016 | TODO |
| [TASK-018](file:///d:/news-map/tasks/TASK-018-article-deduplication-engine.md) | Article Deduplication Engine | Phase 1 — News Ingestion | P0 | TASK-004, TASK-017 | TODO |
| [TASK-019](file:///d:/news-map/tasks/TASK-019-article-ingestion-worker-pipeline.md) | Article Ingestion Worker & Pipeline Integration | Phase 1 — News Ingestion | P0 | TASK-005, TASK-007, TASK-010, TASK-013, TASK-014, TASK-015, TASK-016, TASK-017, TASK-018 | TODO |
| [TASK-020](file:///d:/news-map/tasks/TASK-020-nlp-extraction-prompt-client.md) | NLP Extraction Prompt Engineering & LLM Client | Phase 1 — Intelligence Pipeline | P0 | TASK-002, TASK-006, TASK-010 | TODO |
| [TASK-021](file:///d:/news-map/tasks/TASK-021-event-extraction-schema-validation.md) | Event & Entity Extraction Schema Validation | Phase 1 — Intelligence Pipeline | P0 | TASK-020 | TODO |
| [TASK-022](file:///d:/news-map/tasks/TASK-022-event-extraction-worker.md) | Event & Entity Extraction Worker | Phase 1 — Intelligence Pipeline | P0 | TASK-005, TASK-007, TASK-010, TASK-019, TASK-020, TASK-021 | TODO |
| [TASK-023](file:///d:/news-map/tasks/TASK-023-location-extraction-normalization.md) | Location Extraction & Hierarchical Normalization | Phase 1 — Intelligence Pipeline | P0 | TASK-021, TASK-022 | TODO |
| [TASK-024](file:///d:/news-map/tasks/TASK-024-geocoding-adapter-spatial-resolution.md) | Geocoding Adapter & Spatial Resolution Service | Phase 1 — Intelligence Pipeline | P0 | TASK-002, TASK-023 | TODO |
| [TASK-025](file:///d:/news-map/tasks/TASK-025-geocoding-worker-persistence.md) | Geocoding Worker & Location Persistence | Phase 1 — Intelligence Pipeline | P0 | TASK-004, TASK-005, TASK-007, TASK-022, TASK-023, TASK-024 | TODO |
| [TASK-026](file:///d:/news-map/tasks/TASK-026-clustering-candidate-retrieval.md) | Event Clustering: Candidate Retrieval Service | Phase 1 — Intelligence Pipeline | P0 | TASK-004, TASK-021, TASK-025 | TODO |
| [TASK-027](file:///d:/news-map/tasks/TASK-027-clustering-similarity-scoring.md) | Event Clustering: Multi-Signal Similarity & Scoring | Phase 1 — Intelligence Pipeline | P0 | TASK-021, TASK-026 | TODO |
| [TASK-028](file:///d:/news-map/tasks/TASK-028-clustering-worker-provenance.md) | Event Clustering Worker & Provenance Persistence | Phase 1 — Intelligence Pipeline | P0 | TASK-004, TASK-005, TASK-007, TASK-022, TASK-025, TASK-026, TASK-027 | TODO |
| [TASK-029](file:///d:/news-map/tasks/TASK-029-event-facts-timeline-worker.md) | Event Facts & Timeline Extraction Worker | Phase 1 — Intelligence Pipeline | P0 | TASK-004, TASK-028 | TODO |
| [TASK-030](file:///d:/news-map/tasks/TASK-030-event-summary-generator.md) | Event Summary Generator | Phase 1 — Intelligence Pipeline | P0 | TASK-020, TASK-028, TASK-029 | TODO |
| [TASK-031](file:///d:/news-map/tasks/TASK-031-event-confidence-scoring.md) | Event Confidence Scoring Engine | Phase 1 — Intelligence Pipeline | P0 | TASK-028, TASK-029, TASK-030 | TODO |
| [TASK-032](file:///d:/news-map/tasks/TASK-032-public-events-api.md) | Public Events API (GET /api/v1/events) | Phase 1 — Product | P0 | TASK-004, TASK-006, TASK-028, TASK-031 | TODO |
| [TASK-033](file:///d:/news-map/tasks/TASK-033-public-event-detail-api.md) | Public Event Detail API (GET /api/v1/events/{eventId}) | Phase 1 — Product | P0 | TASK-004, TASK-006, TASK-028, TASK-029, TASK-030, TASK-031 | TODO |
| [TASK-034](file:///d:/news-map/tasks/TASK-034-public-events-search-api.md) | Public Events Search API (GET /api/v1/events/search) | Phase 1 — Product | P0 | TASK-004, TASK-006, TASK-032 | TODO |
| [TASK-035](file:///d:/news-map/tasks/TASK-035-google-maps-web-integration.md) | Google Maps Web Integration & Viewport Bounds Sync | Phase 1 — Product | P0 | TASK-008, TASK-032 | TODO |
| [TASK-036](file:///d:/news-map/tasks/TASK-036-map-marker-rendering-clustering.md) | Map Marker Rendering & Dynamic Marker Clustering | Phase 1 — Product | P0 | TASK-032, TASK-035 | TODO |
| [TASK-037](file:///d:/news-map/tasks/TASK-037-event-quick-popup-bottom-sheet.md) | Event Quick Popup & Mobile Bottom Sheet Preview | Phase 1 — Product | P0 | TASK-008, TASK-036 | TODO |
| [TASK-038](file:///d:/news-map/tasks/TASK-038-event-detail-panel.md) | Event Detail Panel Component | Phase 1 — Product | P0 | TASK-008, TASK-033, TASK-037 | TODO |
| [TASK-039](file:///d:/news-map/tasks/TASK-039-filter-search-ui.md) | Filter & Search UI Component | Phase 1 — Product | P0 | TASK-008, TASK-034 | TODO |
| [TASK-040](file:///d:/news-map/tasks/TASK-040-event-feed-view-map-sync.md) | Event Feed View & Map Synchronization | Phase 1 — Product | P0 | TASK-008, TASK-032, TASK-036, TASK-037, TASK-039 | TODO |
| [TASK-041](file:///d:/news-map/tasks/TASK-041-responsive-layout-accessibility.md) | Responsive Web Layout & Accessibility Polish | Phase 1 — Product | P0 | TASK-008, TASK-035, TASK-036, TASK-037, TASK-038, TASK-039, TASK-040 | TODO |
| [TASK-042](file:///d:/news-map/tasks/TASK-042-historical-snapshot-worker.md) | Historical Snapshot Collection Worker | Phase 1 — Trust & Operations | P1 | TASK-004, TASK-005, TASK-007, TASK-028 | TODO |
| [TASK-043](file:///d:/news-map/tasks/TASK-043-admin-auth-rbac.md) | Admin Authentication & Authorization Module | Phase 1 — Trust & Operations | P0 | TASK-002, TASK-004, TASK-006, TASK-010 | TODO |
| [TASK-044](file:///d:/news-map/tasks/TASK-044-admin-source-monitor-api-ui.md) | Admin Source Monitor API & UI | Phase 1 — Trust & Operations | P1 | TASK-013, TASK-014, TASK-043 | TODO |
| [TASK-045](file:///d:/news-map/tasks/TASK-045-admin-processing-monitor-api-ui.md) | Admin Processing Queue Monitor API & UI | Phase 1 — Trust & Operations | P1 | TASK-005, TASK-007, TASK-010, TASK-043 | TODO |
| [TASK-046](file:///d:/news-map/tasks/TASK-046-admin-review-queue-audit-log.md) | Admin Data Quality Review Queue & Audit Log | Phase 1 — Trust & Operations | P1 | TASK-004, TASK-028, TASK-029, TASK-031, TASK-043 | TODO |
| [TASK-047](file:///d:/news-map/tasks/TASK-047-caching-performance-optimization.md) | Caching Layer & Performance Optimization | Phase 1 — Trust & Operations | P0 | TASK-005, TASK-032, TASK-033, TASK-034 | TODO |
| [TASK-048](file:///d:/news-map/tasks/TASK-048-security-hardening-asvs-verification.md) | Security Hardening & OWASP ASVS Verification | Phase 1 — Trust & Operations | P0 | TASK-006, TASK-010, TASK-015, TASK-020, TASK-043, TASK-047 | TODO |
| [TASK-049](file:///d:/news-map/tasks/TASK-049-e2e-critical-flow-validation.md) | End-to-End Critical Flow Validation | Phase 1 — Trust & Operations | P0 | TASK-012, TASK-019, TASK-022, TASK-025, TASK-028, TASK-029, TASK-030, TASK-031, TASK-032, TASK-033, TASK-035, TASK-036, TASK-037, TASK-038, TASK-040, TASK-041 | TODO |
| [TASK-050](file:///d:/news-map/tasks/TASK-050-phase1-production-readiness.md) | Phase 1 MVP Production Readiness & Runbook | Phase 1 — Trust & Operations | P0 | TASK-012, TASK-041, TASK-044, TASK-045, TASK-047, TASK-048, TASK-049 | TODO |
| [TASK-051](file:///d:/news-map/tasks/TASK-051-historical-analytics-velocity-engine.md) | Historical Snapshot Analytics & Velocity Computation | Phase 2 — Trend Engine | P1 | TASK-042, TASK-050 | TODO |
| [TASK-052](file:///d:/news-map/tasks/TASK-052-search-trend-signal-adapter.md) | Search Trend Signal Integration | Phase 2 — Trend Engine | P1 | TASK-050, TASK-051 | TODO |
| [TASK-053](file:///d:/news-map/tasks/TASK-053-social-public-signal-adapter.md) | Public Social & External Signals Adapter | Phase 2 — Trend Engine | P2 | TASK-050, TASK-051 | TODO |
| [TASK-054](file:///d:/news-map/tasks/TASK-054-baseline-anomaly-detection-engine.md) | Baseline Calculation & Anomaly Detection Engine | Phase 2 — Trend Engine | P1 | TASK-042, TASK-051 | TODO |
| [TASK-055](file:///d:/news-map/tasks/TASK-055-trend-score-engine.md) | Multi-Factor Trend Score Engine | Phase 2 — Trend Engine | P1 | TASK-031, TASK-051, TASK-052, TASK-054 | TODO |
| [TASK-056](file:///d:/news-map/tasks/TASK-056-trend-hotspot-ui.md) | Trend & Hotspot UI Extension | Phase 2 — Trend Engine | P1 | TASK-036, TASK-038, TASK-040, TASK-055 | TODO |
| [TASK-057](file:///d:/news-map/tasks/TASK-057-tts-provider-abstraction.md) | TTS Provider Abstraction & Vietnamese Voice Adapter | Phase 3 — TTS | P2 | TASK-002, TASK-006, TASK-010, TASK-050 | TODO |
| [TASK-058](file:///d:/news-map/tasks/TASK-058-summary-to-script-generator.md) | Summary-to-Script Generation Worker (Quick/Full) | Phase 3 — TTS | P2 | TASK-029, TASK-030, TASK-057 | TODO |
| [TASK-059](file:///d:/news-map/tasks/TASK-059-audio-synthesis-caching-storage.md) | Audio Synthesis, Storage & Caching Pipeline | Phase 3 — TTS | P2 | TASK-005, TASK-007, TASK-057, TASK-058 | TODO |
| [TASK-060](file:///d:/news-map/tasks/TASK-060-audio-player-ui-component.md) | Audio Player UI Component | Phase 3 — TTS | P2 | TASK-037, TASK-038, TASK-059 | TODO |
| [TASK-061](file:///d:/news-map/tasks/TASK-061-area-audio-briefing-synthesizer.md) | Area Audio Briefing Synthesizer | Phase 3 — TTS | P2 | TASK-058, TASK-059, TASK-060 | TODO |

---

## Recommended Implementation Order

To maintain clean velocity without blocking on downstream dependencies, execute tasks in the following grouped sprints:

### Sprint 0 — Foundation & Infrastructure (Tasks 001 to 012)
1. `TASK-001` (Bootstrap)
2. `TASK-002` (Config & Secrets)
3. `TASK-003` (DB & PostGIS) & `TASK-005` (Redis & Queue) [Parallel]
4. `TASK-004` (Entity Models)
5. `TASK-006` (Monolith Base) & `TASK-007` (Worker Base) & `TASK-008` (Frontend Shell) [Parallel]
6. `TASK-009` (Docker Compose)
7. `TASK-010` (Observability) & `TASK-011` (Test Harness)
8. `TASK-012` (CI/CD Gates)

### Sprint 1 — News Ingestion Pipeline (Tasks 013 to 019)
1. `TASK-013` (Source Domain)
2. `TASK-015` (SSRF-Safe HTTP Client)
3. `TASK-014` (Scheduler) & `TASK-016` (RSS Adapter) [Parallel]
4. `TASK-017` (Normalization)
5. `TASK-018` (Deduplication)
6. `TASK-019` (Ingestion Worker Integration)

### Sprint 2 — Intelligence Pipeline: Extraction & Geocoding (Tasks 020 to 025)
1. `TASK-020` (LLM Prompt & Client)
2. `TASK-021` (Extraction Schema Validator)
3. `TASK-022` (Extraction Worker)
4. `TASK-023` (Location Hierarchy Normalizer)
5. `TASK-024` (Geocoder Adapter & Centroids)
6. `TASK-025` (Geocoding Worker & PostGIS Persistence)

### Sprint 3 — Intelligence Pipeline: Clustering & Verification (Tasks 026 to 031)
1. `TASK-026` (Candidate Retrieval Service)
2. `TASK-027` (Multi-Signal Scoring Engine)
3. `TASK-028` (Clustering Worker & Provenance)
4. `TASK-029` (Timeline & Facts Worker)
5. `TASK-030` (Summary Generator)
6. `TASK-031` (Confidence Scoring Engine)

### Sprint 4 — Product: Public APIs & Responsive Frontend (Tasks 032 to 041)
1. `TASK-032` (Events API) & `TASK-033` (Detail API) & `TASK-034` (Search API) [Parallel Backend]
2. `TASK-035` (Google Maps Viewport Sync)
3. `TASK-036` (Marker Rendering & Clustering)
4. `TASK-037` (Quick Popup & Bottom Sheet)
5. `TASK-038` (Event Detail Panel)
6. `TASK-039` (Filter & Search UI)
7. `TASK-040` (Event Feed View & Map Sync)
8. `TASK-041` (Responsive & Accessibility Polish)

### Sprint 5 — Operations, Trust & MVP Hardening (Tasks 042 to 050)
1. `TASK-042` (Historical Snapshot Worker) & `TASK-043` (Admin Auth & RBAC) [Parallel]
2. `TASK-044` (Source Monitor) & `TASK-045` (Queue Monitor) & `TASK-046` (Review Queue & Audit Log) [Parallel Admin]
3. `TASK-047` (Caching & Performance Optimization)
4. `TASK-048` (Security Hardening & ASVS Audit)
5. `TASK-049` (End-to-End 16-Step Critical Flow Validation)
6. `TASK-050` (Phase 1 Production Readiness & Runbook)

### Phase 2 — Trend Engine (Tasks 051 to 056)
*(Commences strictly after Phase 1 MVP is stable in production)*
1. `TASK-051` (Snapshot Analytics & Velocity Engine)
2. `TASK-052` (Search Trends) & `TASK-053` (Social Signals) & `TASK-054` (Anomaly Baseline) [Parallel]
3. `TASK-055` (Multi-Factor Trend Score Engine)
4. `TASK-056` (Trend UI & Heatmap Extension)

### Phase 3 — Text-to-Speech (TTS) (Tasks 057 to 061)
*(Commences strictly after summary quality is stable)*
1. `TASK-057` (TTS Provider Abstraction)
2. `TASK-058` (Summary-to-Script Worker: Quick & Full Briefs)
3. `TASK-059` (Audio Synthesis, Storage & Caching Pipeline)
4. `TASK-060` (Audio Player UI Component)
5. `TASK-061` (Area Audio Briefing Synthesizer)

---

## Parallel Execution Opportunities

The following task streams can be developed in parallel by separate engineers/agents without blocking each other:

- **Stream A (Frontend Shell & Map)**: `TASK-008` -> `TASK-035` -> `TASK-036` (requires only mock API data).
- **Stream B (Ingestion Pipeline)**: `TASK-013` -> `TASK-014` -> `TASK-015` -> `TASK-016` -> `TASK-017` -> `TASK-018` -> `TASK-019`.
- **Stream C (AI / Extraction)**: `TASK-020` -> `TASK-021` -> `TASK-023` -> `TASK-024` (independent of database ingestion).
- **Stream D (Admin & Security Operations)**: `TASK-043` -> `TASK-044` -> `TASK-045` -> `TASK-046` (can be built once Admin Auth is established).

---

## Vibe Coding Rule Compliance

As required by `AGENTS.md` and `docs/16-vibe-coding-workflow.md`:
- Each task represents a bounded vertical slice.
- Before coding any task, agents must state:
  1. Files to change
  2. Approach
  3. Risks
  4. Contracts affected
  5. Tests to run
- After each task, report completion according to Section 13 of `AGENTS.md`.
