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

[Dev Agent: Fill in this section when implementation is complete]

**Completed:** [Date]
**Agent:** [Your name]
**Commit:** [Commit hash]

### Implementation Notes

[Describe what was implemented, key technical decisions, files created/modified, testing results]

**Files Created:**
- [List new files]

**Files Modified:**
- [List modified files]

**Implementation Details:**
1. [Detail 1]
2. [Detail 2]
3. [etc.]

**Key Technical Decisions:**
- [Decision 1 and rationale]
- [Decision 2 and rationale]

**Testing Status:**
- [Test 1]: ✓/✗
- [Test 2]: ✓/✗

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
