# TASK-039 — Filter & Search UI Component

## Status
TODO

## Priority
P0

## Phase
Phase 1 — Product

## Depends On
- TASK-008
- TASK-034

## Objective
Implement the responsive search and filter controls in the web application header/drawer, supporting keyword search with debouncing, time presets, province/municipality selector, category filter chips, and status filters, with full URL parameter synchronization.

## Source of Truth
- `docs/08-ui-ux-responsive.md` (Breakpoints, Performance: debounce search, State model)
- `prd.md` (Section 17: Filters & Search)

## Scope

### MUST
- Implement search input with debouncing (300ms) that queries `GET /api/v1/events/search?q=...` or filters the active view.
- Implement time preset selector matching `prd.md` Section 17.2:
  - `1 giờ qua` (Last 1 hour)
  - `6 giờ qua` (Last 6 hours)
  - `24 giờ qua` (Last 24 hours - default)
  - `3 ngày qua` (Last 3 days)
  - `7 ngày qua` (Last 7 days)
  - `30 ngày qua` (Last 30 days)
  - `Tùy chọn` (Custom date range modal)
- Implement Province / City dropdown selector:
  - Supports all 63 Vietnamese provinces/cities with search filtering inside dropdown.
  - Selecting a province automatically pans/zooms map camera to that province centroid.
- Implement Category filter chips:
  - Horizontal scrolling pill chips for categories (`Tất cả`, `Tai nạn`, `Cháy nổ`, `Thời tiết`, `Giao thông`, `An ninh`, v.v.).
  - Multi-select or single-select modes.
- Implement minimum source/article threshold filter:
  - Sliders or presets: `>= 1 nguồn`, `>= 3 nguồn`, `>= 5 nguồn`.
- Synchronize all active filter values with browser URL query string:
  - `?from=&to=&province=&category=&status=&minSources=`
- Responsive layout adaptation:
  - Desktop: Integrated into top header with compact dropdowns.
  - Mobile: Prominent compact search input in header; "Bộ lọc" (Filter) button opening a slide-up filter drawer with large touch targets.

### MUST NOT
- Trigger full-page reloads when changing filters or search terms.
- Fire instantaneous search API requests on every single keystroke without debouncing.
- Allow filter controls to permanently obscure essential map controls or navigation elements.

## Architecture Constraints
- Conforms to `docs/08-ui-ux-responsive.md`: Compact top search, filter drawer on mobile, URL-addressable state model.
- Filter state drives both Map View and Feed View synchronously.

## Implementation Requirements
- Create `frontend/src/components/filters/FilterBar.tsx` and `frontend/src/components/filters/FilterDrawer.tsx`.
- Create `SearchInput.tsx`, `TimePresetSelect.tsx`, `ProvinceSelect.tsx`, `CategoryChips.tsx`.
- Centralize filter state in a unified hook `useEventFilters.ts` reading and writing to URL query parameters.

## Security Requirements
- Search input sanitized against script injection; max length capped at 100 characters in UI.

## Performance Requirements
- Filter state update < 10ms.
- Debounced search triggers exactly 1 API call after typing stops.

## Testing Requirements
- Component and unit tests:
  - Selecting a time preset (e.g. "7 ngày qua") sets correct ISO timestamps in query state.
  - Typing "cháy" in search bar triggers debounced search callback after 300ms.
  - Selecting a province updates URL parameter `?province=TP.+Hồ+Chí+Minh`.
  - Mobile drawer toggle opens and closes filter drawer cleanly.
  - Reset filters button returns all controls to default state.

## Expected Files / Modules
- `frontend/src/components/filters/FilterBar.tsx`
- `frontend/src/components/filters/FilterDrawer.tsx`
- `frontend/src/components/filters/SearchInput.tsx`
- `frontend/src/components/filters/TimePresetSelect.tsx`
- `frontend/src/components/filters/ProvinceSelect.tsx`
- `frontend/src/components/filters/CategoryChips.tsx`
- `frontend/src/hooks/useEventFilters.ts`
- `tests/frontend/FilterBar.test.tsx`

## Acceptance Criteria
- [ ] Search input operates smoothly with 300ms debounce.
- [ ] All 7 time presets calculate and apply correct UTC time bounds.
- [ ] Province dropdown includes all 63 Vietnamese provinces and triggers map centering.
- [ ] Category chips allow rapid thematic filtering.
- [ ] Filter state synchronizes bidirectionally with URL query parameters.
- [ ] Responsive design provides desktop header bar and mobile bottom/side drawer.

## Completion Report
When completed, report:
1. Filter component breakdown and responsive adaptation.
2. Debounce and URL synchronization logic.
3. Time preset calculation methods.
4. Component test execution results.

## Follow-up Tasks
- TASK-040 (Event Feed View & Map Synchronization)
- TASK-041 (Responsive Layout & Accessibility Polish)
