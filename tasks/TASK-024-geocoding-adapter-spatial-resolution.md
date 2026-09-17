# TASK-024 — Geocoding Adapter & Spatial Resolution Service

## Status
TODO

## Priority
P0

## Phase
Phase 1 — Intelligence Pipeline

## Depends On
- TASK-002
- TASK-023

## Objective
Implement the geocoding service and provider adapter (Google Maps Geocoding API / OpenStreetMap Nominatim / internal gazetteer) that transforms normalized address strings into WGS 84 spatial coordinates, bounding envelopes, and PostGIS geometry points while enforcing centroid fallbacks for coarse locations.

## Source of Truth
- `docs/04-data-architecture.md` (Geospatial, locations entity)
- `docs/10-security.md` (Google Maps key, Resource limits)
- `prd.md` (Section 8: Location Resolution & Geocoding, Section 23.2: False Precision)

## Scope

### MUST
- Implement geocoding provider interface `BaseGeocoderAdapter` with methods:
  - `async geocode(query: str, bounds_bias: Optional[dict] = None) -> GeocodeResult`
- Implement provider adapters:
  - `GoogleMapsGeocoderAdapter`: uses private server-side key (`MAPS_SERVER_KEY`), restricts search to country code `vn`.
  - `InternalGazetteerGeocoder`: uses pre-computed centroids and bounding boxes for all 63 Vietnamese provinces and major districts as an offline/fallback provider.
- Implement strict centroid fallback rule:
  - When the normalized location is only resolved at the Province/Municipality level (e.g. "tại Đà Nẵng"):
    - Set coordinates to the official administrative centroid of that province.
    - Set `location_label` to: `"Vị trí gần đúng — chỉ xác định được [Tỉnh/Thành]"`
    - Set `is_approximate = True`.
    - Do NOT place markers at arbitrary street addresses or specific buildings.
- Implement geocoding cache in Redis (key: `vnm:geocode:<normalized_query_hash>`, TTL: 30 days) to minimize external API costs and quota consumption.
- Return structured `ResolvedLocationDTO`:
  - `latitude`: float
  - `longitude`: float
  - `resolved_address`: str
  - `location_level`: enum
  - `location_confidence`: float
  - `is_approximate`: bool
  - `provider`: str (`GOOGLE_MAPS`, `INTERNAL_GAZETTEER`)
  - `raw_response`: Optional[dict]

### MUST NOT
- Use browser-restricted Google Maps API keys on the backend/worker server.
- Place markers at precise coordinates when the source evidence only supports broad regional certainty.
- Make unthrottled or redundant external geocoding requests for identical queries.

## Architecture Constraints
- Conforms to `prd.md` Section 8.3 & 23.2: Never infer street-level precision from province-level data.
- Server-side geocoding strictly separated from client-side map rendering credentials.

## Implementation Requirements
- Create `backend/app/modules/locations/geocoder/base.py`, `google.py`, `gazetteer.py`, `service.py`.
- Seed file containing official centroids and bounding boxes for all 63 Vietnamese provinces.
- Configure rate-limiting and quota tracking for Google Maps Geocoding API calls.

## Security Requirements
- `MAPS_SERVER_KEY` read strictly from private environment; never exposed via API responses.
- All query inputs sanitized to prevent URL injection or header injection into geocoder HTTP requests.

## Performance Requirements
- Cached geocode query latency < 5ms.
- External geocoding query timeout capped at 5s.

## Testing Requirements
- Unit and integration tests:
  - Province-level query ("Đà Nẵng") returns provincial centroid with `is_approximate: True` and label `"Vị trí gần đúng — chỉ xác định được TP. Đà Nẵng"`.
  - Full address query ("135 Hai Bà Trưng, Quận 1, TP.HCM") returns precise coordinate with `is_approximate: False` and HIGH confidence.
  - Cached query returns response from Redis without calling geocoder adapter mock.
  - External geocoder failure gracefully falls back to internal gazetteer for known administrative entities.

## Expected Files / Modules
- `backend/app/modules/locations/geocoder/base.py`
- `backend/app/modules/locations/geocoder/google.py`
- `backend/app/modules/locations/geocoder/gazetteer.py`
- `backend/app/modules/locations/geocoder/service.py`
- `backend/app/modules/locations/data/vn_centroids.json`
- `tests/unit/test_geocoder_service.py`

## Acceptance Criteria
- [ ] Geocoding service correctly resolves coordinates with explicit confidence and approximate flags.
- [ ] Centroid fallback rule is strictly enforced for province-level locations.
- [ ] Redis caching prevents redundant external geocoder requests.
- [ ] Internal gazetteer provides reliable offline fallback for all 63 provinces.

## Completion Report
When completed, report:
1. Geocoder adapters implemented.
2. Centroid dataset and fallback logic.
3. Cache strategy and quota controls.
4. Unit and integration test pass results.

## Follow-up Tasks
- TASK-025 (Geocoding Worker & Location Persistence)
- TASK-026 (Clustering Candidate Retrieval)
- TASK-035 (Google Maps Web Integration)
