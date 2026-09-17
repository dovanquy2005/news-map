# TASK-061 — Area Audio Briefing Synthesizer

## Status
TODO

## Priority
P2

## Phase
Phase 3 — TTS

## Depends On
- TASK-058
- TASK-059
- TASK-060

## Objective
Implement the regional aggregate audio briefing synthesizer allowing users to generate and listen to a consolidated spoken digest of top news events in a specific Vietnamese province or city within a 24-hour window (e.g. "Bản tin 24 giờ qua tại TP. Hồ Chí Minh") as specified in `prd.md` Section 85 and Section 39.

## Source of Truth
- `docs/01-product-scope.md` (Phase 3: audio by area)
- `prd.md` (Section 85: audio brief theo khu vực, Section 39: F. Local audio briefing)

## Scope

### MUST
- Implement `AreaBriefingService`:
  - Input: `province` (e.g. `TP. Hồ Chí Minh`), `time_window_hours` (default: 24h), `max_events` (top 3 to 5 ranked by Trend Score / article count).
  - Queries top active events occurring within the target province in the past 24 hours.
  - Synthesizes composite spoken digest script:
    - Introduction: "Xin chào quý vị, đây là bản tin tổng hợp các sự kiện đáng chú ý tại [Tỉnh/Thành] trong 24 giờ qua trên Vietnam News Map."
    - Body: Sequential 20-second digest of each top event, highlighting incident type, location, and key confirmed facts.
    - Conclusion: "Vừa rồi là tóm tắt các sự kiện nổi bật tại [Tỉnh/Thành]. Cảm ơn quý vị đã theo dõi."
    - Target duration: 90 to 180 seconds.
- Implement background synthesis and caching:
  - Cache area briefing script and synthesized audio keyed by `(province, date_bucket)`.
  - Cache TTL: 3 hours.
- Expose API endpoint:
  - `GET /api/v1/areas/{province}/audio-brief`
  - Returns audio brief metadata (`audioUrl`, `durationSeconds`, `eventIdsCovered`, `generatedAt`).
- Frontend Area Briefing Trigger:
  - Add "Nghe tin khu vực 🎧" button in the province header and filter bar when a specific province is selected.
  - Launches audio player loaded with the regional briefing track.

### MUST NOT
- Synthesize area briefings synchronously inside the API request handler.
- Include low-confidence or unverified rumors in regional briefings without prominent disclaimers.
- Exceed 3 minutes total duration for regional digests.

## Architecture Constraints
- Conforms to `prd.md` Section 39: "Tin đáng chú ý quanh [Khu vực] trong 24 giờ qua".
- Builds upon the TTS provider and audio caching pipeline established in TASK-057 and TASK-059.

## Implementation Requirements
- Create `backend/app/modules/tts/area_briefing_service.py` and `workers/tts/area_briefing_worker.py`.
- Backend router: `backend/app/api/v1/areas/audio.py`.
- Frontend trigger component: `frontend/src/components/audio/AreaBriefingButton.tsx`.

## Security Requirements
- Province parameter validated against canonical list of 63 Vietnamese provinces to prevent injection.
- Rate limiting applied to area briefing generation requests (max 10 requests per hour per IP).

## Performance Requirements
- If audio is cached, endpoint response time < 50ms.
- Background synthesis completes in < 8s.

## Testing Requirements
- Unit and integration tests:
  - Generates composite script for TP.HCM containing 3 top events within duration constraints (100-250 words).
  - Missing events in province returns informative response ("Không có sự kiện đáng chú ý trong 24h qua").
  - Audio file is synthesized, uploaded to storage, and cached in Redis.
  - Repeat request retrieves cached audio without re-triggering TTS synthesis.
  - API endpoint returns valid audio metadata and HTTP 200.

## Expected Files / Modules
- `backend/app/modules/tts/area_briefing_service.py`
- `backend/app/modules/tts/schemas_area.py`
- `backend/app/api/v1/areas/audio.py`
- `workers/tts/area_briefing_worker.py`
- `frontend/src/components/audio/AreaBriefingButton.tsx`
- `tests/unit/test_area_briefing.py`
- `tests/api/test_area_audio_api.py`

## Acceptance Criteria
- [ ] Regional audio briefings synthesize top events per province into a cohesive spoken narrative.
- [ ] 3-hour caching prevents excessive TTS generation costs for identical regional queries.
- [ ] API endpoint returns streaming audio URL and list of covered event IDs.
- [ ] Frontend button in province view allows users to listen to regional summaries with one click.

## Completion Report
When completed, report:
1. Area briefing script composition logic.
2. Caching and scheduled pre-generation strategy.
3. API endpoint schema.
4. Test execution results for regional digests.

## Follow-up Tasks
- Project post-launch enhancements and monitoring.
