# TASK-058 — Summary-to-Script Generation Worker (Quick Brief & Full Brief)

## Status
TODO

## Priority
P2

## Phase
Phase 3 — TTS

## Depends On
- TASK-029
- TASK-030
- TASK-057

## Objective
Implement the background transformation pipeline that converts structured event facts, summaries, and timelines into spoken narrative scripts for two distinct audio formats: Quick Brief (20–40 seconds) and Full Brief (1–2 minutes), ensuring natural spoken cadence, source attribution, and uncertainty disclaimers.

## Source of Truth
- `prd.md` (Section 27.1: Input, Section 27.2: Quick Brief, Section 27.3: Full Brief)

## Scope

### MUST
- Implement `ScriptGeneratorService` producing two audio script formats:
  - Format 1 — Quick Brief (20–40s target / approx 50–90 spoken words):
    - Opening: "Bản tin nhanh từ Vietnam News Map..."
    - Core facts: What happened, where, when.
    - Verification summary: Number of independent reporting sources.
    - Uncertainty note: Explicit disclaimer if facts conflict or remain developing.
    - Closing: "Thông tin chi tiết mời quý vị xem trên bản đồ tin tức."
  - Format 2 — Full Brief (60–120s target / approx 150–280 spoken words):
    - Comprehensive narrative: Detailed event summary.
    - Chronological progression: Timeline of reporting and developments.
    - Source diversity: Distinction between official statements and eyewitness reports.
    - Fact breakdown: Specific agreements and noted conflicting numbers.
- Convert raw dates and numbers into natural spoken Vietnamese text:
  - Numbers: "15 người" -> "mười lăm người", "2.5 tỷ" -> "hai phẩy năm tỷ đồng".
  - Dates: "18/09 lúc 14:30" -> "ngày mười tám tháng chín, lúc mười bốn giờ ba mươi phút".
- Implement `ScriptGenerationWorker`:
  - Consumes `GenerateAudioScriptJob` triggered after event summary generation or on-demand user request.
  - Generates scripts, formats with SSML markup, and enqueues `SynthesizeAudioJob` into `tts_queue`.

### MUST NOT
- Generate scripts directly by reading raw article HTML or verbatim copyrighted text.
- Omit uncertainty warnings when event facts are marked as conflicting.
- Exceed 120 seconds duration for individual event audio briefs.

## Architecture Constraints
- Conforms to `prd.md` Section 27.1: `Event -> Verified/normalized summary -> TTS script -> Audio`.
- Pure text-to-script transformation running asynchronously before audio synthesis.

## Implementation Requirements
- Create `workers/tts/script_worker.py` and `backend/app/modules/tts/script_generator.py`.
- Vietnamese number-to-words utility (`backend/app/common/utils/vietnamese_speech.py`).
- Output schema: `EventAudioScriptDTO`:
  - `event_id`: UUID
  - `script_type`: `QUICK_BRIEF` | `FULL_BRIEF`
  - `plain_text`: str
  - `ssml_text`: str
  - `estimated_duration_seconds`: int
  - `content_version_hash`: str

## Security Requirements
- Input sanitization ensuring factual inputs cannot inject SSML commands or alter script disclaimers.

## Performance Requirements
- Script generation execution < 500ms per event.

## Testing Requirements
- Unit tests:
  - Quick Brief script generated from sample event meets length constraints (50-90 words).
  - Full Brief includes timeline milestones and source diversity details.
  - Conflicting fact in event (e.g. diverging casualty numbers) forces uncertainty disclaimer into spoken script.
  - Number-to-words converter converts "14:30 ngày 18/09" into natural Vietnamese speech string.

## Expected Files / Modules
- `workers/tts/script_worker.py`
- `backend/app/modules/tts/script_generator.py`
- `backend/app/modules/tts/schemas_script.py`
- `backend/app/common/utils/vietnamese_speech.py`
- `tests/unit/test_audio_script_generator.py`

## Acceptance Criteria
- [ ] Script generator produces natural Vietnamese spoken scripts for Quick Brief (20–40s) and Full Brief (1–2m).
- [ ] Number-to-words and date expansions produce phonetically correct Vietnamese text.
- [ ] Uncertainty disclaimers are automatically included for unverified or conflicting events.
- [ ] Unit tests pass for word count, spoken phrasing, and disclaimer preservation.

## Completion Report
When completed, report:
1. Quick Brief and Full Brief script templates.
2. Vietnamese phonetics and number-to-words helper implementation.
3. Disclaimer insertion logic.
4. Test execution results for sample events.

## Follow-up Tasks
- TASK-059 (Audio Synthesis, Storage & Caching Pipeline)
- TASK-060 (Audio Player UI Component)
