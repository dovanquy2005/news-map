# TASK-027 — Event Clustering: Multi-Signal Similarity & Scoring

## Status
DONE

## Priority
P0

## Phase
Phase 1 — Intelligence Pipeline

## Depends On
- TASK-021
- TASK-026

## Objective
Implement the multi-signal same-event scoring engine that compares an article's extracted representation against candidate events using location, time, semantic text, named entities, and fact overlaps to compute a composite match score and decision (MERGE vs NEW_EVENT vs UNCERTAIN).

## Source of Truth
- `docs/07-event-clustering.md` (Scoring signals, Decision policy, Safety principle)
- `prd.md` (Section 9: Event Clustering, Section 23.3: Không gộp event quá mạnh)

## Scope

### MUST
- Implement multi-signal scoring function combining weighted features:
  - `location_similarity` (0.0 to 1.0): Based on physical distance and administrative level match (exact landmark/street: 1.0; same ward/district: 0.7; same province only: 0.3; distant/mismatch: 0.0).
  - `time_similarity` (0.0 to 1.0): Decay function based on difference in event occurred/reported time (within 2h: 1.0; 2-12h: 0.8; 12-24h: 0.5; >48h: 0.1).
  - `semantic_similarity` (0.0 to 1.0): Cosine similarity of title/content embeddings or high Jaccard/TF-IDF n-gram overlap.
  - `entity_overlap` (0.0 to 1.0): Jaccard similarity of extracted named entities (people, organizations, specific vehicle plates, landmarks).
  - `fact_overlap` (0.0 to 1.0): Overlap ratio of extracted concrete fact claims.
  - `category_match` (0.0 or 1.0): Exact category match (1.0) or compatible category (0.5), incompatible (0.0).
- Implement configurable signal weights:
  - Default: `location: 0.25`, `time: 0.20`, `semantic: 0.25`, `entity: 0.15`, `fact: 0.10`, `category: 0.05`.
- Implement decision policy:
  - `composite_score >= merge_threshold` (e.g. 0.75) -> `MERGE` (attach article to candidate event).
  - `composite_score <= new_event_threshold` (e.g. 0.40) -> `CREATE_NEW_EVENT`.
  - `0.40 < composite_score < 0.75` -> `UNCERTAIN` (requires conservative evaluation: prefer creating separate event or queueing for review).
- Enforce Safety Principle from `docs/07-event-clustering.md`:
  - A false merge is more damaging than a temporary duplicate.
  - NEVER merge two items solely because they mention the same province or street if the temporal or semantic signals indicate different incidents (e.g. 18:00 traffic accident vs 20:00 fire on the same road).

### MUST NOT
- Merge two events if their categories are mutually incompatible (e.g. `WEATHER/FLOOD` vs `BANK_ROBBERY`).
- Merge solely based on location proximity when entities and incident descriptions diverge completely.
- Hardcode fixed weights in business logic without configuration overrides.

## Architecture Constraints
- Conforms strictly to `docs/07-event-clustering.md` decision policy and safety principle.
- Deterministic, testable domain service with transparent score breakdown for provenance.

## Implementation Requirements
- Create `backend/app/modules/clustering/scorer.py` and `backend/app/modules/clustering/signals/`.
  - `signals/location.py`
  - `signals/time.py`
  - `signals/text.py`
  - `signals/entity.py`
  - `signals/fact.py`
- Return detailed `ClusteringDecisionDTO`:
  - `decision`: enum (`MERGE`, `CREATE_NEW_EVENT`, `UNCERTAIN`)
  - `best_match_event_id`: Optional[UUID]
  - `composite_score`: float
  - `signal_scores`: dict of individual signal scores
  - `match_reason`: string explaining the primary driving signals (e.g. `"High entity and temporal overlap at same street address"`)

## Security Requirements
- Safe string and vector operations to prevent algorithmic complexity attacks.
- Bounds validation on all incoming numerical and text features.

## Performance Requirements
- Scoring an article against 25 candidates in < 30ms.

## Testing Requirements
- Unit tests:
  - Same event scenario: two articles on same accident at same bridge within 1 hour produce `composite_score >= 0.80` -> `MERGE`.
  - Different events same location: fire at 18:00 and robbery at 20:00 on same street produce `composite_score < 0.40` -> `CREATE_NEW_EVENT` (proves safety principle).
  - Broad province scenario: two unrelated articles mentioning "TP.HCM" produce low composite score and are NOT merged.
  - Boundary scenario: borderline score (0.55) correctly produces `UNCERTAIN`.

## Expected Files / Modules
- `backend/app/modules/clustering/scorer.py`
- `backend/app/modules/clustering/signals/location.py`
- `backend/app/modules/clustering/signals/time.py`
- `backend/app/modules/clustering/signals/text.py`
- `backend/app/modules/clustering/signals/entity.py`
- `backend/app/modules/clustering/signals/fact.py`
- `tests/unit/test_clustering_scorer.py`

## Acceptance Criteria
- [ ] Multi-signal scoring accurately calculates individual and composite scores.
- [ ] Safety principle verified: same-location different-incident articles are never merged.
- [ ] Configurable thresholds dictate `MERGE` vs `CREATE_NEW_EVENT`.
- [ ] Score breakdown and human-readable explanation generated for every evaluation.

## Completion Report
When completed, report:
1. Signal formulas and default weight distribution.
2. Threshold configuration and decision tree.
3. Verification of safety principle unit test cases.
4. Performance benchmarks for candidate batch scoring.

## Follow-up Tasks
- TASK-028 (Clustering Worker & Provenance Persistence)
- TASK-029 (Event Facts & Timeline Extraction Worker)
- TASK-031 (Event Confidence Scoring Engine)
