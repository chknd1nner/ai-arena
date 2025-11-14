# Story 014: Replay Data Integration

**Epic:** [Epic 003: Canvas-Based Match Replay Viewer](../epic-003-canvas-replay-viewer.md)
**Status:** Not Started
**Size:** Medium (~1.5-2 hours)
**Priority:** P0

---

## User Story

**As a** player
**I want** to load a replay JSON file and see it visualized on the canvas
**So that** I can watch actual matches instead of just mock data

## Context

Replace mock ship data with real replay data from the API. This connects the visualization to actual match results, making the viewer functional for real games.

We have test replays available:
- `/replays/test_strafing_maneuver.json` - Ship A circles Ship B while maintaining gun lock
- `/replays/test_retreat_coverage.json` - Ship A retreats west while facing east

## Acceptance Criteria

- [ ] Can fetch replay JSON from `/api/match/{id}/replay` endpoint
- [ ] Parse replay JSON into renderable state
- [ ] Replace mock data with real replay turn data
- [ ] Display correct turn from replay timeline
- [ ] Handle loading states (loading, error, success)
- [ ] Can load different replays by match ID
- [ ] All ship properties (position, heading, velocity, shields, AE) from replay

## Technical Requirements

### Replay Loader Hook

**File:** `frontend/src/hooks/useReplayData.js`

```javascript
import { useState, useEffect } from 'react';

export function useReplayData(matchId) {
  const [replay, setReplay] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!matchId) return;

    setLoading(true);
    setError(null);

    fetch(`/api/match/${matchId}/replay`)
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then(data => {
        setReplay(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, [matchId]);

  return { replay, loading, error };
}
```

### Replay Viewer Component

**File:** `frontend/src/components/ReplayViewer.jsx`

```jsx
import React, { useState } from 'react';
import CanvasRenderer from './CanvasRenderer';
import { useReplayData } from '../hooks/useReplayData';

const ReplayViewer = ({ matchId }) => {
  const { replay, loading, error } = useReplayData(matchId);
  const [currentTurn, setCurrentTurn] = useState(0);

  if (loading) return <div>Loading replay...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!replay) return <div>No replay loaded</div>;

  const turnData = replay.turns[currentTurn];

  return (
    <div>
      <h2>Match Replay: {replay.model_a} vs {replay.model_b}</h2>

      <div style={{ marginBottom: '10px' }}>
        <button
          onClick={() => setCurrentTurn(Math.max(0, currentTurn - 1))}
          disabled={currentTurn === 0}
        >
          Previous Turn
        </button>
        <span style={{ margin: '0 20px' }}>
          Turn {currentTurn + 1} / {replay.turns.length}
        </span>
        <button
          onClick={() => setCurrentTurn(Math.min(replay.turns.length - 1, currentTurn + 1))}
          disabled={currentTurn === replay.turns.length - 1}
        >
          Next Turn
        </button>
      </div>

      <CanvasRenderer turnState={turnData.state} />

      <div style={{ marginTop: '10px' }}>
        <strong>Events this turn:</strong>
        {turnData.events.length === 0 ? ' None' : (
          <ul>
            {turnData.events.map((event, idx) => (
              <li key={idx}>{JSON.stringify(event)}</li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default ReplayViewer;
```

### Update Canvas Renderer to Accept Data

**File:** `frontend/src/components/CanvasRenderer.jsx` (modify)

```jsx
const CanvasRenderer = ({ turnState, width = 1200, height = 800 }) => {
  // ... existing code ...

  const renderFrame = (ctx, dims) => {
    ctx.clearRect(0, 0, dims.width, dims.height);
    renderArena(ctx, dims);

    if (turnState) {
      // Render real data
      renderShip(ctx, turnState.ship_a, '#4A90E2', dims, worldBounds, 'Ship A');
      renderShip(ctx, turnState.ship_b, '#E24A4A', dims, worldBounds, 'Ship B');

      // Render torpedoes
      turnState.torpedoes.forEach((torpedo, idx) => {
        renderTorpedo(ctx, torpedo, dims, worldBounds);
      });
    } else {
      // Fallback to mock data for testing
      // ... existing mock data code ...
    }
  };

  // ... rest of component ...
};
```

### Update App Integration

**File:** `frontend/src/App.js` (modify)

```javascript
import ReplayViewer from './components/ReplayViewer';

function App() {
  const [replayMatchId, setReplayMatchId] = useState(null);

  // ... existing match start code ...

  return (
    <div className="App">
      <h1>AI Arena</h1>

      {/* Match selector */}
      <div>
        <h3>Test Replays</h3>
        <button onClick={() => setReplayMatchId('test_strafing_maneuver')}>
          Watch Strafing Maneuver
        </button>
        <button onClick={() => setReplayMatchId('test_retreat_coverage')}>
          Watch Retreat with Coverage
        </button>
      </div>

      {/* Replay viewer */}
      {replayMatchId && (
        <ReplayViewer matchId={replayMatchId} />
      )}
    </div>
  );
}
```

## Testing & Validation

### Manual Testing Checklist

- [ ] Click "Watch Strafing Maneuver" button
- [ ] Replay loads without errors
- [ ] Ship A circles around Ship B
- [ ] Can step through turns with Previous/Next buttons
- [ ] Heading and velocity vectors show strafing maneuver
- [ ] Load "Watch Retreat with Coverage" replay
- [ ] Ship A moves west (velocity) while facing east (heading)
- [ ] Events display correctly

### API Testing

Test that API endpoint works:
```bash
# Start backend first: python3 main.py

curl http://localhost:8000/api/matches
# Should list test replays

curl http://localhost:8000/api/match/test_strafing_maneuver/replay
# Should return full replay JSON
```

## Implementation Checklist

- [ ] Create `frontend/src/hooks/useReplayData.js`
- [ ] Create `frontend/src/components/ReplayViewer.jsx`
- [ ] Modify `CanvasRenderer.jsx` to accept `turnState` prop
- [ ] Update `App.js` to integrate ReplayViewer
- [ ] Add basic turn navigation (prev/next buttons)
- [ ] Test loading test_strafing_maneuver replay
- [ ] Test loading test_retreat_coverage replay
- [ ] Verify Epic 002 maneuvers are visible
- [ ] Handle loading/error states gracefully
- [ ] Commit changes

## Definition of Done

- [ ] Can load any replay by match ID
- [ ] Replay data renders correctly on canvas
- [ ] Epic 002 tactical maneuvers visible in test replays
- [ ] Turn navigation works
- [ ] Loading and error states handled
- [ ] No console errors

## Files to Create/Modify

- Create: `frontend/src/hooks/useReplayData.js`
- Create: `frontend/src/components/ReplayViewer.jsx`
- Modify: `frontend/src/components/CanvasRenderer.jsx`
- Modify: `frontend/src/App.js`

## Dependencies

- **Requires:** Stories 012, 013 (canvas and ship rendering)
- **Requires:** Backend running (`python3 main.py`)
- **Requires:** Test replays (generated by `scripts/generate_test_replay.py`)
- **Blocks:** Stories 015-019 (need real data for playback features)

## Notes

**Test Replay IDs:**
- `test_strafing_maneuver` - 20 turns, Ship A circles Ship B
- `test_retreat_coverage` - 15 turns, Ship A retreats while facing forward

**Next Story (015):** Add automatic playback instead of manual turn navigation.
