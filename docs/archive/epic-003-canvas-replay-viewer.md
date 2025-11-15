# Epic 003: Canvas-Based Match Replay Viewer

**Status:** Planning
**Priority:** P0 (High Impact)
**Estimated Size:** Large (8 stories, 10-14 hours)
**Target for:** Claude Code Web

---

## Overview

Build a React canvas-based visualization system that loads match replay JSON and renders battles in real-time with playback controls. This will make Epic 002's tactical maneuvers visible and provide the foundation for all future development by enabling visual debugging, balance tuning, and compelling demonstrations.

## Problem Statement

Currently, AI Arena matches are only observable through:
- JSON replay files in `/replays` directory
- Console logs during match execution
- Final match status API responses

**What we cannot see:**
- Ships executing tactical maneuvers (strafing, retreat with coverage, drift attacks)
- The difference between heading (where ship faces) and velocity (where ship moves)
- Phaser arcs and firing events
- Torpedo trajectories and explosions
- Real-time spatial relationships during combat

**Example of missing visibility:**
- Epic 002 implemented independent movement/rotation enabling a ship to "strafe right while rotating left to maintain gun lock"
- Tests prove this works, but we've never SEEN it happen
- The tactical depth is theoretical without visual confirmation

## Goals

1. **Visual Replay System**: Load any replay JSON and watch the match unfold
2. **Heading vs Velocity Visualization**: Clearly show Epic 002's independent movement/rotation
3. **Playback Controls**: Play, pause, scrub timeline, adjust speed
4. **Weapon Rendering**: Display phaser arcs and torpedo trajectories
5. **State Overlay**: Show shields, AE, turn counter, event log
6. **Foundation for Future**: Architecture supports live streaming, tactical overlays, tournaments

## Success Criteria

- [ ] Can load any replay from `/api/match/{id}/replay` endpoint
- [ ] Ships render with position, heading (triangle orientation), and velocity vector
- [ ] Heading and velocity are visually distinct (validates Epic 002)
- [ ] All 4 tactical maneuvers observable (strafing, retreat, reposition, drift)
- [ ] Phaser arcs render with correct configuration (WIDE vs FOCUSED)
- [ ] Torpedoes render with motion trails
- [ ] Playback controls work smoothly (play/pause/scrub/speed)
- [ ] State overlay displays shields, AE, turn number
- [ ] 60 FPS rendering with smooth interpolation
- [ ] Canvas responsive to window sizing

## User Stories

1. [Story 012: Canvas Foundation & Coordinate System](stories/story-012-canvas-foundation.md)
2. [Story 013: Ship Rendering](stories/story-013-ship-rendering.md)
3. [Story 014: Replay Data Integration](stories/story-014-replay-data-integration.md)
4. [Story 015: Basic Playback Controls](stories/story-015-playback-controls.md)
5. [Story 016: Weapon Visualization](stories/story-016-weapon-visualization.md)
6. [Story 017: Game State Overlay](stories/story-017-game-state-overlay.md)
7. [Story 018: Visual Polish](stories/story-018-visual-polish.md)
8. [Story 019: UX Refinements](stories/story-019-ux-refinements.md)

## Technical Approach

### Current Implementation (Pre-Epic 003)

**Frontend Structure:**
```
frontend/
├── src/
│   ├── App.js           # Main app component
│   ├── components/      # React components
│   └── index.js         # Entry point
└── package.json
```

**Match Viewing:**
- Start match button
- Status polling (running/completed)
- Final results display
- No spatial visualization

### Target Implementation (Epic 003 Goal)

**New Components:**
```javascript
// Canvas replay viewer component
<ReplayViewer matchId={matchId} />

// Architecture:
ReplayViewer
├── CanvasRenderer      // HTML5 Canvas drawing
├── PlaybackControls    // Play/pause/scrub/speed
├── StateOverlay        // Shields, AE, turn info
└── ReplayLoader        // Fetch and parse JSON
```

**Core Rendering Loop:**
```javascript
// 60 FPS animation loop
function renderFrame(timestamp) {
  const currentTurn = getCurrentTurn(timestamp, playbackSpeed);
  const state = interpolateState(replayData, currentTurn);

  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Render in layers
  renderArena(ctx);
  renderShips(ctx, state.ship_a, state.ship_b);
  renderTorpedoes(ctx, state.torpedoes);
  renderWeapons(ctx, state.events);

  requestAnimationFrame(renderFrame);
}
```

**Coordinate Transformation:**
```javascript
// World coordinates → Screen coordinates
function worldToScreen(worldPos, canvasSize, worldBounds) {
  const scaleX = canvasSize.width / worldBounds.width;
  const scaleY = canvasSize.height / worldBounds.height;
  const scale = Math.min(scaleX, scaleY); // Maintain aspect ratio

  return {
    x: worldPos.x * scale + canvasSize.width / 2,
    y: canvasSize.height / 2 - worldPos.y * scale  // Flip Y axis
  };
}
```

**Ship Rendering:**
```javascript
function renderShip(ctx, ship, color) {
  const pos = worldToScreen(ship.position);

  // Draw triangle pointing at heading
  const size = 20;
  const angle = ship.heading;

  ctx.save();
  ctx.translate(pos.x, pos.y);
  ctx.rotate(angle);

  // Triangle (heading indicator)
  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.moveTo(size, 0);          // Nose
  ctx.lineTo(-size, size/2);     // Bottom right
  ctx.lineTo(-size, -size/2);    // Bottom left
  ctx.closePath();
  ctx.fill();

  ctx.restore();

  // Velocity vector (shows movement direction)
  if (ship.velocity.magnitude() > 0) {
    const velAngle = Math.atan2(ship.velocity.y, ship.velocity.x);
    const velLength = 30;

    ctx.strokeStyle = 'rgba(255, 255, 255, 0.7)';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(pos.x, pos.y);
    ctx.lineTo(
      pos.x + Math.cos(velAngle) * velLength,
      pos.y - Math.sin(velAngle) * velLength  // Flip Y
    );
    ctx.stroke();
  }
}
```

**Result:** Ships show both heading (triangle orientation) and velocity (arrow), making Epic 002's independent movement visible.

## Architecture Changes

### Frontend Structure (New)

**New Components:**
```
frontend/src/
├── components/
│   ├── ReplayViewer.jsx         # Main viewer component
│   ├── CanvasRenderer.jsx       # Canvas drawing logic
│   ├── PlaybackControls.jsx    # UI controls
│   ├── StateOverlay.jsx         # Game state display
│   └── MatchSelector.jsx        # Pick replay to watch
├── utils/
│   ├── replayLoader.js          # API integration
│   ├── coordinateTransform.js   # World ↔ Screen
│   └── interpolation.js         # Smooth playback
└── hooks/
    └── useReplayPlayback.js     # Playback state management
```

### API Integration

**Existing Endpoint (No Changes Needed):**
```
GET /api/match/{match_id}/replay
Returns: Complete replay JSON with all turns
```

**Replay JSON Structure:**
```json
{
  "match_id": "uuid",
  "model_a": "gpt-4",
  "model_b": "claude-3-haiku",
  "turns": [
    {
      "turn": 0,
      "state": {
        "ship_a": {
          "position": {"x": 0, "y": 100},
          "velocity": {"x": 10, "y": 0},
          "heading": 0.785,  // Radians
          "shields": 100,
          "ae": 95
        },
        // ... ship_b, torpedoes
      },
      "events": [
        {"type": "phaser_hit", "damage": 15, "attacker": "a"}
      ]
    }
  ]
}
```

### Technology Stack

**Rendering:**
- HTML5 Canvas API (not WebGL - simpler for 2D)
- 60 FPS with `requestAnimationFrame`
- Manual interpolation between discrete turns

**State Management:**
- React hooks for playback state
- No Redux/complex state management needed initially

**Styling:**
- CSS for controls and overlays
- Canvas for game visualization

## Dependencies

- **Requires:**
  - Epic 001 (Configuration System) - ✅ Complete
  - Epic 002 (Independent Movement/Rotation) - ✅ Complete
  - Existing replay API endpoint - ✅ Available
- **Blocks:** None (pure frontend, doesn't block backend work)
- **Enables:**
  - Visual validation of all future physics changes
  - Tournament viewing systems
  - Live match streaming (future)

## Risk Assessment

**Low-Medium Risk**

**Technical Risks:**
- Canvas performance with many entities (torpedoes, effects)
- Interpolation accuracy between discrete turns
- Coordinate system bugs (world ↔ screen mapping)
- Replay JSON parsing edge cases

**UX Risks:**
- Unclear visualization (heading vs velocity confusion)
- Playback controls feel clunky
- Information overload (too much overlay)

**Mitigation Strategies:**
1. **Incremental Stories:** Each story adds testable functionality
2. **Start Simple:** Basic rendering first, polish later
3. **No Backend Changes:** Frontend-only reduces risk
4. **Manual Testing:** Visual bugs are immediately obvious
5. **Existing Replays:** Use Epic 002 replays for validation

## Testing Strategy

### Manual Testing (Primary)
1. **Visual Inspection**: Load replays and watch them
2. **Tactical Validation**: Verify Epic 002 maneuvers look correct
3. **Control Testing**: Test play/pause/scrub/speed controls
4. **Edge Cases**: Very short matches, very long matches, many torpedoes

### Automated Testing (Optional)
- Unit tests for coordinate transformation
- Unit tests for interpolation logic
- Component rendering tests (React Testing Library)

### Acceptance Testing
- [ ] Load 5 different replays successfully
- [ ] All 4 tactical maneuvers visible in test matches
- [ ] Playback controls respond within 100ms
- [ ] Canvas scales correctly on resize
- [ ] No rendering errors in console

## Definition of Done

- All acceptance criteria met for all 8 user stories
- Can watch any replay from `/replays` directory
- Epic 002's tactical maneuvers clearly visible
- Playback controls work smoothly
- State overlay displays correct information
- Canvas responsive to window sizing
- No console errors during playback
- Documentation updated (CLAUDE.md if needed)
- Code committed to feature branch

## Notes for Claude Code Web

This epic is designed for **one feature branch** with incremental commits:
- Clear scope: Frontend visualization only
- Natural progression: Canvas → Ships → Data → Controls → Weapons → Polish
- Stories are mostly independent after foundation
- Creates high-impact user-facing feature
- Estimated: 10-14 hours of Claude Code Web development time

**Implementation Strategy:**
- Story 012 (Canvas Foundation) is fully independent - start here
- Story 013 (Ship Rendering) depends on 012 but can use mock data
- Story 014 (Replay Integration) connects to real API
- Stories 015-019 add features incrementally

**Testing Approach:**
- Visual testing is primary validation method
- Run backend: `python3 main.py`
- Run frontend: `cd frontend && npm start`
- Load existing replays from Epic 002 implementation
- Watch and verify tactical maneuvers look correct

## Future Enhancements (Out of Scope)

- Live match streaming via WebSocket
- Tactical analysis tools (distance measurement, angle indicators)
- Match comparison view (side-by-side)
- Cinematic camera modes (follow ships, zoom on action)
- Export to video/GIF
- 3D rendering with Three.js

## Next Steps After Epic 003

Once visualization is complete, consider:

1. **Epic 004: Continuous Physics System** - Now easier to validate with visuals
2. **Epic 005: Tournament Infrastructure** - Batch matches with viewer integration
3. **Epic 006: Enhanced Torpedo Tactics** - Visual feedback for new mechanics
4. **Epic 007: Live Match Streaming** - WebSocket + real-time viewer
