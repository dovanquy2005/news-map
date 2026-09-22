# TASK-021 — Event & Entity Extraction Schema Validation

## Status
DONE

## Priority
P0

## Phase
Phase 1 — Intelligence Pipeline

## Depends On
- TASK-020

## Objective
Implement strict schema validation and domain sanitization for raw LLM extraction output using Pydantic/Zod, establishing the mandatory boundary between untrusted model responses and internal database models.

## Source of Truth
- `AGENTS.md` (AI output is untrusted)
- `docs/06-ai-nlp-pipeline.md` (Structured output, Extraction fields)
- `prd.md` (Section 7.1: Event Categories, Section 7.2: Extraction Schema)

## Scope

### MUST
- Implement `EventExtractionSchema` enforcing the exact contract:
  - `event_title`: string (10 to 300 characters, required)
  - `event_type`: enum string matching standard categories (`ACCIDENT`, `FIRE`, `CRIME`, `PUBLIC_SAFETY`, `WEATHER`, `FLOOD`, `TRAFFIC`, `PUBLIC_EVENT`, `POLITICS`, `BUSINESS`, `HEALTH`, `EDUCATION`, `ENTERTAINMENT`, `SPORTS`, `OTHER`)
  - `location_text`: Optional[str] (verbatim location phrase mentioned in article)
  - `province`: Optional[str] (standardized Vietnamese province/municipality name)
  - `district`: Optional[str] (district/town/city name)
  - `ward`: Optional[str] (ward/commune name)
  - `occurred_at`: Optional[datetime] (inferred event occurrence time, UTC)
  - `facts`: list of strings (concrete factual claims from text, max 10 facts)
  - `entities`: list of objects (`name`: str, `type`: `PERSON` | `ORGANIZATION` | `LOCATION` | `VEHICLE` | `OTHER`)
  - `uncertainty_notes`: Optional[str] (explicitly noted uncertainties or conflicting claims)
  - `extraction_confidence`: float (0.0 to 1.0)
- Implement schema validator pipeline:
  - `Raw LLM String -> JSON Parser -> Pydantic Schema Validation -> Domain Rule Sanity Checks -> ValidatedExtractionDTO`
- Implement error handling for invalid model outputs:
  - If JSON is malformed: attempt fallback parser (e.g. regex JSON block extractor).
  - If schema validation fails: retry once with corrective prompt.
  - If retry fails: mark job as validation failure and route to Dead-Letter Queue / Admin review queue.
- Validate temporal plausibility: `occurred_at` cannot be in the future beyond 24 hours, and cannot precede article publication by more than 10 years without warning.

### MUST NOT
- Allow raw LLM output to be persisted directly into the database without passing schema validation.
- Accept fabricated categories outside the defined enum list (fallback to `OTHER`).
- Invent street-level or coordinates at this stage (geocoding is handled strictly by TASK-024).

## Architecture Constraints
- Conforms strictly to Rule 7 in `AGENTS.md`: `raw input -> model -> schema validation -> business validation -> persistence`.
- Zero database write permissions given to unvalidated model payloads.

## Implementation Requirements
- Create `backend/app/modules/events/schemas/extraction.py` and `validator.py`.
- Define enum `EventCategory` matching `prd.md` Section 7.1.
- Implement domain sanitizers:
  - Clean whitespace and trim text.
  - Standardize province names against canonical list of 63 provinces/cities in Vietnam.
  - Convert ISO timestamp strings to UTC datetime objects.

## Security Requirements
- JSON parser must reject deeply nested or cyclic JSON payloads (max depth 10).
- Strip any residual prompt tokens or injection markers from extracted strings.

## Performance Requirements
- Schema validation and domain checks execute in < 2ms per extraction result.

## Testing Requirements
- Comprehensive schema unit tests:
  - Valid extraction JSON passes and produces `ValidatedExtractionDTO`.
  - Missing required `event_title` raises `ValidationError`.
  - Invalid `event_type` raises `ValidationError` or falls back to `OTHER`.
  - Markdown-wrapped JSON (e.g. ```json ... ```) is parsed correctly by fallback parser.
  - Malformed/truncated JSON fails validation and triggers the retry/DLQ signal.
  - Future timestamp (> 24h) is caught and flagged by temporal sanity check.

## Expected Files / Modules
- `backend/app/modules/events/schemas/extraction.py`
- `backend/app/modules/events/schemas/categories.py`
- `backend/app/modules/events/validators/extraction_validator.py`
- `tests/unit/test_extraction_validator.py`
- `tests/fixtures/llm_outputs/valid_extraction.json`
- `tests/fixtures/llm_outputs/invalid_extraction.json`

## Acceptance Criteria
- [x] Schema validator strictly enforces all fields from `prd.md` Section 7.2.
- [x] Fallback parser handles markdown fences and common LLM formatting artifacts.
- [x] Invalid model outputs are safely caught without throwing unhandled exceptions.
- [x] Unit tests verify all valid, edge-case, and adversarial model payloads.

## Completion Report
When completed, report:
1. Pydantic extraction schema definition.
2. Category enums and province standardizer implementation.
3. Fallback parsing and error handling workflow.
4. Unit test execution results.

## Follow-up Tasks
- TASK-022 (Event Extraction Worker)
- TASK-023 (Location Extraction & Hierarchical Normalization)
- TASK-046 (Admin Review Queue & Audit Log)
