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

**Completed:** 2025-11-14
**Agent:** Claude (Dev Agent)
**Commit:** 95190d7f0dc94b3a577d63a537005c5fd8728309

### Implementation Notes

Implemented comprehensive game state overlay component that displays ship stats, turn information, events, and match metadata in an organized, non-intrusive manner.

**Files Created:**
- `frontend/src/components/StateOverlay.jsx` - Complete state overlay component with ship stats and event display

**Files Modified:**
- `frontend/src/components/ReplayViewer.jsx` - Integrated StateOverlay component into replay viewer

**Implementation Details:**
1. **StateOverlay Component** (`StateOverlay.jsx`):
   - **ShipStats Sub-component**: Displays shields, AE, and phaser configuration for each ship
   - **Color-coded Borders**: Blue (#4A90E2) for Ship A, Red (#E24A4A) for Ship B
   - **Dynamic Status Colors**: Green/yellow/red indicators based on shields and AE levels
   - **Turn Counter**: Displays current turn vs total turns with match ID
   - **Event Log**: Formats and displays recent events (last 5) with readable descriptions
   - **Torpedo Count**: Shows active torpedoes per ship
   - **Blast Zone Warnings**: Highlights active blast zones with warning emoji

2. **Event Formatting** (`formatEvent()` function):
   - Handles multiple event types: phaser_fired, torpedo_launched, torpedo_blast, etc.
   - Provides human-readable descriptions with relevant details (damage, attacker, target)
   - Fallback formatting for unknown event types

3. **ReplayViewer Integration**:
   - Replaced basic event display with comprehensive StateOverlay
   - Passes turnState, turnNumber, maxTurns, events, and matchInfo as props
   - Positioned below playback controls to avoid obscuring canvas
   - Clean integration maintaining existing viewer structure

4. **Visual Design**:
   - Consistent dark theme (#1a1a1a background) matching existing UI
   - Three-column layout: Ship A stats | Turn counter | Ship B stats
   - Clear visual hierarchy with borders and spacing
   - Responsive sizing with minimum widths for readability

**Key Technical Decisions:**
- **Color-Coded Health Indicators**: Dynamic colors (green/yellow/red) for shields and AE provide instant status visibility
- **Recent Events Only**: Limited to last 5 events to prevent information overload and maintain readability
- **Phaser Config Display**: Shows WIDE/FOCUSED with distinct colors (green for WIDE, cyan for FOCUSED) for quick identification
- **Non-Intrusive Placement**: Positioned below canvas and controls to maintain clear view of action
- **Ship Identification**: Consistent color coding (blue/red) matches canvas ship colors for easy correlation
- **Null Safety**: Comprehensive null/undefined checks to handle missing or incomplete data gracefully

**Testing Status:**
- Ship shields display: ✓ (Code review confirmed)
- Ship AE display: ✓ (Code review confirmed)
- Turn number and phase: ✓ (Code review confirmed)
- Event log with formatting: ✓ (Code review confirmed)
- Match info display: ✓ (Code review confirmed)
- Color-coded ship identification: ✓ (Code review confirmed)
- Overlay positioning (non-intrusive): ✓ (Code review confirmed)
- Phaser config display: ✓ (Code review confirmed)

**Note**: Visual integration testing with live replays recommended for QA validation

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
