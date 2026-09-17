# TASK-059 — Audio Synthesis, Storage & Caching Pipeline

## Status
TODO

## Priority
P2

## Phase
Phase 3 — TTS

## Depends On
- TASK-005
- TASK-007
- TASK-057
- TASK-058

## Objective
Implement the asynchronous audio synthesis pipeline, object storage persistence (S3 / Cloud Storage / MinIO), content-hash caching, audio stream serving endpoint (`GET /api/v1/events/{eventId}/audio`), and cache invalidation when event summaries change materially.

## Source of Truth
- `docs/01-product-scope.md` (Phase 3: cached audio)
- `docs/02-system-architecture.md` (Object Storage - optional)
- `prd.md` (Section 27.4: Audio caching)

## Scope

### MUST
- Implement `AudioSynthesisWorker` consuming `SynthesizeAudioJob` from `tts_queue`:
  1. Receives `event_id`, `script_type` (`QUICK_BRIEF` | `FULL_BRIEF`), `ssml_text`, `content_version_hash`.
  2. Checks if valid cached audio file exists in object storage / cache matching `content_version_hash`:
     - If exists: skip re-synthesis and return existing audio URL.
  3. Calls `BaseTTSProvider` to synthesize MP3 audio stream.
  4. Uploads audio file to object storage (or local media directory in dev):
     - Path: `audio/events/{event_id}/{script_type}_{content_version_hash}.mp3`
     - Metadata: Content-Type `audio/mpeg`, Cache-Control `public, max-age=31536000, immutable`.
  5. Records audio metadata in `event_audio_briefs` table:
     - `id`, `event_id`, `brief_type`, `audio_url`, `duration_seconds`, `file_size_bytes`, `content_hash`, `created_at`.
- Implement public streaming audio endpoint:
  - `GET /api/v1/events/{eventId}/audio?type=QUICK_BRIEF`
  - Returns audio stream directly with HTTP 206 Partial Content (byte-range requests for audio seeking) or redirects to CDN/object storage signed URL.
- Implement Cache Invalidation:
  - When an event summary is materially regenerated (new facts added, version hash changes), mark previous audio brief as superseded and enqueue background synthesis of new audio version.

### MUST NOT
- Synthesize audio on-the-fly inside the user-facing HTTP request (audio synthesis is strictly asynchronous and cached).
- Serve audio files without `Range` header support (byte-range streaming is required for mobile audio scrubbing).
- Retain orphaned audio files indefinitely without lifecycle retention policy.

## Architecture Constraints
- Conforms strictly to `prd.md` Section 27.4: Never generate TTS on every listen; cache once, stream to thousands of users.
- Storage abstraction supports local filesystem for local dev and S3-compatible object storage for staging/production.

## Implementation Requirements
- Create `workers/tts/audio_worker.py` and `backend/app/modules/tts/storage.py`.
- Create `backend/app/api/v1/events/audio.py`.
- Migration adding `event_audio_briefs` table with composite index on `(event_id, brief_type, created_at DESC)`.
- Implement HTTP Byte-Range response streamer for local files / dev environment.

## Security Requirements
- Audio files cannot be overwritten via client input (immutable hash naming).
- Object storage bucket configured with read-only public access for audio assets; private access for operational buckets.

## Performance Requirements
- Public audio stream endpoint TTFB < 50ms (served from CDN/cache or local storage).
- Audio streaming bandwidth consumption < 1MB per minute of speech.

## Testing Requirements
- Integration and API tests:
  - Worker consumes audio job, calls mock TTS provider, and uploads MP3 file to storage mock.
  - Re-running job with identical `content_version_hash` skips TTS provider call and reuses existing file.
  - Endpoint `GET /api/v1/events/{eventId}/audio` returns HTTP 200/206 with `Content-Type: audio/mpeg` and `Accept-Ranges: bytes`.
  - Range request test (`Range: bytes=0-1023`) returns HTTP 206 Partial Content with correct `Content-Range` header.

## Expected Files / Modules
- `workers/tts/audio_worker.py`
- `backend/app/modules/tts/storage.py`
- `backend/app/modules/tts/models/audio_brief.py`
- `backend/app/api/v1/events/audio.py`
- `tests/integration/test_audio_pipeline.py`
- `tests/api/test_audio_streaming_api.py`

## Acceptance Criteria
- [ ] Audio synthesis worker runs asynchronously and uploads MP3 files with immutable content hashes.
- [ ] Audio caching strictly prevents re-synthesizing unchanged event summaries.
- [ ] Streaming API endpoint supports HTTP 206 byte-range seeking on desktop and mobile.
- [ ] Material summary updates trigger background audio regeneration.

## Completion Report
When completed, report:
1. Audio worker and storage abstraction implementation.
2. Content-hash caching and invalidation flow.
3. Byte-range streaming verification.
4. Test execution results for audio synthesis and streaming.

## Follow-up Tasks
- TASK-060 (Audio Player UI Component)
- TASK-061 (Area Audio Briefing Synthesizer)
