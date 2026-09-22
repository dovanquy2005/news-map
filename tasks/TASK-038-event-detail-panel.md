# TASK-038 — Event Detail Panel Component

## Status
DONE

## Priority
P0

## Phase
Phase 1 — Product

## Depends On
- TASK-008
- TASK-033
- TASK-037

## Objective
Implement the comprehensive Event Detail Panel component (slide-over drawer on desktop/tablet, full-screen overlay on mobile) that lazy-loads full event data via `GET /api/v1/events/{eventId}` and renders the 6 core sections defined in `prd.md` Section 16: Header, AI Summary with uncertainty warnings, Verification & Confidence breakdown, Chronological Timeline, Source List with direct article links, and Related Events.

## Source of Truth
- `docs/08-ui-ux-responsive.md` (Desktop right drawer, Mobile full viewport, Lazy load)
- `docs/18-legal-content.md` (Always attribute original source, direct access)
- `prd.md` (Section 12: Source & Verification View, Section 13: Timeline, Section 16: Event Detail Panel)

## Scope

### MUST
- Implement responsive container:
  - Desktop / Tablet: Slide-over right drawer (width: 440px to 520px) overlaying the event feed while keeping map visible.
  - Mobile: Full-screen modal overlay with sticky header, back/close button, and vertical scroll.
- Lazy-load full event detail using TanStack Query hook (`useEventDetail(eventId)`).
- Implement Section A — Header:
  - Event title, category pill, resolved location, status tag, occurred timestamp and last update in Vietnam Time (UTC+7).
- Implement Section B — AI Summary:
  - AI-generated summary paragraph.
  - Prominent alert/callout box if there are conflicting facts or unresolved uncertainties.
- Implement Section C — Verification & Confidence:
  - Total article count, independent source count, location confidence score.
  - Interactive confidence card displaying the score breakdown and positive/warning factor explanations.
- Implement Section D — Timeline:
  - Vertical timeline component with distinct icons for `OCCURRED`, `FIRST_REPORTED`, and `SOURCE_UPDATE` milestones.
- Implement Section E — Sources:
  - List of all reporting news sources with publisher logo/name, published time, and external link button ("Đọc bài gốc ↗") opening the canonical article URL in a new tab (`target="_blank" rel="noopener noreferrer"`).
- Implement Section F — Related Events:
  - Cards for nearby or related events allowing user to navigate directly to contextually similar incidents.

### MUST NOT
- Load the heavy event detail payload upfront when user merely browses the map or feed (lazy loading is mandatory).
- Hide or obscure original source links; source transparency and external article attribution are non-negotiable.
- Allow unescaped publisher content or summary text to execute arbitrary scripts.

## Architecture Constraints
- Conforms to `docs/08-ui-ux-responsive.md`: Drawer on desktop/tablet, full-screen on mobile; lazy loads detail data.
- Conforms to `docs/18-legal-content.md`: Always attribute the original source with direct links.

## Implementation Requirements
- Create `frontend/src/components/events/EventDetailPanel.tsx` and sub-components:
  - `DetailHeader.tsx`
  - `SummarySection.tsx`
  - `ConfidenceCard.tsx`
  - `TimelineView.tsx`
  - `SourceListView.tsx`
  - `RelatedEventsView.tsx`
- Ensure smooth CSS transitions (`transform: translateX` on desktop, `translateY` on mobile).
- Handle loading skeletons and error states (e.g. event not found or network failure).

## Security Requirements
- External links must include `rel="noopener noreferrer"` to prevent window.opener hijacking.
- All dynamic strings sanitized against XSS.

## Performance Requirements
- Panel opens immediately (< 100ms) with skeleton state while data loads in background.
- Detail data cached in TanStack Query for 5 minutes to prevent redundant network fetches on repeated clicks.

## Testing Requirements
- Component and integration tests:
  - Panel renders skeleton while loading and displays all 6 sections upon query resolution.
  - Verifies source links contain `href`, `target="_blank"`, and `rel="noopener noreferrer"`.
  - Verifies timeline entries are rendered in order.
  - Verifies mobile layout adopts full-screen presentation.
  - Clicking close button or pressing Escape triggers onClose callback and updates URL.

## Expected Files / Modules
- `frontend/src/components/events/EventDetailPanel.tsx`
- `frontend/src/components/events/detail/DetailHeader.tsx`
- `frontend/src/components/events/detail/SummarySection.tsx`
- `frontend/src/components/events/detail/ConfidenceCard.tsx`
- `frontend/src/components/events/detail/TimelineView.tsx`
- `frontend/src/components/events/detail/SourceListView.tsx`
- `frontend/src/components/events/detail/RelatedEventsView.tsx`
- `frontend/src/hooks/useEventDetail.ts`
- `tests/frontend/EventDetailPanel.test.tsx`

## Acceptance Criteria
- [ ] Panel renders all 6 required sections with clean, modern styling.
- [ ] Lazy-loading executes only when panel is activated.
- [ ] Direct links to original publisher articles are prominent and securely formatted.
- [ ] Confidence explanation card accurately renders positive and warning indicators.
- [ ] Responsive behavior adapts seamlessly between desktop drawer and mobile full-screen view.

## Completion Report
When completed, report:
1. Event detail panel component architecture.
2. Section breakdown and visual design implementation.
3. Lazy-loading query hook and caching strategy.
4. Test execution results across responsive viewports.

## Follow-up Tasks
- TASK-039 (Filter & Search UI Component)
- TASK-040 (Event Feed View & Map Synchronization)
- TASK-041 (Responsive Layout & Accessibility Polish)
- TASK-060 (Phase 3 TTS Audio Player UI Component)
