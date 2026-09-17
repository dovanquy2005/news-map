# TASK-008 — Frontend Application Foundation (Responsive Web Shell & Design System)

## Status
TODO

## Priority
P0

## Phase
Phase 0 — Foundation

## Depends On
- TASK-001
- TASK-002

## Objective
Initialize the single responsive web application shell (React + TypeScript), setup the core design system and responsive layout tokens, configure TanStack Query and client routing, and establish responsive view containers conforming to `docs/08-ui-ux-responsive.md` and `adr/003-responsive-web-first.md`.

## Source of Truth
- `AGENTS.md` (Responsive is mandatory)
- `docs/08-ui-ux-responsive.md` (Product principle, Breakpoints, Layouts)
- `docs/15-dev-conventions.md` (Naming, Time)
- `adr/003-responsive-web-first.md` (Responsive Web as Primary Client)
- `prd.md` (Section 28: UI/UX Structure)

## Scope

### MUST
- Build one responsive web application (React, TypeScript, Vite/Next.js) supporting all target viewports:
  - Mobile: 360–767px
  - Tablet: 768–1023px
  - Desktop: >=1024px (Wide: >=1440px)
- Establish design system tokens (colors, typography, spacing, elevations, transitions, touch target sizes >= 48px).
- Implement responsive app shell:
  - Header: Branding, search bar placeholder, filter trigger, date selector.
  - Main viewport container: Split map/feed container on desktop, full-screen map with bottom sheet / drawer containers on mobile and tablet.
- Configure client state management and remote data fetching:
  - TanStack Query (React Query) configured with sensible cache/stale times and retry policies.
  - Browser URL state management synchronization helper (`useUrlState`) for `?from=&to=&province=&category=&event=&lat=&lng=&zoom=`.
- Enforce accessibility baselines: visible keyboard focus states, WCAG AA color contrast, landmark HTML5 elements (`<header>`, `<main>`, `<aside>`, `<nav>`).

### MUST NOT
- Create separate mobile and desktop codebases or subdomains.
- Design desktop-only layouts and attempt to shrink them with ad-hoc media queries.
- Introduce hover-only critical interactions that cannot be triggered via touch on mobile.

## Architecture Constraints
- Conforms strictly to ADR-003: Responsive Web as Primary Client.
- Single web application bundle; zero native mobile client divergence for MVP.

## Implementation Requirements
- Initialize modern frontend build configuration with TypeScript strict mode enabled.
- CSS/Design System tokens:
  - Primary color palette tailored for geospatial visualization (neutral darks/lights, semantic alert colors for event categories: accident, fire, weather, etc.).
  - Fluid typography scale using system fonts or modern web fonts (Inter/Outfit).
- Layout components:
  - `ResponsiveShell.tsx`
  - `Header.tsx`
  - `MapContainer.tsx` (placeholder slot for Google Maps)
  - `FeedContainer.tsx` (collapsible side panel on desktop, bottom sheet on mobile)
  - `DetailDrawer.tsx` (slide-over on desktop, bottom sheet on mobile)

## Security Requirements
- Ensure HTML meta tags and Content Security Policy (CSP) headers are compatible with Google Maps and API endpoints.
- Sanitize any dynamic text rendering to prevent Cross-Site Scripting (XSS).

## Performance Requirements
- First Contentful Paint (FCP) < 1.2s on standard broadband / 4G.
- Initial bundle size (excluding external Maps API) < 200KB gzipped.

## Testing Requirements
- Unit and component tests:
  - Test responsive layout rendering across mobile (375px), tablet (768px), and desktop (1280px) viewport widths.
  - Test URL query parameter synchronization with state hook.
  - Test accessibility linting (axe-core or jest-axe) ensuring zero critical violations.

## Expected Files / Modules
- `frontend/src/App.tsx`
- `frontend/src/main.tsx`
- `frontend/src/styles/tokens.css` (or theme configuration)
- `frontend/src/components/layout/ResponsiveShell.tsx`
- `frontend/src/components/layout/Header.tsx`
- `frontend/src/components/layout/DetailDrawer.tsx`
- `frontend/src/hooks/useUrlState.ts`
- `frontend/src/lib/queryClient.ts`
- `tests/frontend/ResponsiveShell.test.tsx`

## Acceptance Criteria
- [ ] Application renders clean responsive layouts on 360px (mobile), 768px (tablet), and 1280px (desktop) without layout breaking or horizontal scrolling.
- [ ] URL state helper correctly reads and updates query string parameters for filters and coordinates.
- [ ] TanStack Query client is configured and available in React context.
- [ ] Automated component tests verify viewport behavior and accessibility standards.

## Completion Report
When completed, report:
1. Frontend application scaffolding.
2. Design system tokens and layout structure.
3. Responsive breakpoint validation.
4. Component test execution results.

## Follow-up Tasks
- TASK-035 (Google Maps Web Integration)
- TASK-037 (Event Quick Popup & Bottom Sheet)
- TASK-038 (Event Detail Panel)
- TASK-039 (Filter & Search UI)
- TASK-040 (Event Feed View & Map Sync)
- TASK-041 (Responsive Layout & Accessibility Polish)
