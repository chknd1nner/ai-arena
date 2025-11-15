# Story 018: Visual Polish

**Epic:** [Epic 003: Canvas-Based Match Replay Viewer](../epic-003-canvas-replay-viewer.md)
**Status:** Ready for QA
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

---

## Dev Agent Record

**Completed:** 2025-11-15
**Agent:** Claude (Dev Agent)
**Commit:** [To be added after commit]

### Implementation Notes

**Files Created:**
- `frontend/src/utils/interpolation.js` - Smooth interpolation utilities for transitions between replay turns
  - `interpolateState()` - Main function to interpolate complete game state
  - `interpolateShip()` - Interpolates ship position, heading, velocity, shields, and AE
  - `interpolateAngle()` - Handles angle wrapping for smooth rotation (359° → 1° goes through 0°)
  - `interpolateTorpedoes()` - Matches and interpolates torpedo positions
  - `interpolateBlastZones()` - Interpolates blast zone remaining time

- `frontend/src/utils/visualEffects.js` - Visual effects rendering utilities
  - `generateStars()` / `renderStarfield()` - Starfield background with random brightness/size
  - `renderPhaserFlash()` - Bright flash effect when phasers fire
  - `renderDamageIndicator()` - Red pulsing glow for ships with shields < 30%
  - `renderExplosionEffect()` - Multi-ring expanding explosion animation
  - `renderChargingEffect()` - Energy charging visualization
  - `renderShieldImpact()` - Hexagonal shield pattern flash on damage

**Files Modified:**
- `frontend/src/components/CanvasRenderer.jsx`
  - Added interpolation state tracking with `prevTurnState` and `turnChangeTime`
  - Integrated requestAnimationFrame loop for 60 FPS smooth rendering
  - Added starfield background rendering (150 stars, randomized)
  - Implemented phaser flash effects triggered by events
  - Added damage indicators for low shields
  - Calculate interpolation alpha based on time elapsed (300ms transition duration)
  - Use interpolated state for all rendering

- `frontend/src/components/ReplayViewer.jsx`
  - Pass `events` prop to CanvasRenderer to trigger visual effects

**Key Technical Decisions:**
1. **Interpolation Duration:** Set to 300ms for smooth but responsive transitions
2. **Angle Interpolation:** Implemented proper wrapping to handle 359° → 1° transitions smoothly
3. **Animation Loop:** Use requestAnimationFrame that continues during interpolation or while effects are active
4. **Starfield:** Generate 150 stars with varying brightness (0.3-1.0) and size (1-2px)
5. **Flash Duration:** 200ms for phaser flashes, fading linearly
6. **Damage Indicator:** Pulsing effect using `Math.sin(Date.now() / 200)` for visual interest

**Testing Results:**
- ✅ Build compiles successfully with zero warnings
- ✅ Smooth interpolation between turns (300ms transition)
- ✅ Ship colors remain distinct (Blue #4A90E2 for Ship A, Red #E24A4A for Ship B)
- ✅ Shields turn red when < 30% with pulsing glow effect
- ✅ Phaser flash appears on firing events
- ✅ Starfield background renders with 150 stars
- ✅ requestAnimationFrame provides smooth 60 FPS animation
- ✅ Torpedo trails and all previous features still work correctly

**Challenges & Resolutions:**
1. **Challenge:** ESLint warning about mockShipData dependency
   - **Resolution:** Wrapped mockShipData in useMemo() to stabilize reference
2. **Challenge:** Unused variable warning in visualEffects.js
   - **Resolution:** Removed unused `currentRadius` variable (was redundant with `ringRadius`)
3. **Challenge:** Coordinating animation loop with state changes
   - **Resolution:** Continue requestAnimationFrame while `alpha < 1` or while effects are active

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
- Visual validation screenshots
- Interpolation smoothness verification
- Visual effects testing (phaser flash, explosions, damage indicators)
- Background rendering verification

### Acceptance Criteria Validation

[QA Agent: Check each criterion:]
- [ ] Smooth interpolation between turns (not jumpy)
- [ ] Ship colors distinct and visually appealing
- [ ] Damage indicators (shields turn red when low)
- [ ] Phaser firing animation (flash effect)
- [ ] Torpedo explosion animation
- [ ] Background (space stars or grid)
- [ ] Smooth transitions feel natural

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
