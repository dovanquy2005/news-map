# TASK-057 — TTS Provider Abstraction & Vietnamese Voice Adapter

## Status
TODO

## Priority
P2

## Phase
Phase 3 — TTS

## Depends On
- TASK-002
- TASK-006
- TASK-010
- TASK-050

## Objective
Implement the Text-to-Speech (TTS) provider abstraction layer and provider adapters (e.g. Google Cloud Text-to-Speech / OpenAI Audio / Edge TTS / local model) specialized for natural, high-quality Vietnamese voice synthesis with configurable speed, pitch, and voice gender (Northern / Southern dialects).

## Source of Truth
- `docs/01-product-scope.md` (Phase 3: TTS Quick Brief, Full Brief)
- `docs/18-legal-content.md` (Future TTS: original event summary/brief, not copyrighted articles)
- `prd.md` (Section 27: TTS — Phase 3 Only, Section 27.1: Input)

## Scope

### MUST
- Implement `BaseTTSProvider` interface with methods:
  - `async synthesize(ssml_or_text: str, voice_config: VoiceConfig) -> TTSAudioResultDTO`
  - `async list_available_voices() -> list[VoiceDescriptor]`
- Implement provider adapters:
  - Primary Provider: Google Cloud Text-to-Speech API (`vi-VN-Neural2-A`, `vi-VN-Neural2-D`, `vi-VN-Wavenet-*`) or equivalent high-fidelity neural voice provider.
  - Secondary/Fallback Provider: Local or lightweight API provider for cost management during testing.
- Support voice configuration options:
  - Language code: `vi-VN`.
  - Dialect: Northern (`vi-VN-Neural2-A` female, `vi-VN-Neural2-B` male) / Southern (`vi-VN-Neural2-C` male, `vi-VN-Neural2-D` female).
  - Speaking rate: 0.8x to 1.5x (default: 1.0x).
  - Pitch: -2.0 to +2.0 semitones.
  - Audio encoding: MP3 / OGG Opus at 64kbps to 128kbps (optimized for fast mobile streaming).
- Implement bounded request timeouts (<= 10s) and retry policies for transient network failures.

### MUST NOT
- Synthesize full third-party copyrighted article text directly (TTS is strictly restricted to the product's original summaries and scripts).
- Make unthrottled external TTS calls (TTS audio must be generated asynchronously and cached).
- Hardcode provider-specific SDK logic into application domain code.

## Architecture Constraints
- Conforms to `docs/18-legal-content.md` Section 36: TTS should read the product's original event summary/brief, not copyrighted articles.
- Modular provider pattern allowing seamless swapping of underlying speech synthesis vendors.

## Implementation Requirements
- Create `backend/app/modules/tts/providers/base.py`, `google_tts.py`, `service.py`.
- Configure provider credentials via `TTS_API_KEY` / Google Application Credentials.
- Implement SSML builder helper supporting pauses (`<break time="500ms"/>`), prosody, and phonetic corrections for Vietnamese acronyms/numbers (e.g. "TP.HCM" pronounced as "Thành phố Hồ Chí Minh", "18/09" as "ngày 18 tháng 9").

## Security Requirements
- All text passed to SSML builder sanitized to prevent SSML injection attacks.
- Provider API keys stored in environment and redacted from all logs.

## Performance Requirements
- Audio generation for a 30-second script completes in < 3s.
- Synthesized MP3 payload compressed to < 500KB per 30-second audio clip.

## Testing Requirements
- Unit tests:
  - SSML builder expands Vietnamese acronyms ("TP.HCM" -> "Thành phố Hồ Chí Minh", "QL1A" -> "Quốc lộ một A").
  - SSML sanitizer escapes special XML characters (`&`, `<`, `>`, `"`) preventing SSML injection.
  - Mock TTS adapter returns audio byte stream with valid MP3 headers.
  - Provider failure triggers fallback or returns informative domain error.

## Expected Files / Modules
- `backend/app/modules/tts/providers/base.py`
- `backend/app/modules/tts/providers/google_tts.py`
- `backend/app/modules/tts/service.py`
- `backend/app/modules/tts/ssml_builder.py`
- `tests/unit/test_tts_provider.py`
- `tests/unit/test_ssml_builder.py`

## Acceptance Criteria
- [ ] TTS provider abstraction supports pluggable backends with Vietnamese neural voices.
- [ ] SSML builder handles Vietnamese acronyms, dates, and pause insertions naturally.
- [ ] SSML injection defense prevents malicious markup execution.
- [ ] Unit tests pass for SSML formatting and audio byte stream generation.

## Completion Report
When completed, report:
1. TTS provider architecture and supported voice profiles (Northern/Southern).
2. SSML builder acronym expansion dictionary.
3. SSML injection defense validation.
4. Test execution results.

## Follow-up Tasks
- TASK-058 (Summary-to-Script Generation Worker)
- TASK-059 (Audio Synthesis, Storage & Caching Pipeline)
