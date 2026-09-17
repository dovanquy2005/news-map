# TASK-060 — Audio Player UI Component

## Status
TODO

## Priority
P2

## Phase
Phase 3 — TTS

## Depends On
- TASK-037
- TASK-038
- TASK-059

## Objective
Implement the responsive, accessible audio player component in the web application, allowing users to listen to Quick Briefs and Full Briefs directly within the Event Detail Panel and mobile preview sheets with playback controls, playback speed selector (1.0x, 1.25x, 1.5x), audio scrubber, and background playback support.

## Source of Truth
- `docs/08-ui-ux-responsive.md` (Touch targets, Responsive UX)
- `prd.md` (Section 27: TTS, Section 27.2: Quick Brief, Section 27.3: Full Brief)

## Scope

### MUST
- Implement responsive `AudioPlayer` component:
  - Toggle between `Bản tin nhanh` (Quick Brief 20-40s) and `Bản tin chi tiết` (Full Brief 1-2m).
  - Controls:
    - Play / Pause toggle button (minimum 48x48px touch target).
    - Progress scrubber bar / waveform display with current time and total duration.
    - Playback speed button: toggles between `1.0x`, `1.25x`, `1.5x`, `1.75x`.
    - Rewind 10s (`-10s`) / Skip 10s (`+10s`) buttons.
    - Mute / Volume slider.
  - Keyboard shortcuts: `Space` for play/pause, `Left`/`Right` arrow keys for 5s seeking.
- Integrate player into UI containers:
  - Inside `EventDetailPanel.tsx` right beneath the AI Summary section.
  - Compact audio play button on mobile `EventBottomSheet.tsx` allowing one-tap listening without expanding the full detail panel.
- Handle audio states gracefully:
  - `IDLE`, `LOADING` (audio buffering skeleton/spinner), `PLAYING`, `PAUSED`, `ERROR` (with retry button if audio fails to load).
- Audio Session & Media Session API integration:
  - Populate `navigator.mediaSession` with event title, category, and Vietnam News Map branding for native lock-screen and headphone controls on mobile.

### MUST NOT
- Auto-play audio unprompted (violates browser autoplay policies and degrades mobile UX).
- Require flash, external plugins, or proprietary codecs (standard HTML5 `<audio>` with MP3/AAC).
- Block the UI thread while loading or decoding audio.

## Architecture Constraints
- Conforms to ADR-003: Single responsive web application player adapting to desktop and mobile.
- Conforms to `docs/08-ui-ux-responsive.md`: Touch target minimum 48px; full keyboard accessibility.

## Implementation Requirements
- Create `frontend/src/components/audio/AudioPlayer.tsx` and `useAudioPlayback.ts`.
- Sub-components:
  - `PlayButton.tsx`
  - `ProgressBar.tsx`
  - `SpeedSelector.tsx`
  - `BriefTypeToggle.tsx`
- Media Session API hook: `frontend/src/hooks/useMediaSession.ts`.

## Security Requirements
- Audio source URL strictly bound to verified application streaming endpoints.
- Secure audio buffer disposal to prevent memory leaks during prolonged listening sessions.

## Performance Requirements
- Player UI response time < 50ms on play/pause click.
- Memory consumption < 15MB for active audio buffer.

## Testing Requirements
- Component and unit tests:
  - Clicking play initiates audio playback and updates play/pause icon state.
  - Speed toggle modifies `HTMLAudioElement.playbackRate`.
  - Scrubbing progress bar updates `HTMLAudioElement.currentTime`.
  - Media Session API is updated with event title and metadata.
  - Error state renders gracefully when audio stream endpoint returns 404 or network drops.
  - Responsive test: renders compact inline player on mobile bottom sheet.

## Expected Files / Modules
- `frontend/src/components/audio/AudioPlayer.tsx`
- `frontend/src/components/audio/PlayButton.tsx`
- `frontend/src/components/audio/ProgressBar.tsx`
- `frontend/src/components/audio/SpeedSelector.tsx`
- `frontend/src/hooks/useAudioPlayback.ts`
- `frontend/src/hooks/useMediaSession.ts`
- `frontend/src/styles/audio.css`
- `tests/frontend/AudioPlayer.test.tsx`

## Acceptance Criteria
- [ ] Audio player streams Quick Brief and Full Brief audio smoothly.
- [ ] Speed selector (1.0x to 1.75x) and 10s skip controls work accurately.
- [ ] Lock screen / headphone controls supported via Media Session API.
- [ ] Touch targets exceed 48x48px on mobile devices.
- [ ] Automated component tests verify playback states, scrubbing, and error recovery.

## Completion Report
When completed, report:
1. Audio player component design and styling.
2. Hook implementation and playback state machine.
3. Media Session API integration details.
4. Component test execution results across viewports.

## Follow-up Tasks
- TASK-061 (Area Audio Briefing Synthesizer)
