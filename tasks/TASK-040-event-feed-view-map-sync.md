# TASK-040 — Event Feed View & Map Synchronization

## Status
DONE

## Priority
P0

## Phase
Phase 1 — Product

## Depends On
- TASK-008
- TASK-032
- TASK-036
- TASK-037
- TASK-039

## Objective
Implement the virtualized Event Feed list view (desktop right panel, tablet collapsible sidebar, mobile toggleable bottom sheet/tab), displaying chronological event cards synchronized bidirectionally with map markers, active filters, and event selection.

## Source of Truth
- `docs/08-ui-ux-responsive.md` (Desktop split layout, Tablet collapsible, Mobile bottom sheet, Virtualize long feed lists)
- `adr/003-responsive-web-first.md` (Desktop split map/feed layout)
- `prd.md` (Section 18: Feed View)

## Scope

### MUST
- Implement `EventFeedView` displaying a list of event cards matching current viewport/filter events:
  - Event Card contents:
    - Event category badge and status indicator.
    - Title (clear 2-line truncation).
    - Location name (with approximate tag if applicable).
    - Metrics: Source count and article count (e.g. `12 bài · 7 nguồn`).
    - Relative timestamp (e.g. `15 phút trước`, `18/09 15:58`).
    - Confidence badge.
  - Sorting options:
    - `Mới nhất` (Newest first - default).
    - `Nhiều nguồn nhất` (Most sources first).
    - `Nhiều bài nhất` (Most articles first).
- Implement bidirectional synchronization between Map and Feed:
  - Hovering/focusing a card in the feed highlights the corresponding marker on the map.
  - Clicking a card in the feed centers the map on that event's coordinates and opens the quick preview / detail panel.
  - Clicking a marker on the map automatically scrolls the feed list to bring the corresponding card into view and highlights it.
  - Updating filters or panning map view updates the feed list accordingly.
- Implement list virtualization (using `@tanstack/react-virtual` or equivalent) to ensure high rendering performance with hundreds of loaded events.
- Responsive layout presentation:
  - Desktop (>= 1024px): Persistent right-hand feed panel alongside map (split view).
  - Tablet (768–1023px): Collapsible side drawer toggled via feed button.
  - Mobile (360–767px): Mobile tab toggle (`[ Bản đồ ]` vs `[ Danh sách ]`) or swipe-up bottom sheet.

### MUST NOT
- Render unvirtualized DOM nodes for hundreds of event cards (causes scrolling jank and memory bloat).
- Decouple feed filters from map filters (they must always display the same query results).
- Break on mobile by forcing desktop side-by-side columns.

## Architecture Constraints
- Conforms to ADR-003: Desktop split map/feed layout; mobile tab/bottom sheet.
- Virtualization required by `docs/08-ui-ux-responsive.md` Section 7.

## Implementation Requirements
- Create `frontend/src/components/feed/EventFeedView.tsx` and `EventCard.tsx`.
- Implement virtual list windowing with `@tanstack/react-virtual`.
- Maintain active selected event ID state shared across map markers and feed list.
- Implement auto-scroll to card when marker is clicked using `virtualizer.scrollToIndex()`.

## Security Requirements
- Safe string truncation without splitting multi-byte UTF-8 Vietnamese characters.
- Output sanitization preventing script injection in feed cards.

## Performance Requirements
- 60 FPS smooth scrolling in feed list with 500+ items rendered via virtualizer.
- Feed card click response time < 50ms.

## Testing Requirements
- Component and integration tests:
  - Virtualizer renders only visible items in the DOM viewport.
  - Clicking an event card invokes map center and event selection callbacks.
  - Marker selection triggers scroll-to-index in the virtual list.
  - Switching sort orders (Newest vs Most Sources) re-sorts the displayed items correctly.
  - Responsive layout test: switches from side panel on desktop to toggle tab on mobile.

## Expected Files / Modules
- `frontend/src/components/feed/EventFeedView.tsx`
- `frontend/src/components/feed/EventCard.tsx`
- `frontend/src/components/feed/FeedSortSelect.tsx`
- `frontend/src/styles/feed.css`
- `tests/frontend/EventFeedView.test.tsx`

## Acceptance Criteria
- [ ] Feed displays event cards with all required metadata fields.
- [ ] Bidirectional map-feed synchronization highlights and centers events seamlessly.
- [ ] Virtualization maintains smooth scrolling regardless of total event count.
- [ ] Responsive behavior conforms to desktop split, tablet collapsible, and mobile tab modes.

## Completion Report
When completed, report:
1. Feed view architecture and virtualization implementation.
2. Bidirectional map synchronization flow.
3. Sorting algorithms and options.
4. Component test execution results.

## Follow-up Tasks
- TASK-041 (Responsive Web Layout & Accessibility Polish)
- TASK-056 (Phase 2 Trend & Hotspot UI Extension)
