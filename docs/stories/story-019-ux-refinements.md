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

---

## Dev Agent Record

**Completed:** [Date to be filled by Dev Agent]
**Agent:** Claude (Dev Agent)
**Commit:** [Commit hash to be filled by Dev Agent]

### Implementation Notes

[Dev Agent: Please document your implementation here. Include:]
- Files created and their purposes
- Files modified and what changed
- Key technical decisions and rationale
- Implementation approach for match selector, keyboard shortcuts, and responsive canvas
- Loading indicators and error handling implementation
- Testing results and validation performed
- Any challenges encountered and how you resolved them
- Update the YAML status to "Ready for QA" when complete

---

## QA Agent Record

**Reviewed:** [Date to be filled by QA Agent]
**QA Agent:** Claude (QA Agent)
**Branch:** claude/plan-next-sprint-01HUc1o8niUYfixdx8uZrDxw
**Result:** [✅ PASS / ❌ FAIL / 🔄 REMEDIATION NEEDED - to be filled by QA Agent]

### Automated Testing Results

[QA Agent: Document your test execution here:]
- Test environment and setup
- Automated test results
- Match selector functionality testing
- Keyboard shortcuts verification (space, arrows)
- Responsive canvas sizing tests
- Loading indicators validation
- Error message testing
- Tooltip functionality

### Acceptance Criteria Validation

[QA Agent: Check each criterion:]
- [ ] Match selector dropdown to choose replay
- [ ] Keyboard shortcuts (space = play/pause, arrow keys = scrub)
- [ ] Canvas scales responsively to window size
- [ ] Loading indicators during replay fetch
- [ ] Error messages are clear and helpful
- [ ] Tooltips for controls
- [ ] Mobile-friendly layout (bonus)

### Issues Found

**Critical Issues:**
[List any blocking issues]

**Minor Issues:**
[List any non-blocking issues]

**Recommendations:**
[Suggestions for future improvements]

### Final Assessment

[QA Agent: Provide final verdict here]

**Update YAML status based on results:**
- ✅ PASS → Status: "Completed"
- ❌ FAIL → Status: "Remediation needed"
- 🔄 REMEDIATION NEEDED → Status: "Remediation needed"
