# TASK-025 — Geocoding Worker & Location Persistence

## Status
TODO

## Priority
P0

## Phase
Phase 1 — Intelligence Pipeline

## Depends On
- TASK-004
- TASK-005
- TASK-007
- TASK-022
- TASK-023
- TASK-024

## Objective
Implement the background worker that consumes location resolution tasks from `geocoding_queue`, normalizes and geocodes the address, persists the location entity with PostGIS geometry points, and updates the article's location metadata.

## Source of Truth
- `docs/04-data-architecture.md` (locations entity, Geospatial)
- `docs/11-performance-scalability.md` (Worker scaling)
- `prd.md` (Section 8: Location Resolution & Geocoding)

## Scope

### MUST
- Implement `GeocodingWorker` consuming `GeocodeLocationJob` from `geocoding_queue`:
  1. Extract article metadata and extracted location text.
  2. If location text is missing or explicitly non-geographical:
     - Record location as `NULL` / `UNRESOLVED`, log informational notice, and finish job.
  3. Execute `LocationNormalizer` to get administrative components and level.
  4. Execute `GeocoderService` to obtain coordinates, confidence, and `is_approximate` flag.
  5. Check if identical resolved location exists in `locations` table (within 50 meters or identical address string):
     - If exists: reuse existing `location_id`.
     - If not: insert new `Location` row with `geom = ST_SetSRID(ST_MakePoint(lng, lat), 4326)`.
  6. Update article record with resolved `location_id`.
- Support retry with exponential backoff on transient network or external API errors.
- Record metrics: `geocode_success_total`, `geocode_approximate_total`, `geocode_failure_total`, `geocode_duration_seconds`.

### MUST NOT
- Stop or crash the worker when an address is unresolvable (mark confidence as 0 and persist unresolvable state).
- Create duplicate `locations` records for the exact same physical coordinates and address.
- Insert geometry with invalid or mismatched spatial reference identifiers (must strictly be SRID 4326).

## Architecture Constraints
- Conforms to `docs/04-data-architecture.md`: Canonical geometry point stored in PostGIS.
- Asynchronous execution: Never blocks the web API or incoming feed ingestion.

## Implementation Requirements
- Create `workers/geocoding/worker.py` and `backend/app/modules/locations/repository.py`.
- SQL/ORM mapping for PostGIS Point geometry:
  - Latitude bounds check: -90.0 to 90.0 (Vietnam bounds: approx 8.0 to 24.0 N).
  - Longitude bounds check: -180.0 to 180.0 (Vietnam bounds: approx 102.0 to 110.0 E).
- Handle location deduplication via spatial distance check (`ST_DWithin`) or composite hash on `(province, district, ward, address)`.

## Security Requirements
- All geocoder inputs and outputs validated before SQL insertion.
- Coordinates validated to ensure they fall within acceptable terrestrial boundaries.

## Performance Requirements
- Geocoding worker throughput: 20 jobs/second when leveraging Redis geocode cache.
- PostGIS point insertion < 10ms.

## Testing Requirements
- Integration tests:
  - Push `GeocodeLocationJob` to `geocoding_queue` with valid Vietnamese location text.
  - Worker processes job: verifies `locations` row is created with valid PostGIS point (`ST_X(geom)` = lng, `ST_Y(geom)` = lat).
  - Verifies article row is updated with `location_id`.
  - Push second job with same location: verifies existing `location_id` is reused without duplicate insertion.
  - Push job with unresolvable text: verifies graceful handling and low confidence assignment.

## Expected Files / Modules
- `workers/geocoding/worker.py`
- `workers/geocoding/pipeline.py`
- `backend/app/modules/locations/service.py`
- `backend/app/modules/locations/repository.py`
- `tests/integration/test_geocoding_worker.py`

## Acceptance Criteria
- [ ] Worker consumes from `geocoding_queue` and persists locations with SRID 4326 PostGIS geometry.
- [ ] Approximate locations receive appropriate labels and confidence scores.
- [ ] Location deduplication prevents redundant location rows.
- [ ] Automated tests verify point geometry correctness and relationship with articles.

## Completion Report
When completed, report:
1. Worker queue handling implementation.
2. PostGIS geometry persistence details.
3. Location deduplication logic.
4. Test execution results.

## Follow-up Tasks
- TASK-026 (Clustering Candidate Retrieval)
- TASK-028 (Clustering Worker & Provenance Persistence)
- TASK-032 (Public Events API)
