# TASK-036 — Map Marker Rendering & Dynamic Marker Clustering

## Status
TODO

## Priority
P0

## Phase
Phase 1 — Product

## Depends On
- TASK-032
- TASK-035

## Objective
Implement client-side marker rendering and dynamic marker clustering on Google Maps using `@googlemaps/markerclusterer`, rendering distinct visual markers per event category while preventing browser DOM node explosion.

## Source of Truth
- `AGENTS.md` (Performance rules: Do not render thousands of marker DOM nodes)
- `docs/08-ui-ux-responsive.md` (Performance: marker clustering)
- `prd.md` (Section 4.1: Marker = Event, Section 14.2: Marker, Section 14.3: Cluster)

## Scope

### MUST
- Implement event marker rendering on Google Maps:
  - Each marker represents exactly ONE event (never an individual article).
  - Marker visual styling: distinct SVG pin/glyph color-coded by event category (`ACCIDENT`: red/orange, `FIRE`: amber/red, `WEATHER`: blue, `TRAFFIC`: purple, etc.).
  - Approximate location indicator: if `isApproximate = true`, render dashed border or subtle aura indicating broad regional precision.
  - Marker size: minimum 44x44px clickable target area for touch devices.
- Implement dynamic marker clustering via `@googlemaps/markerclusterer`:
  - When zoom level is zoomed out, group adjacent markers into cluster bubbles displaying the event count (e.g. `(18)`).
  - Clicking a cluster bubble smoothly zooms into that region bounds (`map.fitBounds()`).
- Implement marker click interaction:
  - Clicking an individual marker selects the event, centers the map slightly offset for drawer/popup, and opens the preview.
- Marker lifecycle management:
  - Efficiently add/remove markers as the viewport changes without leaking memory or instantiating redundant Google Maps marker objects.

### MUST NOT
- Render thousands of raw DOM marker nodes simultaneously without clustering (causes browser freezing).
- Represent articles as separate markers; multiple articles must remain grouped inside their single event marker.
- Require mouse hover to interact with markers (all interactions must support touch click).

## Architecture Constraints
- Conforms to `AGENTS.md` Rule 9 and `docs/08-ui-ux-responsive.md`: Avoid thousands of React DOM nodes for markers.
- Conforms to `prd.md` Section 4.1: 1 Event = 1 Marker.

## Implementation Requirements
- Create `frontend/src/components/map/MarkerLayer.tsx` and `frontend/src/components/map/clustering.ts`.
- Use Google Maps AdvancedMarkerElement or standard Marker with SVG icons.
- Create SVG icon generator utility mapping `category` to styled SVG data URI.
- Clean up markers during unmount or data refresh using `markerClusterer.clearMarkers()`.

## Security Requirements
- All data passed to markers (tooltips, labels) sanitized to prevent client-side script execution.

## Performance Requirements
- Smooth 60 FPS panning and zooming with 500+ markers loaded in clustering tree.
- Marker cluster rendering update < 16ms.

## Testing Requirements
- Component and unit tests:
  - Verifies correct number of markers created from API event list.
  - Verifies category color mapping assigns appropriate icon to `FIRE` vs `ACCIDENT`.
  - Verifies approximate location flag adds visual styling indicator.
  - Test cluster click: triggers `map.fitBounds` with cluster bounds.
  - Test memory cleanup: updating event data properly disposes previous marker instances.

## Expected Files / Modules
- `frontend/src/components/map/MarkerLayer.tsx`
- `frontend/src/components/map/clustering.ts`
- `frontend/src/components/map/icons.ts`
- `frontend/src/styles/map.css`
- `tests/frontend/MarkerLayer.test.tsx`

## Acceptance Criteria
- [ ] Markers render on map with distinct category visual styling.
- [ ] Zooming out groups markers into cluster bubbles with count numbers.
- [ ] Clicking a cluster smoothly zooms in to reveal individual events.
- [ ] Clicking a marker triggers event selection.
- [ ] No performance degradation or memory leak during frequent viewport movement.

## Completion Report
When completed, report:
1. Marker clusterer implementation.
2. SVG marker icon palette and category mapping.
3. Approximate location visual indicator design.
4. Performance verification under 500+ markers.

## Follow-up Tasks
- TASK-037 (Event Quick Popup & Bottom Sheet)
- TASK-038 (Event Detail Panel Component)
- TASK-040 (Event Feed View & Map Sync)
