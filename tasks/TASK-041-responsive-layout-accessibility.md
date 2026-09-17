# TASK-041 — Responsive Web Layout & Accessibility Polish

## Status
TODO

## Priority
P0

## Phase
Phase 1 — Product

## Depends On
- TASK-008
- TASK-035
- TASK-036
- TASK-037
- TASK-038
- TASK-039
- TASK-040

## Objective
Harmonize the entire responsive web application across all viewports (Mobile: 360–767px, Tablet: 768–1023px, Desktop: >=1024px, Wide: >=1440px), enforce touch target standards (>= 48px), eliminate hover-only critical paths, and conduct comprehensive WCAG AA accessibility verification in accordance with `docs/08-ui-ux-responsive.md`.

## Source of Truth
- `AGENTS.md` (Rule 8: Responsive is mandatory)
- `docs/08-ui-ux-responsive.md` (Breakpoints, Desktop, Tablet, Mobile, Touch targets, Accessibility)
- `adr/003-responsive-web-first.md` (Responsive Web as Primary Client)

## Scope

### MUST
- Ensure flawless multi-device presentation across exact semantic breakpoints:
  - Mobile (360–767px): Full-screen map, floating search bar, filter drawer, bottom sheet preview and full-screen detail overlay, toggleable tab for feed list, sticky action row when useful.
  - Tablet (768–1023px): Primary map viewport, collapsible side feed panel, slide-over detail drawer, controls positioned to never cover native Google Maps zoom/compass controls.
  - Desktop (>= 1024px): Header with search & filters, split map and persistent feed panel, slide-over detail drawer, bottom status/legend bar.
  - Wide (>= 1440px): Constrained max-width layout or expanded multi-column feed for ultra-wide screens.
- Enforce touch target requirements:
  - All interactive buttons, filter chips, map markers, and drawer handles must have a minimum clickable/tappable area of 48x48px (or 44x44px with padding) on touch devices.
- Guarantee zero hover-only dependencies:
  - All essential information, preview popups, source links, and tooltips must be accessible via direct tap/click and keyboard navigation.
- Implement WCAG AA Accessibility standards:
  - Visible keyboard focus rings (`:focus-visible`) on all interactive controls.
  - Full keyboard navigation: `Tab` through header, filters, feed cards, and drawer; `Escape` closes drawers and popups; arrow keys navigate list items.
  - Text color contrast ratio >= 4.5:1 for normal text and >= 3:1 for large text against background.
  - Screen reader semantic markup (`aria-label`, `aria-expanded`, `role="dialog"`, `role="feed"`, live regions for filter updates).
  - Status indicators and category badges must not rely on color alone (include text labels or distinct geometric icons).

### MUST NOT
- Allow horizontal scrolling or layout clipping at 360px viewport width.
- Rely on device-specific user-agent sniffing hacks instead of semantic CSS media queries and container queries.
- Remove visible focus outlines without providing an accessible high-contrast alternative.

## Architecture Constraints
- Conforms strictly to Rule 8 of `AGENTS.md`: Mobile-first responsive implementation; do not design desktop first then shrink.
- Conforms to ADR-003: Single responsive web application client.

## Implementation Requirements
- Audit and refine CSS stylesheets across all frontend components:
  - `frontend/src/styles/responsive.css`
  - `frontend/src/styles/accessibility.css`
- Implement responsive layout tester helper or storybook stories simulating 360px, 768px, 1024px, 1440px.
- Skip-to-content accessibility link (`<a href="#main-content" class="skip-link">`).

## Security Requirements
- Ensure responsive frames and overlays do not facilitate clickjacking (overlay opacity and z-index hierarchy clearly audited).

## Performance Requirements
- Resize observer and orientation change reflow < 16ms (no visible layout thrashing).

## Testing Requirements
- Automated accessibility and responsive tests:
  - Run `@axe-core/react` / `lighthouse` accessibility audit: zero critical or serious WCAG AA violations.
  - Automated viewport tests verifying zero horizontal overflow (`scrollWidth <= clientWidth`) at 360px, 390px, 412px, 768px, 1024px, 1440px.
  - Keyboard navigation test: verify user can tab through entire interface and open/close an event without touching mouse.
  - Color contrast automated audit confirming 4.5:1 ratio across light and dark mode tokens.

## Expected Files / Modules
- `frontend/src/styles/responsive.css`
- `frontend/src/styles/accessibility.css`
- `frontend/src/components/common/SkipLink.tsx`
- `tests/frontend/accessibility.test.tsx`
- `tests/frontend/responsive_viewports.test.tsx`

## Acceptance Criteria
- [ ] Application renders cleanly without overflow on 360px mobile, 768px tablet, and 1280px desktop.
- [ ] Touch targets measure at least 48x48px on mobile viewports.
- [ ] No interactions require mouse hovering.
- [ ] Automated accessibility test passes WCAG AA compliance standards with zero critical errors.
- [ ] Keyboard navigation allows full interaction with filters, map markers, feed, and detail panel.

## Completion Report
When completed, report:
1. Breakpoint implementation and layout adjustments.
2. Touch target audit results.
3. Accessibility test results (axe-core / lighthouse scores).
4. Viewport overflow verification across 360px, 768px, 1024px, 1440px.

## Follow-up Tasks
- TASK-047 (Caching & Performance Optimization)
- TASK-049 (End-to-End Critical Flow Validation)
- TASK-050 (Phase 1 Production Readiness)
