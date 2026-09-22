# TASK-023 — Location Extraction & Hierarchical Normalization

## Status
DONE

## Priority
P0

## Phase
Phase 1 — Intelligence Pipeline

## Depends On
- TASK-021
- TASK-022

## Objective
Implement the Vietnamese geospatial administrative hierarchy normalization service that parses location text into standard administrative levels (Country, Province/Municipality, District, Ward, Street/POI) and assigns initial location confidence.

## Source of Truth
- `docs/04-data-architecture.md` (Geospatial, locations entity)
- `prd.md` (Section 8.2: Location Hierarchy, Section 8.3: Location Confidence)

## Scope

### MUST
- Implement location hierarchy parser for Vietnamese administrative divisions:
  - Level 1: Country (`Việt Nam`)
  - Level 2: Province / Municipality (63 standard units: `TP. Hồ Chí Minh`, `Hà Nội`, `Đà Nẵng`, etc.)
  - Level 3: District / Urban District / Town (`Quận 1`, `Huyện Bình Chánh`, `TP. Thủ Đức`, etc.)
  - Level 4: Ward / Commune / Township (`Phường Bến Nghé`, `Xã Tân Nhựt`, etc.)
  - Level 5: Street / Highway / Bridge (`Đường Nguyễn Huệ`, `Quốc lộ 1A`, `Cầu Sài Gòn`)
  - Level 6: Landmark / Specific POI / House number (`Chợ Bến Thành`, `Bệnh viện Chợ Rẫy`)
- Provide canonical administrative reference dataset for Vietnam (provinces, districts, common aliases like `Sài Gòn` -> `TP. Hồ Chí Minh`).
- Standardize location confidence score based on the deepest resolved administrative level:
  - Landmark / POI / Street address: HIGH (0.85 - 1.00)
  - Ward / Commune: MEDIUM-HIGH (0.70 - 0.84)
  - District / County: MEDIUM (0.50 - 0.69)
  - Province only: LOW-MEDIUM (0.30 - 0.49)
  - Unresolved / National general: LOW (0.00 - 0.29)
- Produce `NormalizedLocationDTO` containing raw text, structured hierarchy components, resolved level, and baseline confidence.

### MUST NOT
- Guess or infer a specific street or ward if the source article text only mentions a province or city.
- Hardcode brittle regexes without normalization for common Vietnamese spelling variations (e.g. `Tp.HCM`, `TP. HCM`, `Tp Hồ Chí Minh`, `Sài Gòn`).
- Create spatial coordinates directly in this task (spatial coordinate resolution is owned by TASK-024).

## Architecture Constraints
- Conforms to `docs/04-data-architecture.md`: Never infer street-level precision from province-level data.
- Pure deterministic domain service with zero external network dependency.

## Implementation Requirements
- Create `backend/app/modules/locations/normalizer.py` and `backend/app/modules/locations/data/vn_administrative.json`.
- Normalize aliases and abbreviations:
  - `TP.HCM`, `Tp. HCM`, `Sài Gòn` -> `TP. Hồ Chí Minh`
  - `HN`, `Hà nội` -> `Hà Nội`
  - `ĐN` -> `Đà Nẵng`
- Output DTO:
  - `raw_text`: str
  - `country`: str
  - `province`: Optional[str]
  - `district`: Optional[str]
  - `ward`: Optional[str]
  - `street`: Optional[str]
  - `landmark`: Optional[str]
  - `location_level`: enum (`PROVINCE`, `DISTRICT`, `WARD`, `STREET`, `POI`, `UNKNOWN`)
  - `baseline_confidence`: float

## Security Requirements
- Input length limits (max 500 characters) to prevent regular expression denial of service (ReDoS).
- Sanitized strings free of control characters.

## Performance Requirements
- Location parsing execution time < 5ms per text string.

## Testing Requirements
- Unit tests:
  - Parses "Đường Nguyễn Huệ, Phường Bến Nghé, Quận 1, TP.HCM" into levels 2, 3, 4, 5 with HIGH confidence.
  - Parses "Quận 7, TP. Hồ Chí Minh" into levels 2, 3 with MEDIUM confidence.
  - Parses "tại Đà Nẵng" into level 2 with LOW-MEDIUM confidence.
  - Recognizes aliases: "Sài Gòn" correctly resolves to "TP. Hồ Chí Minh".
  - Malformed or non-geographical text returns UNKNOWN level with LOW confidence.

## Expected Files / Modules
- `backend/app/modules/locations/normalizer.py`
- `backend/app/modules/locations/schemas.py`
- `backend/app/modules/locations/data/vn_administrative.json`
- `tests/unit/test_location_normalizer.py`

## Acceptance Criteria
- [ ] Vietnamese administrative divisions dataset includes all 63 provinces and major cities.
- [ ] Location hierarchy parser identifies administrative components accurately.
- [ ] Confidence score aligns strictly with administrative granularity.
- [ ] Unit tests pass across all specified address variations and edge cases.

## Completion Report
When completed, report:
1. Administrative dataset structure.
2. Normalization logic and alias mappings.
3. Confidence scoring thresholds.
4. Unit test execution results.

## Follow-up Tasks
- TASK-024 (Geocoding Adapter & Spatial Resolution Service)
- TASK-025 (Geocoding Worker & Location Persistence)
