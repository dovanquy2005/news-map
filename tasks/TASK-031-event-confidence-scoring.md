# TASK-031 — Event Confidence Scoring Engine

## Status
TODO

## Priority
P0

## Phase
Phase 1 — Intelligence Pipeline

## Depends On
- TASK-028
- TASK-029
- TASK-030

## Objective
Implement the explainable confidence calculation service that computes an event's confidence score (0–100) based on source diversity, independent reporting, location precision, temporal consistency, and fact overlap, providing human-readable explanations in compliance with `prd.md` Section 4.3 and Section 24.

## Source of Truth
- `prd.md` (Section 4.3: Confidence không đồng nghĩa với Truth, Section 24: Event Confidence Score)
- `docs/04-data-architecture.md` (events.confidence_score)
- `docs/14-testing-qa.md` (Unit tests: confidence calculation)

## Scope

### MUST
- Implement `ConfidenceScoringEngine` with scoring factors:
  - Factor 1 — Independent Source Count (weight: 35%):
    - 1 source: 20 pts; 2 sources: 50 pts; 3-4 sources: 80 pts; >= 5 independent sources: 100 pts.
  - Factor 2 — Location Precision & Consistency (weight: 25%):
    - Consistent street/landmark across articles: 100 pts; ward/district: 75 pts; province only: 40 pts; conflicting locations: 10 pts.
  - Factor 3 — Temporal Consistency (weight: 15%):
    - Cohesive timeline across reporting outlets: 100 pts; minor discrepancies (< 3h): 70 pts; major unexplained discrepancies: 20 pts.
  - Factor 4 — Fact Overlap & Consensus (weight: 15%):
    - Multiple agreeing facts with zero unresolved conflicts: 100 pts; minor conflict: 60 pts; high contradiction: 15 pts.
  - Factor 5 — Source Diversity (weight: 10%):
    - Mix of national major news, local news, and official sources: 100 pts; single source type: 50 pts.
- Compute composite `confidence_score` (integer 0 to 100) and qualitative label:
  - `HIGH`: 80–100
  - `MEDIUM`: 50–79
  - `LOW`: 0–49
- Generate transparent, explainable breakdown factors:
  - Positive indicators (e.g., `["Được 7 nguồn báo chí độc lập đưa tin", "Địa điểm nhất quán ở cấp đường/quận", "Nhiều thông tin sự kiện trùng khớp"]`).
  - Warning/caution indicators (e.g., `["Chỉ có 1 nguồn duy nhất đưa tin", "Vị trí chỉ xác định ở cấp tỉnh/thành", "Có thông tin thương vong chưa thống nhất"]`).
- Update `events.confidence_score` and confidence metadata in PostgreSQL.

### MUST NOT
- State or imply that a high confidence score certifies 100% absolute truth ("Tin chắc chắn đúng 100%").
- Calculate confidence solely as a function of raw article count (must reward source independence and fact consensus).
- Treat syndicated copies from the same parent media network as multiple independent sources.

## Architecture Constraints
- Conforms strictly to `prd.md` Section 4.3: Confidence indicates data strength and multi-source consensus, NOT certified absolute truth.
- Explainability is mandatory: UI must be able to present the breakdown to the user.

## Implementation Requirements
- Create `backend/app/modules/events/confidence.py`.
- Define `EventConfidenceDTO`:
  - `score`: int (0-100)
  - `level`: `HIGH` | `MEDIUM` | `LOW`
  - `factors`: dict of factor scores
  - `explanations`: list of human-readable bullet points
- Wire confidence calculation into event clustering and summary updates.

## Security Requirements
- Deterministic, bounded scoring logic immune to score manipulation by spamming duplicate syndicated articles.
- Sanitize explanation text before rendering or serializing to JSON.

## Performance Requirements
- Confidence score calculation execution < 5ms per event.

## Testing Requirements
- Unit tests:
  - Single-source event with province location produces LOW confidence (score < 45) with warning explanations.
  - Multi-source event (6 independent major news outlets) with consistent street address produces HIGH confidence (score > 85) with positive explanations.
  - Event with severe fact contradictions produces penalized confidence score and flags conflict in explanation list.
  - Verify that syndication check does not award independent points to duplicate network feeds.

## Expected Files / Modules
- `backend/app/modules/events/confidence.py`
- `backend/app/modules/events/schemas/confidence.py`
- `tests/unit/test_confidence_engine.py`

## Acceptance Criteria
- [ ] Confidence engine produces 0-100 scores based on the 5 documented factors.
- [ ] Human-readable explanation strings generated for every confidence evaluation.
- [ ] Language adheres strictly to neutral data strength wording ("được X nguồn độc lập đề cập").
- [ ] Unit tests pass for single-source, multi-source, and conflicting fact scenarios.

## Completion Report
When completed, report:
1. Confidence algorithm and factor weighting implementation.
2. Neutral wording standards for explanation strings.
3. Integration with event update pipeline.
4. Unit test execution results.

## Follow-up Tasks
- TASK-032 (Public Events API)
- TASK-033 (Public Event Detail API)
- TASK-037 (Event Quick Popup & Bottom Sheet)
- TASK-038 (Event Detail Panel)
- TASK-046 (Admin Review Queue & Audit Log)
