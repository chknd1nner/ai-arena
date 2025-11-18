# Story 038: Thinking Token Display Integration

**Epic:** [Epic 006: Thinking Tokens Visualization & Frontend Polish](../epic-006-thinking-tokens-visualization.md)
**Status:** Not Started
**Size:** Medium (~2-3 hours)
**Priority:** P0

---

## Dev Agent Record

**Implementation Date:** [To be filled by Dev Agent]
**Agent:** [To be filled by Dev Agent]
**Status:** [To be filled by Dev Agent]

### Instructions for Dev Agent

When implementing this story:

1. **Import ThinkingPanel** into ReplayViewer component
2. **Wire up thinking token data** from replay turns to ThinkingPanel props
3. **Add visibility toggle** with state management (useState hook)
4. **Create toggle button** in UI with clear labeling
5. **Add keyboard shortcut** (T key) for toggle
6. **Update layout** to accommodate thinking panel without breaking existing UI
7. **Test with real replay data** (not just mock data)
8. **Verify turn navigation** updates thinking tokens correctly

**After implementation, update this section with:**
- Implementation date and your agent name
- Summary of integration work
- Layout decisions and approach
- File paths modified
- Any challenges encountered
- Code references (file:line format)
- Screenshot showing integrated thinking panel

---

## QA Agent Record

**Validation Date:** [To be filled by QA Agent]
**Validator:** [To be filled by QA Agent]
**Verdict:** [To be filled by QA Agent]

### Instructions for QA Agent

When validating this story:

1. **Integration validation:**
   - Load a real replay (use test replay buttons in App.js)
   - Verify ThinkingPanel appears and displays thinking tokens
   - Check that both Ship A and Ship B thinking tokens are correct
   - Navigate through turns - verify thinking updates on each turn change

2. **Toggle functionality:**
   - Click toggle button - verify panel shows/hides
   - Press 'T' key - verify keyboard shortcut works
   - Verify toggle state persists during turn navigation
   - Check that hiding panel doesn't break layout

3. **Layout validation:**
   - Verify thinking panel fits properly in page layout
   - Check that canvas, controls, and state overlay still visible
   - Verify no overlapping elements
   - Check responsive behavior (try different window sizes)

4. **Data correctness:**
   - Compare thinking tokens in UI with replay JSON
   - Verify turn numbers match between panel and playback controls
   - Verify model names displayed correctly
   - Check for any data loading issues

5. **User experience:**
   - Check that toggle button is prominent and clear
   - Verify keyboard shortcut hint is visible
   - Verify smooth transitions when toggling
   - Check that overall flow feels natural

**After validation, update this section with:**
- Validation date and your name
- Test results for each validation criterion
- Screenshots showing integration in working replay viewer
- Any issues found
- Overall verdict (PASSED/FAILED/BLOCKED)

---

## User Story

**As a** spectator
**I want** thinking tokens integrated into the replay viewer
**So that** I can see AI reasoning while watching matches

## Context

Story 037 created the ThinkingPanel component. This story integrates it into the existing ReplayViewer so users can actually see thinking tokens when watching replays.

The replay data already contains thinking tokens in every turn:
```json
{
  "thinking_a": "Distance is 250 units...",
  "thinking_b": "[BALANCED] Turn 5: Adaptive tactical decision..."
}
```

We need to wire this data into the UI and give users control over visibility.

## Acceptance Criteria

- [ ] ThinkingPanel imported and used in ReplayViewer
- [ ] Thinking tokens from current turn passed to ThinkingPanel
- [ ] Model names (model_a, model_b) passed from replay metadata
- [ ] Toggle button added to ReplayViewer UI
- [ ] Keyboard shortcut (T key) implemented for toggle
- [ ] Panel visibility state managed with useState
- [ ] Toggle state doesn't break turn navigation
- [ ] Thinking tokens update correctly when turn changes
- [ ] Layout accommodates thinking panel without breaking existing UI
- [ ] Works with all test replays (strafing, retreat, tactical showcase)
- [ ] Previous turn thinking tokens available (for future diff highlighting)
- [ ] No console errors or warnings

## Technical Details

### ReplayViewer.jsx Modifications

**Add imports:**
```javascript
import ThinkingPanel from './ThinkingPanel';
```

**Add state for visibility toggle:**
```javascript
const [showThinking, setShowThinking] = useState(true); // Default: visible
```

**Extract thinking token data:**
```javascript
// In ReplayViewer function body
const currentTurn = replay.turns[currentTurnIndex];
const previousTurn = currentTurnIndex > 0 ? replay.turns[currentTurnIndex - 1] : null;

// Extract thinking tokens
const thinkingA = currentTurn?.thinking_a || '';
const thinkingB = currentTurn?.thinking_b || '';
const prevThinkingA = previousTurn?.thinking_a || '';
const prevThinkingB = previousTurn?.thinking_b || '';

// Extract model names from replay metadata
const modelA = replay.model_a || replay.models?.ship_a || 'Unknown';
const modelB = replay.model_b || replay.models?.ship_b || 'Unknown';
```

**Add keyboard shortcut:**
```javascript
React.useEffect(() => {
  const handleKeyPress = (e) => {
    // Ignore if user is typing in an input field
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.tagName === 'SELECT') {
      return;
    }

    switch (e.key) {
      case ' ':
        e.preventDefault();
        togglePlayPause();
        break;
      case 'ArrowLeft':
        e.preventDefault();
        jumpToTurn(Math.max(0, currentTurnIndex - 1));
        break;
      case 'ArrowRight':
        e.preventDefault();
        jumpToTurn(Math.min(totalTurns - 1, currentTurnIndex + 1));
        break;
      case 'Home':
        e.preventDefault();
        jumpToTurn(0);
        break;
      case 'End':
        e.preventDefault();
        jumpToTurn(totalTurns - 1);
        break;
      case 't':
      case 'T':
        e.preventDefault();
        setShowThinking(prev => !prev); // NEW: Toggle thinking panel
        break;
      default:
        break;
    }
  };

  window.addEventListener('keydown', handleKeyPress);
  return () => window.removeEventListener('keydown', handleKeyPress);
}, [currentTurnIndex, totalTurns, togglePlayPause, jumpToTurn]);
```

**Add toggle button in UI:**
```javascript
{/* Updated controls section */}
<section className="controls">
  <button onClick={startMatch} disabled={loading}>
    {loading ? 'Starting Match...' : 'Start New Match'}
  </button>
  <button
    onClick={() => setShowThinking(!showThinking)}
    style={{
      marginLeft: '10px',
      backgroundColor: showThinking ? '#4A90E2' : '#333',
      color: '#fff',
      padding: '10px 20px',
      border: 'none',
      borderRadius: '4px',
      cursor: 'pointer',
      fontWeight: 'bold'
    }}
    title="Toggle thinking tokens (T key)"
  >
    {showThinking ? '🧠 Hide Thinking' : '🧠 Show Thinking'}
  </button>
</section>
```

**Integrate ThinkingPanel in render:**
```javascript
return (
  <div style={{ width: '100%', padding: '20px' }}>
    {/* Match Info Header */}
    <div style={{
      marginBottom: '20px',
      padding: '15px',
      backgroundColor: '#1a1a1a',
      borderRadius: '8px',
      color: '#fff'
    }}>
      <h3 style={{ margin: '0 0 10px 0' }}>
        Match: {replay.match_id}
      </h3>
      <div style={{ display: 'flex', gap: '30px', fontSize: '14px', color: '#aaa' }}>
        <div>
          <span style={{ color: '#4A90E2', fontWeight: 'bold' }}>Ship A:</span> {modelA}
        </div>
        <div>
          <span style={{ color: '#E24A4A', fontWeight: 'bold' }}>Ship B:</span> {modelB}
        </div>
      </div>
    </div>

    {/* NEW: Thinking Panel */}
    <ThinkingPanel
      thinkingA={thinkingA}
      thinkingB={thinkingB}
      turnNumber={currentTurnIndex}
      modelA={modelA}
      modelB={modelB}
      isVisible={showThinking}
      previousThinkingA={prevThinkingA}
      previousThinkingB={prevThinkingB}
    />

    {/* Canvas Renderer */}
    <div style={{ marginBottom: '20px' }}>
      <CanvasRenderer
        width={1200}
        height={800}
        turnState={currentTurn?.state}
        events={currentTurn?.events || []}
      />
    </div>

    {/* Playback Controls */}
    <div style={{ marginBottom: '20px' }}>
      <PlaybackControls
        playing={playing}
        speed={speed}
        currentTurn={currentTurnIndex}
        maxTurns={totalTurns}
        onTogglePlayPause={togglePlayPause}
        onChangeSpeed={changeSpeed}
        onJumpToTurn={jumpToTurn}
      />
    </div>

    {/* Keyboard Shortcuts Help - UPDATE to include T key */}
    <div style={{
      marginBottom: '20px',
      padding: '12px 15px',
      backgroundColor: '#1a1a1a',
      borderRadius: '8px',
      fontSize: '12px',
      color: '#888'
    }}>
      <strong style={{ color: '#aaa' }}>Keyboard Shortcuts:</strong>
      {' '}
      <span style={{ color: '#4A90E2' }}>Space</span> = Play/Pause
      {' • '}
      <span style={{ color: '#4A90E2' }}>← →</span> = Previous/Next Turn
      {' • '}
      <span style={{ color: '#4A90E2' }}>Home/End</span> = First/Last Turn
      {' • '}
      <span style={{ color: '#4A90E2' }}>T</span> = Toggle Thinking
    </div>

    {/* State Overlay */}
    <StateOverlay
      turnState={currentTurn?.state}
      turnNumber={currentTurnIndex}
      maxTurns={totalTurns}
      events={currentTurn?.events || []}
      matchInfo={{
        match_id: replay.match_id,
        model_a: modelA,
        model_b: modelB,
        winner: replay.winner
      }}
    />
  </div>
);
```

### Data Flow Diagram

```
Replay JSON
    │
    ├─> turns[currentTurnIndex].thinking_a ──┐
    ├─> turns[currentTurnIndex].thinking_b ──┤
    ├─> model_a (or models.ship_a)      ──┤
    ├─> model_b (or models.ship_b)      ──┤
    └─> currentTurnIndex                ──┤
                                          │
                                          ▼
                                   ThinkingPanel
                                          │
                                          ▼
                                  Rendered UI
```

### Model Name Extraction (Handle Format Differences)

The replay format changed in Epic 005. Handle both old and new formats:

```javascript
// Old format: replay.model_a, replay.model_b
// New format: replay.models.ship_a, replay.models.ship_b

const modelA = replay.model_a || replay.models?.ship_a || 'Unknown Model A';
const modelB = replay.model_b || replay.models?.ship_b || 'Unknown Model B';
```

### Error Handling

```javascript
// Handle missing thinking tokens gracefully
const thinkingA = currentTurn?.thinking_a || '(No thinking data available)';
const thinkingB = currentTurn?.thinking_b || '(No thinking data available)';

// Handle missing replay metadata
if (!replay || !replay.turns || replay.turns.length === 0) {
  return <div>No replay data available</div>;
}

// Handle invalid turn index
const safeTurnIndex = Math.max(0, Math.min(currentTurnIndex, replay.turns.length - 1));
const currentTurn = replay.turns[safeTurnIndex];
```

## Layout Considerations

### Current ReplayViewer Layout
```
┌─────────────────────────────────────────┐
│  Match Info                             │
├─────────────────────────────────────────┤
│  Canvas (1200x800)                      │
├─────────────────────────────────────────┤
│  Playback Controls                      │
├─────────────────────────────────────────┤
│  Keyboard Shortcuts                     │
├─────────────────────────────────────────┤
│  State Overlay                          │
└─────────────────────────────────────────┘
```

### Updated Layout with Thinking Panel
```
┌─────────────────────────────────────────┐
│  Match Info + Toggle Button             │
├─────────────────────────────────────────┤
│  Thinking Panel (if visible)            │
│  ┌────────────┬────────────┐            │
│  │ Ship A     │ Ship B     │            │
│  └────────────┴────────────┘            │
├─────────────────────────────────────────┤
│  Canvas (1200x800)                      │
├─────────────────────────────────────────┤
│  Playback Controls                      │
├─────────────────────────────────────────┤
│  Keyboard Shortcuts (updated)           │
├─────────────────────────────────────────┤
│  State Overlay                          │
└─────────────────────────────────────────┘
```

**Key Layout Decisions:**
1. Thinking panel goes ABOVE canvas (prime real estate)
2. Thinking panel can be hidden without affecting other elements
3. Toggle button prominent in header section
4. Keyboard shortcuts help updated to include T key

## Testing Checklist

### Functional Testing
- [ ] Load test replay "strafing_maneuver"
- [ ] Verify thinking tokens displayed for both ships
- [ ] Navigate to turn 3 - verify thinking updates
- [ ] Navigate to turn 5 - verify thinking updates
- [ ] Press T key - verify panel hides
- [ ] Press T key again - verify panel shows
- [ ] Click toggle button - verify same behavior as T key
- [ ] Play through entire replay - verify thinking updates each turn

### Data Correctness Testing
- [ ] Open replay JSON and compare thinking_a text with UI
- [ ] Verify model names match replay metadata
- [ ] Verify turn numbers match between panel and controls
- [ ] Test with replay that has empty thinking tokens
- [ ] Test with replay that has very long thinking tokens

### Layout Testing
- [ ] Verify thinking panel doesn't overlap canvas
- [ ] Verify hiding panel doesn't create layout shift
- [ ] Verify all elements still visible and accessible
- [ ] Test on 1920x1080 screen
- [ ] Test on 1366x768 screen
- [ ] Test on 2560x1440 screen

## Deliverables

- [ ] `frontend/src/components/ReplayViewer.jsx` - Updated with ThinkingPanel integration
- [ ] Toggle button implemented and styled
- [ ] Keyboard shortcut (T) working
- [ ] Keyboard shortcuts help updated
- [ ] Screenshot showing integrated thinking panel with real replay data
- [ ] Dev Agent Record updated with implementation details

## Definition of Done

- [ ] ThinkingPanel integrated into ReplayViewer
- [ ] Thinking token data wired correctly from replay
- [ ] Toggle button and keyboard shortcut working
- [ ] Turn navigation updates thinking tokens
- [ ] Layout works correctly with panel visible/hidden
- [ ] Tested with multiple real replays
- [ ] Model names displayed correctly
- [ ] Previous turn data available (for future diff highlighting)
- [ ] No console errors
- [ ] Screenshot taken showing integration
- [ ] Dev Agent Record completed
- [ ] Ready for QA validation

## Notes

**Implementation Priority:**
1. Get basic integration working first (data flow)
2. Add toggle functionality
3. Polish the toggle button styling
4. Test with real replays
5. Handle edge cases

**Data Compatibility:**
- Handle both old replay format (model_a/model_b)
- And new replay format (models.ship_a/models.ship_b)
- Use optional chaining (?.) to prevent crashes

**User Experience:**
- Default to thinking panel VISIBLE (core feature)
- Make toggle button prominent and clear
- Include keyboard hint in button tooltip
- Update keyboard shortcuts help prominently

**Future Enhancement Hooks:**
- Previous turn data already passed (for diff highlighting in Story 039)
- Component structure supports adding match summary later

---

**Story 038 Ready for Implementation** 🔌
