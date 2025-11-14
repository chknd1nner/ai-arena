# Story 016: Weapon Visualization

**Epic:** [Epic 003: Canvas-Based Match Replay Viewer](../epic-003-canvas-replay-viewer.md)
**Status:** Ready for Dev
**Size:** Medium (~2 hours)
**Priority:** P1

---

## User Story

**As a** player
**I want** to see phaser arcs and torpedo trajectories
**So that** I can understand weapon ranges and firing patterns

## Acceptance Criteria

- [ ] Phaser arcs render (WIDE = 90°, FOCUSED = 10°)
- [ ] Phaser arcs shown in correct direction (ship heading)
- [ ] Phaser firing events trigger visual effect
- [ ] Torpedoes render as circles
- [ ] Torpedo motion trails visible
- [ ] Torpedo explosions shown on blast events

## Technical Approach

**Phaser Arc Rendering:**
```javascript
function renderPhaserArc(ctx, ship, config, canvasSize, worldBounds) {
  const pos = worldToScreen(ship.position, canvasSize, worldBounds);
  const scale = getScale(canvasSize, worldBounds);

  const arcAngle = config === 'WIDE' ? Math.PI / 2 : Math.PI / 18; // 90° or 10°
  const range = config === 'WIDE' ? 30 : 50;

  ctx.save();
  ctx.globalAlpha = 0.2;
  ctx.fillStyle = '#00ff00';
  ctx.beginPath();
  ctx.moveTo(pos.x, pos.y);
  ctx.arc(
    pos.x, pos.y,
    range * scale,
    -ship.heading - arcAngle / 2,
    -ship.heading + arcAngle / 2
  );
  ctx.closePath();
  ctx.fill();
  ctx.restore();
}
```

**Torpedo Rendering:**
```javascript
function renderTorpedo(ctx, torpedo, canvasSize, worldBounds) {
  const pos = worldToScreen(torpedo.position, canvasSize, worldBounds);

  const color = torpedo.owner === 'a' ? '#4A90E2' : '#E24A4A';

  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.arc(pos.x, pos.y, 6, 0, Math.PI * 2);
  ctx.fill();

  ctx.strokeStyle = '#fff';
  ctx.lineWidth = 2;
  ctx.stroke();
}
```

## Files to Modify

- Create: `frontend/src/utils/weaponRenderer.js`
- Modify: `frontend/src/components/CanvasRenderer.jsx`

## Dependencies

- **Requires:** Story 014 (replay data with weapon events)

---

## Dev Agent Record

**Completed:** 2025-11-14
**Agent:** Claude (Dev Agent)
**Commit:** 95190d7f0dc94b3a577d63a537005c5fd8728309

### Implementation Notes

Implemented comprehensive weapon visualization system for the canvas-based replay viewer, including phaser arcs, torpedoes with motion trails, and blast zones.

**Files Created:**
- `frontend/src/utils/weaponRenderer.js` - Complete weapon rendering utilities

**Files Modified:**
- `frontend/src/components/CanvasRenderer.jsx` - Integrated weapon rendering into canvas rendering pipeline

**Implementation Details:**
1. **Weapon Renderer Utilities** (`weaponRenderer.js`):
   - `renderPhaserArc()`: Renders semi-transparent firing arcs (WIDE = 90°, FOCUSED = 10°)
   - `renderPhaserFiring()`: Renders phaser beam effects during firing events
   - `renderTorpedo()`: Renders torpedoes as colored circles with owner identification
   - `renderTorpedoTrail()`: Renders fading motion trails for torpedoes
   - `renderExplosion()`: Renders expanding explosion effects
   - `renderBlastZone()`: Renders persistent blast zones with gradient danger areas

2. **Canvas Integration** (`CanvasRenderer.jsx`):
   - Added torpedo trail tracking using `useRef` to maintain position history
   - Implemented layered rendering: blast zones → phaser arcs → ships → torpedoes
   - Integrated weapon rendering into `renderFrame()` callback
   - Added phaser_config to mock ship data for testing
   - Implemented trail cleanup for destroyed torpedoes

3. **Rendering Order**:
   - Blast zones rendered first (background danger zones)
   - Phaser arcs rendered semi-transparently before ships
   - Ships rendered in middle layer
   - Torpedoes and trails rendered on top for visibility

**Key Technical Decisions:**
- **Coordinate System**: Used worldToScreen() and getScale() consistently for all weapon rendering to ensure proper positioning and scaling
- **Heading Conversion**: Canvas Y-axis is inverted, so ship heading is negated when drawing arcs: `-ship.heading`
- **Trail Implementation**: Used ref-based trail tracking instead of state to avoid unnecessary re-renders and maintain smooth performance
- **Color Coding**: Ships A (blue #4A90E2) and B (red #E24A4A) consistently color-coded across all weapon visualizations
- **Layering**: Weapons rendered in specific order to ensure proper visual hierarchy without obscuring important elements

**Testing Status:**
- Phaser arc rendering (WIDE 90°, FOCUSED 10°): ✓ (Code review confirmed)
- Phaser arc direction (follows ship heading): ✓ (Code review confirmed)
- Torpedo rendering as circles: ✓ (Code review confirmed)
- Torpedo trails with fade effect: ✓ (Code review confirmed)
- Blast zone rendering with gradients: ✓ (Code review confirmed)
- Coordinate transformations: ✓ (Code review confirmed)

**Note**: Integration testing with live replays recommended for QA validation

---

## QA Agent Record

[QA Agent: Fill in this section after reviewing the implementation]

**Reviewed:** [Date]
**QA Agent:** [Your name]
**Branch:** [Branch name]
**Result:** ✅ PASS / ⚠️ PASS with recommendations / ❌ FAIL - Remediation needed

### Automated Testing Results

[Describe automated tests run and results]

### Acceptance Criteria Validation

- [ ] Phaser arcs render (WIDE = 90°, FOCUSED = 10°)
- [ ] Phaser arcs shown in correct direction (ship heading)
- [ ] Phaser firing events trigger visual effect
- [ ] Torpedoes render as circles
- [ ] Torpedo motion trails visible
- [ ] Torpedo explosions shown on blast events

### Issues Found

[List any issues discovered during QA]

**Critical Issues:**
- [None or list]

**Minor Issues:**
- [None or list]

**Recommendations:**
- [Suggestions for improvement]

### Final Assessment

[Summary of QA findings and final pass/fail decision. If PASS with recommendations, list them. If FAIL, specify what needs remediation and update story status to "Remediation needed"]
