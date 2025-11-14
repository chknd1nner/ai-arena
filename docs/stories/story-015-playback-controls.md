# Story 015: Basic Playback Controls

**Epic:** [Epic 003: Canvas-Based Match Replay Viewer](../epic-003-canvas-replay-viewer.md)
**Status:** Not Started
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
