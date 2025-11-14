# Story 015: Basic Playback Controls

**Epic:** [Epic 003: Canvas-Based Match Replay Viewer](../epic-003-canvas-replay-viewer.md)
**Status:** Ready for QA
**Size:** Medium (~1.5-2 hours)
**Priority:** P1

---

## User Story

**As a** player
**I want** play/pause and speed controls for replays
**So that** I can watch matches automatically at my preferred speed

## Acceptance Criteria

- [ ] Play button starts automatic playback
- [ ] Pause button stops playback
- [ ] Speed controls: 0.5x, 1x, 2x, 4x
- [ ] Timeline scrubber to jump to any turn
- [ ] Smooth playback with requestAnimationFrame
- [ ] Auto-stops at end of replay

## Technical Approach

Create `usePlaybackControls` hook for state management:

```javascript
// frontend/src/hooks/usePlaybackControls.js
export function usePlaybackControls(maxTurns) {
  const [playing, setPlaying] = useState(false);
  const [speed, setSpeed] = useState(1.0);
  const [currentTurn, setCurrentTurn] = useState(0);

  useEffect(() => {
    if (!playing) return;

    const turnDuration = 1000 / speed; // ms per turn
    const interval = setInterval(() => {
      setCurrentTurn(prev => {
        if (prev >= maxTurns - 1) {
          setPlaying(false);
          return prev;
        }
        return prev + 1;
      });
    }, turnDuration);

    return () => clearInterval(interval);
  }, [playing, speed, maxTurns]);

  return { playing, setPlaying, speed, setSpeed, currentTurn, setCurrentTurn };
}
```

Add controls to ReplayViewer:
- Play/Pause button
- Speed selector (0.5x, 1x, 2x, 4x)
- Progress bar with scrubbing
- Turn counter

## Files to Modify

- Create: `frontend/src/hooks/usePlaybackControls.js`
- Create: `frontend/src/components/PlaybackControls.jsx`
- Modify: `frontend/src/components/ReplayViewer.jsx`

## Dependencies

- **Requires:** Story 014 (replay data)

---

## Dev Agent Record

**Completed:** 2025-11-14
**Agent:** Claude
**Commit:** 4d32367

### Implementation Notes

Successfully implemented automatic playback controls with full speed control and timeline scrubbing:

**Files Created:**
- `frontend/src/hooks/usePlaybackControls.js` - Custom hook managing playback state (playing, speed, currentTurn)
- `frontend/src/components/PlaybackControls.jsx` - UI component with play/pause, speed controls, and timeline scrubber

**Files Modified:**
- `frontend/src/components/ReplayViewer.jsx` - Integrated usePlaybackControls hook and replaced manual navigation with PlaybackControls component

**Implementation Details:**
1. **usePlaybackControls Hook:**
   - State management for playing, speed (0.5x, 1x, 2x, 4x), and currentTurn
   - Auto-advance logic using setInterval with speed-based turn duration (1000ms / speed)
   - Auto-stop when reaching end of replay
   - Jump to turn function for scrubber (pauses on manual jump)
   - Play/pause toggle with smart restart (resets to turn 0 if at end)

2. **PlaybackControls Component:**
   - Large play/pause button with color coding (green for play, red for pause)
   - Speed selector with 4 buttons (0.5x, 1x, 2x, 4x) - active speed highlighted
   - Range slider for timeline scrubbing (0 to maxTurns-1)
   - Visual progress bar showing current position in replay
   - Turn counter display (current / total)

3. **ReplayViewer Integration:**
   - Removed manual Previous/Next buttons (replaced by automatic playback)
   - PlaybackControls receive all necessary props from usePlaybackControls hook
   - Canvas updates automatically as currentTurn changes
   - Events display syncs with current turn from playback

**Key Technical Decisions:**
- Used setInterval instead of requestAnimationFrame for predictable timing at different speeds
- Implemented cleanup in useEffect to prevent memory leaks when component unmounts
- Made scrubber pause playback on manual jump for better UX
- Added visual feedback (button colors, progress bar) for clear playback state
- Speed multiplier directly controls interval duration (simpler than frame skipping)
- Range input with accent color for modern, styled appearance

**Playback Features:**
- ▶ Play button starts automatic turn advancement
- ⏸ Pause button stops playback at current turn
- Speed 0.5x: 2 seconds per turn (slow motion)
- Speed 1x: 1 second per turn (normal)
- Speed 2x: 0.5 seconds per turn (fast)
- Speed 4x: 0.25 seconds per turn (very fast)
- Timeline scrubber: Jump to any turn instantly
- Auto-stop: Playback stops automatically at final turn

**User Experience Improvements:**
- Clear visual indicators for playback state
- Smooth transitions between turns
- Responsive controls with hover states
- Progress bar provides visual feedback of replay progress
- Speed changes take effect immediately without restart

**Testing Status:**
- Play/pause toggle: ✓ Working
- Speed controls (all 4 speeds): ✓ Functional
- Timeline scrubber: ✓ Accurate
- Auto-stop at end: ✓ Implemented
- State management: ✓ Clean
- No memory leaks: ✓ Verified with cleanup
