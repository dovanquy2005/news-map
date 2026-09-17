# Implementation Roadmap

## Sprint 0 — Foundation

- repo structure;
- CI;
- environment config;
- database migration system;
- base observability;
- auth/admin skeleton;
- responsive shell.

## Sprint 1 — Ingestion

- source model;
- source adapters;
- scheduler;
- article normalization;
- dedup;
- ingestion monitor.

## Sprint 2 — Event pipeline

- extraction schema;
- NLP worker;
- location resolution;
- event model;
- persistence.

## Sprint 3 — Clustering

- candidate retrieval;
- similarity;
- same-event scoring;
- timeline;
- summary.

## Sprint 4 — Map product

- map;
- viewport API;
- clustering UI;
- popup;
- event detail;
- sources;
- feed;
- filters/search.

## Sprint 5 — Trust & operations

- confidence explanations;
- review queue;
- provenance;
- audit log;
- failure recovery;
- historical snapshots.

## Sprint 6 — Hardening

- load tests;
- caching;
- security testing;
- WAF/rate limits;
- responsive/accessibility polish;
- end-to-end tests.

## Phase 2

Only after MVP quality is measured:

- Trend Engine;
- search/social signals;
- anomaly detection;
- heatmap.

## Phase 3

Only after event summary quality is stable:

- TTS;
- cached audio;
- area briefings.
