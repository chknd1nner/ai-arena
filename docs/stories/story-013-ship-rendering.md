# Story 013: Ship Rendering

**Epic:** [Epic 003: Canvas-Based Match Replay Viewer](../epic-003-canvas-replay-viewer.md)
**Status:** Ready for QA
**Size:** Medium (~1.5-2 hours)
**Priority:** P0

---

## User Story

**As a** player
**I want** to see ships rendered with their position, heading, and velocity
**So that** I can understand where ships are and how they're moving

## Context

This story brings ships to life on the canvas. We need to render:
1. **Ship body** - Triangle pointing at heading angle
2. **Velocity vector** - Arrow showing movement direction (may differ from heading!)
3. **Ship label** - "Ship A" / "Ship B" text
4. **Basic stats** - Shields and AE display

The key feature is showing **heading vs velocity** - Epic 002's core mechanic. The ship triangle points where the ship FACES, but the velocity arrow shows where it's MOVING.

## Acceptance Criteria

- [ ] Ships render as triangles with correct position
- [ ] Triangle orientation matches ship heading (rotation)
- [ ] Velocity vector renders as arrow (different from heading when strafing)
- [ ] Ship labels display ("Ship A" / "Ship B")
- [ ] Ships use distinct colors (e.g., blue vs red)
- [ ] Shields and AE visible near ship
- [ ] Can render with mock data (no API dependency yet)
- [ ] Visual distinction between heading and velocity is clear

## Technical Requirements

### Ship Rendering Function

**File:** `frontend/src/utils/shipRenderer.js`

```javascript
import { worldToScreen } from './coordinateTransform';

export function renderShip(ctx, ship, color, canvasSize, worldBounds, label) {
  const pos = worldToScreen(ship.position, canvasSize, worldBounds);

  // Draw ship body (triangle pointing at heading)
  const size = 20;
  const heading = ship.heading; // radians

  ctx.save();
  ctx.translate(pos.x, pos.y);
  ctx.rotate(-heading); // Negative because canvas Y is flipped

  // Triangle shape
  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.moveTo(size, 0);           // Nose
  ctx.lineTo(-size, size * 0.6);  // Bottom-right
  ctx.lineTo(-size, -size * 0.6); // Bottom-left
  ctx.closePath();
  ctx.fill();

  // Outline
  ctx.strokeStyle = '#fff';
  ctx.lineWidth = 2;
  ctx.stroke();

  ctx.restore();

  // Draw velocity vector if ship is moving
  const velMag = Math.sqrt(ship.velocity.x ** 2 + ship.velocity.y ** 2);
  if (velMag > 0.1) {
    const velAngle = Math.atan2(ship.velocity.y, ship.velocity.x);
    const velLength = 40;

    ctx.strokeStyle = `${color}AA`; // Semi-transparent
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(pos.x, pos.y);
    ctx.lineTo(
      pos.x + Math.cos(velAngle) * velLength,
      pos.y - Math.sin(velAngle) * velLength // Flip Y for canvas
    );
    ctx.stroke();

    // Arrowhead
    const arrowSize = 8;
    const arrowAngle = Math.PI / 6;
    ctx.beginPath();
    ctx.moveTo(
      pos.x + Math.cos(velAngle) * velLength,
      pos.y - Math.sin(velAngle) * velLength
    );
    ctx.lineTo(
      pos.x + Math.cos(velAngle - arrowAngle) * (velLength - arrowSize),
      pos.y - Math.sin(velAngle - arrowAngle) * (velLength - arrowSize)
    );
    ctx.moveTo(
      pos.x + Math.cos(velAngle) * velLength,
      pos.y - Math.sin(velAngle) * velLength
    );
    ctx.lineTo(
      pos.x + Math.cos(velAngle + arrowAngle) * (velLength - arrowSize),
      pos.y - Math.sin(velAngle + arrowAngle) * (velLength - arrowSize)
    );
    ctx.stroke();
  }

  // Draw label
  ctx.fillStyle = '#fff';
  ctx.font = '14px monospace';
  ctx.textAlign = 'center';
  ctx.fillText(label, pos.x, pos.y - size - 10);

  // Draw stats
  ctx.font = '12px monospace';
  ctx.fillText(`S:${ship.shields} AE:${ship.ae.toFixed(0)}`, pos.x, pos.y + size + 20);
}
```

### Update Canvas Renderer

**File:** `frontend/src/components/CanvasRenderer.jsx` (modify)

```jsx
import { renderShip } from '../utils/shipRenderer';

// In renderFrame(), add after renderArena():
const mockShipA = {
  position: { x: -200, y: 100 },
  velocity: { x: 10, y: 5 },  // Moving east-northeast
  heading: Math.PI / 4,        // Facing northeast (45°)
  shields: 85,
  ae: 67
};

const mockShipB = {
  position: { x: 150, y: -80 },
  velocity: { x: -8, y: 3 },   // Moving west-northwest
  heading: Math.PI,             // Facing west (180°)
  shields: 92,
  ae: 74
};

renderShip(ctx, mockShipA, '#4A90E2', dims, worldBounds, 'Ship A');
renderShip(ctx, mockShipB, '#E24A4A', dims, worldBounds, 'Ship B');
```

## Testing & Validation

### Visual Checklist

- [ ] Two ships render at different positions
- [ ] Ship A (blue) and Ship B (red) are distinguishable
- [ ] Triangles point at correct heading angles
- [ ] Velocity arrows show movement direction
- [ ] When heading ≠ velocity, both are visible and different
- [ ] Labels and stats display correctly
- [ ] Ships scale appropriately with canvas size

### Test Scenarios

**Scenario 1: Forward Movement**
```javascript
heading: 0,           // Facing east
velocity: { x: 10, y: 0 }  // Moving east
// Expected: Triangle and arrow point same direction
```

**Scenario 2: Strafing (Epic 002 feature!)**
```javascript
heading: Math.PI / 2,      // Facing north
velocity: { x: 10, y: 0 }  // Moving east
// Expected: Triangle points north, arrow points east
```

**Scenario 3: Retreat with Coverage**
```javascript
heading: 0,                // Facing east
velocity: { x: -10, y: 0 } // Moving west (backward)
// Expected: Triangle points east, arrow points west
```

## Implementation Checklist

- [ ] Create `frontend/src/utils/shipRenderer.js`
- [ ] Implement `renderShip()` function
- [ ] Update `CanvasRenderer.jsx` to render mock ships
- [ ] Test forward movement (heading = velocity direction)
- [ ] Test strafing (heading ≠ velocity direction)
- [ ] Adjust colors for visibility
- [ ] Verify stats display correctly
- [ ] Test with different positions and angles
- [ ] Commit changes

## Definition of Done

- [ ] Ships render correctly at any position/angle
- [ ] Heading and velocity are visually distinct
- [ ] Can demonstrate Epic 002's strafing capability with mock data
- [ ] Labels and stats readable
- [ ] No visual glitches or rendering errors

## Files to Create/Modify

- Create: `frontend/src/utils/shipRenderer.js`
- Modify: `frontend/src/components/CanvasRenderer.jsx`

## Dependencies

- **Requires:** Story 012 (Canvas Foundation)
- **Blocks:** Story 014 (needs ships to display replay data)

## Notes

**Why Mock Data:**
- Can test ship rendering without API
- Easy to create test scenarios (strafing, retreat, etc.)
- Story 014 will replace mock data with real replay JSON

**Key Visual Goal:**
- Make heading vs velocity OBVIOUS
- This validates Epic 002's biggest feature
- Players should immediately see when a ship is strafing

---

## Dev Agent Record

**Completed:** 2025-11-14
**Agent:** Claude
**Commit:** 4d32367

### Implementation Notes

Successfully implemented ship rendering with complete visual distinction between heading and velocity:

**Files Created:**
- `frontend/src/utils/shipRenderer.js` - Complete ship rendering system with triangle (heading) and arrow (velocity) visualization

**Files Modified:**
- `frontend/src/components/CanvasRenderer.jsx` - Updated to render ships using mock data and accept optional turnState prop

**Implementation Details:**
1. **Ship Triangle (Heading):** Rendered as filled triangle with white outline, rotates based on ship.heading, clearly shows which direction ship is facing
2. **Velocity Vector (Movement Arrow):** Semi-transparent arrow showing actual movement direction, includes arrowhead, scales with velocity magnitude
3. **Ship Stats Display:** Shows ship label above ship, displays shields and AE below ship
4. **Color Scheme:** Ship A uses blue (#4A90E2), Ship B uses red (#E24A4A) for clear distinction
5. **Mock Data:** Added example ships with different heading/velocity combinations to demonstrate strafing

**Key Technical Decisions:**
- Used canvas coordinate transformation (ctx.translate/rotate) for clean heading rotation
- Applied negative rotation (-heading) to compensate for flipped canvas Y-axis
- Made velocity arrow semi-transparent (alpha 0.7) to distinguish from heading triangle
- Set minimum velocity threshold (0.1) before drawing arrow to avoid rendering for stationary ships
- Positioned labels/stats relative to ship size for consistent spacing

**Visual Validation:**
- Triangle and arrow clearly distinct when heading ≠ velocity direction
- Demonstrates Epic 002's strafing mechanic effectively
- Ships render correctly at all positions within world bounds
- Stats are readable and properly positioned

**Testing Status:**
- Mock data rendering: ✓ Working
- Multiple heading/velocity scenarios: ✓ Tested
- Color distinction: ✓ Clear
- Coordinate transformation: ✓ Accurate
