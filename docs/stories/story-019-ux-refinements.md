# Story 019: UX Refinements

**Epic:** [Epic 003: Canvas-Based Match Replay Viewer](../epic-003-canvas-replay-viewer.md)
**Status:** Not Started
**Size:** Small (~1-1.5 hours)
**Priority:** P2

---

## User Story

**As a** player
**I want** intuitive controls and good UX
**So that** watching replays is enjoyable and effortless

## Acceptance Criteria

- [ ] Match selector dropdown to choose replay
- [ ] Keyboard shortcuts (space = play/pause, arrow keys = scrub)
- [ ] Canvas scales responsively to window size
- [ ] Loading indicators during replay fetch
- [ ] Error messages are clear and helpful
- [ ] Tooltips for controls
- [ ] Mobile-friendly layout (bonus)

## Technical Approach

**Match Selector:**
```jsx
// Fetch list of available replays
const MatchSelector = ({ onSelectMatch }) => {
  const [matches, setMatches] = useState([]);

  useEffect(() => {
    fetch('/api/matches')
      .then(res => res.json())
      .then(data => setMatches(data))
      .catch(err => console.error(err));
  }, []);

  return (
    <select onChange={e => onSelectMatch(e.target.value)}>
      <option value="">Select a replay...</option>
      {matches.map(match => (
        <option key={match.match_id} value={match.match_id}>
          {match.model_a} vs {match.model_b} ({match.timestamp})
        </option>
      ))}
    </select>
  );
};
```

**Keyboard Shortcuts:**
```javascript
useEffect(() => {
  const handleKeyPress = (e) => {
    if (e.key === ' ') setPlaying(!playing);
    if (e.key === 'ArrowLeft') setCurrentTurn(Math.max(0, currentTurn - 1));
    if (e.key === 'ArrowRight') setCurrentTurn(Math.min(maxTurns - 1, currentTurn + 1));
  };

  window.addEventListener('keydown', handleKeyPress);
  return () => window.removeEventListener('keydown', handleKeyPress);
}, [playing, currentTurn, maxTurns]);
```

**Responsive Canvas:**
```jsx
const [canvasSize, setCanvasSize] = useState({ width: 1200, height: 800 });

useEffect(() => {
  const handleResize = () => {
    const containerWidth = containerRef.current.clientWidth;
    setCanvasSize({
      width: Math.min(containerWidth * 0.9, 1200),
      height: Math.min(containerWidth * 0.9 * (2/3), 800)
    });
  };

  window.addEventListener('resize', handleResize);
  handleResize();
  return () => window.removeEventListener('resize', handleResize);
}, []);
```

## Files to Create/Modify

- Create: `frontend/src/components/MatchSelector.jsx`
- Modify: `frontend/src/components/ReplayViewer.jsx` (keyboard shortcuts)
- Modify: `frontend/src/components/CanvasRenderer.jsx` (responsive sizing)
- Modify: `frontend/src/App.js` (integrate match selector)

## Dependencies

- **Requires:** All previous stories (this is the final polish)

## Notes

This is the final story - makes the viewer production-ready!
