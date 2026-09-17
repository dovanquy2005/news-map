# TASK-037 — Event Quick Popup & Mobile Bottom Sheet Preview

## Status
TODO

## Priority
P0

## Phase
Phase 1 — Product

## Depends On
- TASK-008
- TASK-036

## Objective
Implement the responsive event preview component: an InfoWindow/Card popup on desktop viewports and a swipeable bottom sheet preview on mobile viewports (< 768px), displaying the event title, category, location, time, source/article count, confidence badge, and a call-to-action button to open full details.

## Source of Truth
- `AGENTS.md` (Responsive is mandatory)
- `docs/08-ui-ux-responsive.md` (Mobile bottom sheet, Breakpoints)
- `adr/003-responsive-web-first.md` (Bottom-sheet event details)
- `prd.md` (Section 15: Event Quick Popup)

## Scope

### MUST
- Implement responsive preview presentation:
  - Desktop / Tablet (>= 768px): Lightweight floating card or Google Maps OverlayView popup anchored adjacent to the clicked marker.
  - Mobile (360–767px): Touch-friendly swipeable bottom sheet preview docked at the bottom of the screen with a swipe handle.
- Display required preview fields:
  - Event title (prominent, 2-line clamp).
  - Category badge (color-coded).
  - Location label and approximate indicator (if approximate).
  - Occurred time / first reported time formatted in Vietnam Time (ICT, UTC+7).
  - Multi-source metrics: Article count and independent source count (e.g. `12 bài · 7 nguồn`).
  - Confidence label: `HIGH` (Green), `MEDIUM` (Amber), `LOW` (Neutral).
  - Call-to-action button: "Xem chi tiết →" (opens Event Detail Panel).
  - Close button ("✕") and backdrop dismiss.
- Sync selected event with URL query parameter: `?event=<eventId>` so preview states are shareable.

### MUST NOT
- Obscure the entire mobile viewport with the quick popup; bottom sheet must peek at 30-40% height, allowing map context above.
- Make the CTA button smaller than 48x48px on mobile devices.
- Require double-clicking or hovering to reveal the preview.

## Architecture Constraints
- Conforms strictly to ADR-003 and `docs/08-ui-ux-responsive.md`: Bottom sheet for event popup/detail on mobile; no hover-only requirements.
- Single unified component adapting to viewport size via CSS/media queries.

## Implementation Requirements
- Create `frontend/src/components/events/EventQuickPopup.tsx` and `EventBottomSheet.tsx`.
- Support touch swipe gestures on mobile (swipe down to dismiss, swipe up or tap to expand full detail).
- Keyboard accessible: `Escape` key closes preview, focus trapped properly while open.

## Security Requirements
- HTML output encoding on all event titles and summaries to protect against XSS.

## Performance Requirements
- Popup/sheet open animation < 150ms with 60 FPS CSS transforms.
- Zero extra network request needed to show the quick preview (uses data already loaded from viewport event list).

## Testing Requirements
- Component tests:
  - On mobile viewport (375px), renders bottom sheet drawer at bottom of screen.
  - On desktop viewport (1280px), renders floating map popup.
  - Displays title, counts (`12 bài · 7 nguồn`), and confidence badge correctly.
  - Clicking "Xem chi tiết" triggers full detail panel handler.
  - Clicking close button or pressing Escape dismisses preview and clears `?event=` URL parameter.

## Expected Files / Modules
- `frontend/src/components/events/EventQuickPopup.tsx`
- `frontend/src/components/events/EventBottomSheet.tsx`
- `frontend/src/components/events/EventPreviewContainer.tsx`
- `frontend/src/styles/bottom-sheet.css`
- `tests/frontend/EventQuickPopup.test.tsx`

## Acceptance Criteria
- [ ] Clicking a marker reveals the quick preview card on desktop and bottom sheet on mobile.
- [ ] All required fields from `prd.md` Section 15 are displayed cleanly.
- [ ] Touch gestures allow smooth drag-to-dismiss on mobile devices.
- [ ] CTA button triggers transition into full event detail view.

## Completion Report
When completed, report:
1. Quick popup and mobile bottom sheet implementation.
2. Responsive behavior across mobile/desktop breakpoints.
3. Touch gesture and keyboard accessibility handling.
4. Component test execution results.

## Follow-up Tasks
- TASK-038 (Event Detail Panel Component)
- TASK-040 (Event Feed View & Map Synchronization)
- TASK-041 (Responsive Layout & Accessibility Polish)
