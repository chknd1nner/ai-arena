# Story 019: UX Refinements

**Epic:** [Epic 003: Canvas-Based Match Replay Viewer](../epic-003-canvas-replay-viewer.md)
**Status:** Ready for QA
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

**Completed:** 2025-11-15
**Agent:** Claude (Dev Agent)
**Commit:** [To be added after commit]

### Implementation Notes

**Files Created:**
- `frontend/src/components/MatchSelector.jsx` - Match selector dropdown component
  - Fetches available matches from `/api/matches`
  - Displays matches with model names, winner, turns, and timestamp
  - Includes loading state, error handling, and retry functionality
  - Auto-fetches matches on component mount

**Files Modified:**
- `frontend/src/components/ReplayViewer.jsx`
  - **Keyboard Shortcuts:** Added global keydown listener with support for:
    - `Space` = Play/Pause (with preventDefault to avoid page scroll)
    - `←` / `→` = Previous/Next Turn
    - `Home` / `End` = Jump to First/Last Turn
    - Ignores shortcuts when typing in input fields
  - **Enhanced Loading State:** Added spinning loader with CSS animation
  - **Enhanced Error State:** Added warning icon, styled error box with border
  - **Enhanced Empty State:** Added folder icon and helpful message
  - **Keyboard Shortcuts Help:** Added visible help text showing available shortcuts

- `frontend/src/components/CanvasRenderer.jsx`
  - **Responsive Canvas:** Added `containerRef` and resize event listener
  - Calculate dimensions based on container width (95% max, maintaining aspect ratio)
  - Regenerate starfield when dimensions change
  - Initial sizing on mount

- `frontend/src/components/PlaybackControls.jsx`
  - **Tooltips:** Added `title` attributes to all interactive controls:
    - Play/Pause button: "Pause replay (Space)" / "Play replay (Space)"
    - Speed buttons: "Set playback speed to Nx"
    - Timeline slider: "Scrub through replay timeline (← → arrow keys)"

- `frontend/src/App.js`
  - **Integrated MatchSelector:** Added MatchSelector component above test replays
  - Updated section heading to "Or Load Test Replays" for clarity

**Key Technical Decisions:**
1. **Keyboard Event Handling:** Check `e.target.tagName` to prevent shortcuts when typing in inputs
2. **Responsive Sizing:** Use 95% of container width (capped at original size) to prevent overflow
3. **Loading Indicator:** CSS-only spinner using border animation for lightweight implementation
4. **Error Handling:** Retry button in MatchSelector for better UX
5. **Aspect Ratio:** Maintain original aspect ratio when resizing canvas
6. **Tooltip Placement:** Use native browser `title` attribute for simplicity and accessibility

**Implementation Approach:**

1. **Match Selector:**
   - Fetches matches on mount using `useEffect`
   - Displays formatted match info (models, winner, turns, timestamp)
   - Handles empty state, loading, and errors gracefully
   - Retry button on error

2. **Keyboard Shortcuts:**
   - Global window event listener added in ReplayViewer
   - Prevents default browser behavior (page scroll on Space, etc.)
   - Ignores shortcuts when user is in text input
   - Cleanup removes event listener on unmount

3. **Responsive Canvas:**
   - Calculate new dimensions on window resize
   - Maintain aspect ratio using `height / width` calculation
   - Cap at original dimensions to prevent upscaling
   - Regenerate stars when canvas size changes

4. **Loading & Error States:**
   - Loading: Spinning circle animation with inline CSS keyframes
   - Error: Red-bordered box with warning icon and retry guidance
   - Empty: Friendly message with folder icon

5. **Tooltips:**
   - Native `title` attributes for browser-native tooltips
   - Include keyboard shortcuts in tooltip text
   - Hover-based, no JS required

**Testing Results:**
- ✅ Build compiles successfully with zero warnings
- ✅ Match selector dropdown appears and fetches from /api/matches
- ✅ Keyboard shortcuts work (Space, Arrow keys, Home/End)
- ✅ Canvas resizes smoothly when window is resized
- ✅ Loading spinner displays during data fetch
- ✅ Error messages appear on fetch failure
- ✅ Tooltips appear on button hover
- ✅ Keyboard shortcuts help text is visible
- ✅ MatchSelector integrates cleanly into App.js

**Challenges & Resolutions:**
1. **Challenge:** Preventing keyboard shortcuts when user is typing
   - **Resolution:** Check `e.target.tagName` for INPUT/TEXTAREA/SELECT before handling shortcuts
2. **Challenge:** Maintaining canvas aspect ratio on resize
   - **Resolution:** Calculate `newHeight = newWidth * aspectRatio` using original dimensions
3. **Challenge:** Animating loading spinner without external libraries
   - **Resolution:** Inline CSS `@keyframes spin` with border-top color change

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
