# Story 018: Visual Polish

**Epic:** [Epic 003: Canvas-Based Match Replay Viewer](../epic-003-canvas-replay-viewer.md)
**Status:** Not Started
**Size:** Small-Medium (~1.5-2 hours)
**Priority:** P2

---

## User Story

**As a** player
**I want** smooth animations and visual effects
**So that** matches are engaging and easy to follow

## Acceptance Criteria

- [ ] Smooth interpolation between turns (not jumpy)
- [ ] Ship colors distinct and visually appealing
- [ ] Damage indicators (shields turn red when low)
- [ ] Phaser firing animation (flash effect)
- [ ] Torpedo explosion animation
- [ ] Background (space stars or grid)
- [ ] Smooth transitions feel natural

## Technical Approach

**Interpolation Between Turns:**
```javascript
// frontend/src/utils/interpolation.js
export function interpolateState(prevState, nextState, alpha) {
  // alpha ∈ [0, 1]: 0 = prevState, 1 = nextState
  return {
    ship_a: interpolateShip(prevState.ship_a, nextState.ship_a, alpha),
    ship_b: interpolateShip(prevState.ship_b, nextState.ship_b, alpha),
    torpedoes: interpolateTorpedoes(prevState.torpedoes, nextState.torpedoes, alpha)
  };
}

function interpolateShip(prev, next, alpha) {
  return {
    position: {
      x: prev.position.x + (next.position.x - prev.position.x) * alpha,
      y: prev.position.y + (next.position.y - prev.position.y) * alpha
    },
    heading: interpolateAngle(prev.heading, next.heading, alpha),
    velocity: prev.velocity, // Use current velocity
    shields: prev.shields + (next.shields - prev.shields) * alpha,
    ae: prev.ae + (next.ae - prev.ae) * alpha,
    phaser_config: prev.phaser_config
  };
}

function interpolateAngle(prev, next, alpha) {
  // Handle angle wrapping (e.g., 359° to 1° should go through 0°, not 358°)
  let diff = next - prev;
  if (diff > Math.PI) diff -= 2 * Math.PI;
  if (diff < -Math.PI) diff += 2 * Math.PI;
  return prev + diff * alpha;
}
```

**Visual Effects:**
- Phaser firing: Bright flash on arc
- Low shields: Red tint on ship
- Explosion: Expanding circle with fade
- Background: Starfield with parallax

## Files to Create/Modify

- Create: `frontend/src/utils/interpolation.js`
- Create: `frontend/src/utils/visualEffects.js`
- Modify: `frontend/src/components/CanvasRenderer.jsx`

## Dependencies

- **Requires:** Stories 012-016 (all rendering features)
