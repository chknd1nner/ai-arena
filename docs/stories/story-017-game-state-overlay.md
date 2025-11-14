# Story 017: Game State Overlay

**Epic:** [Epic 003: Canvas-Based Match Replay Viewer](../epic-003-canvas-replay-viewer.md)
**Status:** Ready for Dev
**Size:** Small (~1 hour)
**Priority:** P2

---

## User Story

**As a** player
**I want** to see shields, AE, and turn information overlaid on the canvas
**So that** I can understand the game state while watching matches

## Acceptance Criteria

- [ ] Ship shields displayed near each ship
- [ ] Ship AE displayed near each ship
- [ ] Turn number and phase shown
- [ ] Event log (recent hits, launches) visible
- [ ] Match info (models, winner) displayed
- [ ] Overlay doesn't obscure important action

## Technical Approach

Add overlay component that renders over canvas or beside it:

```jsx
// frontend/src/components/StateOverlay.jsx
const StateOverlay = ({ turnState, turnNumber, maxTurns, events }) => {
  return (
    <div style={{ marginTop: '10px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-around' }}>
        <ShipStats ship={turnState.ship_a} label="Ship A" color="#4A90E2" />
        <div>
          <strong>Turn {turnNumber + 1} / {maxTurns}</strong>
        </div>
        <ShipStats ship={turnState.ship_b} label="Ship B" color="#E24A4A" />
      </div>

      {events.length > 0 && (
        <div style={{ marginTop: '10px' }}>
          <strong>Events:</strong>
          <ul>
            {events.map((event, idx) => (
              <li key={idx}>{formatEvent(event)}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

const ShipStats = ({ ship, label, color }) => (
  <div style={{ borderLeft: `4px solid ${color}`, paddingLeft: '10px' }}>
    <strong>{label}</strong>
    <div>Shields: {ship.shields}%</div>
    <div>AE: {ship.ae.toFixed(0)}</div>
    <div>Config: {ship.phaser_config}</div>
  </div>
);
```

## Files to Create

- Create: `frontend/src/components/StateOverlay.jsx`
- Modify: `frontend/src/components/ReplayViewer.jsx`

## Dependencies

- **Requires:** Story 014 (replay data)

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

- [ ] Ship shields displayed near each ship
- [ ] Ship AE displayed near each ship
- [ ] Turn number and phase shown
- [ ] Event log (recent hits, launches) visible
- [ ] Match info (models, winner) displayed
- [ ] Overlay doesn't obscure important action

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
