# TASK-056 — Trend & Hotspot UI Extension

## Status
TODO

## Priority
P1

## Phase
Phase 2 — Trend Engine

## Depends On
- TASK-036
- TASK-038
- TASK-040
- TASK-055

## Objective
Extend the frontend map, feed, and detail views to visually surface trending events and regional hotspots: flame indicators on trending markers, a dedicated "Xu hướng" (Trending) sort tab in the feed, trend score breakdowns in detail panels, and an optional regional density heatmap layer.

## Source of Truth
- `docs/01-product-scope.md` (Phase 2: hotspot/heatmap)
- `prd.md` (Section 25.4: Trend vs Confidence, Section 39: Trend Map, Area Heatmap)

## Scope

### MUST
- Implement visual trend indicators on map markers:
  - Events with `trend_score >= 85` (EXPLODING): render animated flame glyph badge / pulsing halo.
  - Events with `trend_score >= 65` (TRENDING): render orange trend pill tag.
- Extend Event Feed view:
  - Add `🔥 Thịnh hành` (Trending) tab option alongside `Mới nhất` (Newest).
  - Cards in Trending tab display Trend Score pill (e.g. `🔥 92/100`) and velocity indicator (e.g. `+8 bài/giờ`).
- Extend Event Detail Panel:
  - Render dual-score header section displaying both `Độ tin cậy` (Confidence Score: e.g. 42/100) and `Xu hướng` (Trend Score: e.g. 95/100).
  - Clear descriptive tooltip/callout explaining the difference: "Xu hướng phản ánh tốc độ quan tâm tăng vọt trong 24h qua; Độ tin cậy phản ánh số lượng bằng chứng và nguồn độc lập hiện có."
- Implement toggleable Regional Hotspot Layer:
  - Optional map layer button: `[ Bản đồ nhiệt ]` (Heatmap toggle).
  - Renders Google Maps HeatmapLayer (`google.maps.visualization.HeatmapLayer`) weighted by `trend_score` across Vietnamese provinces.
  - Smoothly enables/disables without reloading the base map.

### MUST NOT
- Replace or obscure category icons entirely with trend badges (flame badge is an accent badge on the existing category marker).
- Mislead users by conflating trend with truth in UI copy.
- Impair map panning performance when the heatmap layer is active.

## Architecture Constraints
- Conforms strictly to ADR-003 and `docs/08-ui-ux-responsive.md`: Seamless responsive integration across mobile and desktop.
- Heatmap layer is optional and client-toggled; does not degrade default map load time.

## Implementation Requirements
- Create `frontend/src/components/map/HeatmapLayer.tsx` and `frontend/src/components/trend/TrendBadge.tsx`.
- Update `MarkerLayer.tsx` to include trend badges.
- Update `EventDetailPanel.tsx` to display dual Confidence and Trend score meters.
- Update `EventFeedView.tsx` with Trending tab.

## Security Requirements
- Safe number formatting and sanitization of trend explanation tooltips.

## Performance Requirements
- Heatmap layer toggle execution < 100ms.
- Marker flame micro-animations use CSS `transform` / `opacity` (GPU accelerated, 60 FPS).

## Testing Requirements
- Component tests:
  - Event with `trend_score >= 85` renders flame indicator on marker.
  - Selecting "Thịnh hành" tab in feed displays events ordered by Trend Score.
  - Detail panel renders both Trend Score and Confidence Score with independent values and clear explanatory labels.
  - Heatmap toggle accurately mounts and unmounts Google Maps HeatmapLayer.
  - Responsive test: Trend badges scale cleanly on mobile viewports.

## Expected Files / Modules
- `frontend/src/components/trend/TrendBadge.tsx`
- `frontend/src/components/trend/TrendDetailCard.tsx`
- `frontend/src/components/map/HeatmapLayer.tsx`
- `frontend/src/styles/trend.css`
- `tests/frontend/TrendUI.test.tsx`

## Acceptance Criteria
- [ ] Markers visibly highlight exploding/trending events with flame accents.
- [ ] Feed includes working "Thịnh hành" sort option displaying velocity badges.
- [ ] Detail panel clearly presents both Trend Score and Confidence Score independently with explanatory text.
- [ ] Heatmap layer toggles smoothly across all viewports.
- [ ] Responsive design maintains usability across mobile, tablet, and desktop.

## Completion Report
When completed, report:
1. Trend UI visual design and badge styling.
2. Dual-score presentation in detail panel.
3. Google Maps HeatmapLayer integration.
4. Component test execution results across viewports.

## Follow-up Tasks
- TASK-057 (Phase 3 TTS initiation)
