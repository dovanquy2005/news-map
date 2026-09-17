# TASK-035 — Google Maps Web Integration & Viewport Bounds Synchronizer

## Status
TODO

## Priority
P0

## Phase
Phase 1 — Product

## Depends On
- TASK-008
- TASK-032

## Objective
Integrate the Google Maps JavaScript API into the responsive web application, implement camera controls and viewport bounds debouncing, sync map position with browser URL query parameters (`lat`, `lng`, `zoom`), and trigger viewport-based event fetching.

## Source of Truth
- `docs/08-ui-ux-responsive.md` (Product principle, Performance, State model)
- `docs/10-security.md` (Google Maps key)
- `docs/11-performance-scalability.md` (Public map query)
- `prd.md` (Section 14.1: Main map, Section 33: Performance Requirements)

## Scope

### MUST
- Load Google Maps JavaScript API asynchronously using `@googlemaps/js-api-loader` with browser-restricted key (`MAPS_BROWSER_KEY`).
- Center the map on Vietnam by default (approx lat: 16.0471, lng: 107.8350, zoom: 6).
- Implement viewport bounds change listener with debouncing (300ms) on `idle` / `bounds_changed` events.
- Extract current bounding box (`minLng,minLat,maxLng,maxLat`) and feed it into TanStack Query to trigger `GET /api/v1/events?bbox=...`.
- Implement two-way synchronization with browser URL state:
  - When user pans or zooms, update URL parameters (`?lat=10.77&lng=106.70&zoom=12`) via `replaceState` without reloading the page.
  - When user opens a URL with coordinate parameters, initialize map camera at those coordinates.
- Ensure smooth touch interaction on mobile devices (pinch-to-zoom, two-finger pan, gesture handling).

### MUST NOT
- Fetch events without viewport bounding box constraints (never load entire country in one request).
- Trigger API requests on every individual pixel mousemove/drag event (debouncing is mandatory).
- Leak server-side Google Maps private credentials into client JavaScript bundles.

## Architecture Constraints
- Conforms strictly to ADR-003 and `docs/08-ui-ux-responsive.md`: Map is primary across all viewports; full screen on mobile, split on desktop.
- Security: Browser key must be restricted by HTTP referrer domain in Google Cloud Console.

## Implementation Requirements
- Create `frontend/src/components/map/GoogleMapView.tsx` and `useMapBounds.ts`.
- Set map styling options: clean, readable cartography with subdued default POIs to prioritize news markers.
- Implement loading skeleton and offline/error fallback state if Maps API fails to load.

## Security Requirements
- Ensure browser key is passed via `NEXT_PUBLIC_MAPS_BROWSER_KEY` or `VITE_MAPS_BROWSER_KEY` and restricted to authorized production/development domain origins.
- Validate incoming URL latitude and longitude values before applying to map camera.

## Performance Requirements
- Initial map interactive render < 2.5s on broadband (PRD target < 3s).
- Viewport query debounce: exactly 1 request per pan/zoom pause.

## Testing Requirements
- Component and unit tests:
  - Maps loader initializes with expected API key and parameters.
  - Camera movement updates URL parameters cleanly.
  - Viewport bounds calculation correctly derives `minLng,minLat,maxLng,maxLat`.
  - Rapid map movement debounce test: fires exactly 1 API call after camera settles.

## Expected Files / Modules
- `frontend/src/components/map/GoogleMapView.tsx`
- `frontend/src/components/map/MapContainer.tsx`
- `frontend/src/hooks/useMapBounds.ts`
- `frontend/src/hooks/useMapCamera.ts`
- `tests/frontend/GoogleMapView.test.tsx`

## Acceptance Criteria
- [ ] Google Maps loads smoothly across desktop, tablet, and mobile browsers.
- [ ] Panning and zooming triggers debounced viewport bounding-box API fetches.
- [ ] Map center and zoom are reflected in browser URL query parameters.
- [ ] Touch gestures on mobile devices operate fluidly without viewport jumping.

## Completion Report
When completed, report:
1. Google Maps JS API loader setup and domain restriction.
2. Viewport debouncing mechanism and query hook.
3. Two-way URL state synchronization flow.
4. Test execution results.

## Follow-up Tasks
- TASK-036 (Map Marker Rendering & Dynamic Clustering)
- TASK-037 (Event Quick Popup & Bottom Sheet)
- TASK-040 (Event Feed View & Map Synchronization)
