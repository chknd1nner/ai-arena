# Epic 005: Advanced Torpedo & Blast Zone System

**Status:** Not Started
**Priority:** P0 (Core Gameplay)
**Estimated Size:** Medium-Large (8 stories, 10-14 hours)
**Target for:** Claude Code Web

---

## Overview

Complete the weapon system by implementing advanced torpedo mechanics with timed detonation and persistent blast zones. This enables the area denial, battlefield shaping, and tactical depth described in the game specification.

## Problem Statement

Currently, torpedoes provide only basic functionality:
- ✅ Torpedoes launch and fly
- ✅ Torpedoes turn using movement commands
- ✅ Torpedoes collide with ships for instant damage
- ❌ No timed detonation (can't create traps or area denial)
- ❌ No blast zones (damage is instant, not persistent)
- ❌ No expansion/persistence/dissipation lifecycle
- ❌ No continuous damage over time
- ❌ Self-damage not enforced (can't hurt yourself with own torpedoes)

**Current torpedo behavior (simplified):**
```python
# Torpedo hits ship → instant damage → torpedo removed
if torpedo.position.distance_to(ship.position) < blast_radius:
    damage = torpedo.ae_remaining * 1.5
    ship.shields -= damage
    torpedoes.remove(torpedo)
```

**Desired behavior (per game spec):**
```python
# Torpedo detonates → creates blast zone → zone persists → continuous damage
if torpedo.detonate_timer <= 0:
    blast_zone = BlastZone(
        position=torpedo.position,
        base_damage=torpedo.ae_remaining * 1.5,
        lifecycle_phase="expansion",
        age=0.0,
        current_radius=0.0
    )
    blast_zones.append(blast_zone)
    torpedoes.remove(torpedo)

# Each substep: update blast zones
for zone in blast_zones:
    zone.update(dt=0.1)  # Expand, persist, or dissipate
    for ship in [ship_a, ship_b]:
        if ship.position.distance_to(zone.position) < zone.current_radius:
            damage_per_second = zone.base_damage / 15.0
            ship.shields -= damage_per_second * dt
```

## Goals

1. **Timed Detonation**: LLMs can specify `detonate_after:X` seconds (0.0-15.0s range)
2. **Blast Zone Lifecycle**: 3-phase system (expansion → persistence → dissipation)
3. **Continuous Damage**: Ships take damage while inside blast zones
4. **Self-Damage**: Ships can be damaged by their own torpedoes (tactical risk)
5. **Area Denial**: Blast zones persist for 60 seconds, forcing tactical adjustments
6. **Deterministic Physics**: Same inputs → same outputs (critical for replays)

## Success Criteria

- [ ] Torpedoes support timed detonation commands
- [ ] Blast zones created on torpedo detonation
- [ ] Expansion phase: 0→15 units over 5 seconds (3 units/second)
- [ ] Persistence phase: 60 seconds at full 15-unit radius
- [ ] Dissipation phase: 15→0 units over 5 seconds (3 units/second)
- [ ] Continuous damage applied per substep to ships in zones
- [ ] Self-damage works (ships damaged by own torpedoes)
- [ ] Multiple blast zones can overlap (damage stacks)
- [ ] LLM prompts updated with timed detonation examples
- [ ] Physics remains 100% deterministic
- [ ] All existing tests still pass
- [ ] At least 3 matches demonstrate blast zone tactics

## User Stories

1. [Story 028: Blast Zone Data Models](stories/story-028-blast-zone-data-models.md)
2. [Story 029: Timed Torpedo Detonation](stories/story-029-timed-detonation.md)
3. [Story 030: Blast Zone Expansion Phase](stories/story-030-expansion-phase.md)
4. [Story 031: Blast Zone Persistence System](stories/story-031-persistence-system.md)
5. [Story 032: Blast Zone Dissipation Phase](stories/story-032-dissipation-phase.md)
6. [Story 033: Continuous Blast Damage](stories/story-033-continuous-damage.md)
7. [Story 034: Self-Damage Implementation](stories/story-034-self-damage.md)
8. [Story 035: Blast Zone Integration & Balance](stories/story-035-integration-balance.md)

## Technical Approach

### Game Specification Reference

From `docs/game_spec_revised.md`:

**Blast Zone Lifecycle (lines 351-376):**
- **Expansion:** 5.0 seconds, 0 → 15 units radius, 3.0 units/second growth
- **Persistence:** 60.0 seconds at full radius
- **Dissipation:** 5.0 seconds, 15 → 0 units radius, 3.0 units/second shrink
- **Total lifecycle:** 70.0 seconds (5 + 60 + 5)

**Damage Model (lines 377-387):**
- Base damage = (Torpedo AE at detonation) × 1.5
- Damage rate = Base damage ÷ 15.0 = damage per second in zone
- Example: 30 AE torpedo → 45 base damage → 3.0 damage/second
- Ship in zone for 2.3 seconds → 2.3 × 3.0 = 6.9 damage

**Timed Detonation (lines 310-319):**
- Format: `{"torpedo_id": "torp_1", "action": "detonate_after", "delay": 5.2}`
- Delay range: 0.0 to 15.0 seconds (within current decision interval)
- Torpedo continues trajectory until detonation time
- Enables precise timing: "Detonate at t=8.0s to catch opponent mid-maneuver"

### Architecture Changes

#### New Data Model: BlastZone

```python
from enum import Enum

class BlastZonePhase(Enum):
    EXPANSION = "expansion"
    PERSISTENCE = "persistence"
    DISSIPATION = "dissipation"

@dataclass
class BlastZone:
    """Persistent area of damage from torpedo detonation."""
    id: str                          # "ship_a_torp_5_blast"
    position: Vec2D                  # Center of blast (fixed)
    base_damage: float               # (Torpedo AE) × 1.5
    phase: BlastZonePhase           # Current lifecycle phase
    age: float                       # Seconds since creation
    current_radius: float            # 0.0 → 15.0 → 15.0 → 0.0
    owner: str                       # "ship_a" or "ship_b" (for tracking)

    # Lifecycle timing constants (from config)
    expansion_duration: float = 5.0
    persistence_duration: float = 60.0
    dissipation_duration: float = 5.0
    max_radius: float = 15.0
```

#### Updated GameState

```python
@dataclass
class GameState:
    turn: int
    ship_a: ShipState
    ship_b: ShipState
    torpedoes: List[TorpedoState]
    blast_zones: List[BlastZone] = field(default_factory=list)  # NEW
```

#### Updated TorpedoState

```python
@dataclass
class TorpedoState:
    # ... existing fields ...
    detonation_timer: Optional[float] = None  # NEW: Seconds until detonation
```

#### Updated Orders (Torpedo Actions)

```python
# Current format:
{"torpedo_id": "ship_a_torp_1", "action": "hard_left"}

# New timed detonation format:
{"torpedo_id": "ship_a_torp_1", "action": "detonate_after:8.5"}
# Parsed as: action="detonate_after", delay=8.5 seconds
```

### Physics Engine Changes

**New Methods:**

```python
class PhysicsEngine:

    def _update_blast_zones(self, blast_zones: List[BlastZone], dt: float):
        """Update all blast zones per substep (lifecycle + radius)."""
        zones_to_remove = []
        for zone in blast_zones:
            zone.age += dt

            if zone.phase == BlastZonePhase.EXPANSION:
                # Grow radius: 0 → 15 over 5 seconds
                growth_rate = zone.max_radius / zone.expansion_duration
                zone.current_radius += growth_rate * dt
                if zone.age >= zone.expansion_duration:
                    zone.phase = BlastZonePhase.PERSISTENCE
                    zone.current_radius = zone.max_radius

            elif zone.phase == BlastZonePhase.PERSISTENCE:
                # Maintain full radius for 60 seconds
                if zone.age >= zone.expansion_duration + zone.persistence_duration:
                    zone.phase = BlastZonePhase.DISSIPATION

            elif zone.phase == BlastZonePhase.DISSIPATION:
                # Shrink radius: 15 → 0 over 5 seconds
                shrink_rate = zone.max_radius / zone.dissipation_duration
                zone.current_radius -= shrink_rate * dt
                zone.current_radius = max(0.0, zone.current_radius)
                if zone.current_radius <= 0.0:
                    zones_to_remove.append(zone)

        for zone in zones_to_remove:
            blast_zones.remove(zone)

    def _apply_blast_damage(self, state: GameState, dt: float) -> List[Event]:
        """Apply continuous damage to ships in blast zones."""
        events = []
        for zone in state.blast_zones:
            damage_per_second = zone.base_damage / 15.0
            damage_this_substep = damage_per_second * dt

            for ship_id, ship in [("ship_a", state.ship_a), ("ship_b", state.ship_b)]:
                distance = ship.position.distance_to(zone.position)
                if distance < zone.current_radius:
                    ship.shields -= damage_this_substep
                    events.append(Event(
                        type="blast_damage",
                        turn=state.turn,
                        data={
                            "ship": ship_id,
                            "blast_zone_id": zone.id,
                            "damage": damage_this_substep,
                            "zone_phase": zone.phase.value
                        }
                    ))
        return events

    def _handle_torpedo_detonations(self, torpedoes: List[TorpedoState],
                                    blast_zones: List[BlastZone], dt: float):
        """Check for timed detonations and create blast zones."""
        torpedoes_to_detonate = []

        for torpedo in torpedoes:
            # Decrement detonation timer if set
            if torpedo.detonation_timer is not None:
                torpedo.detonation_timer -= dt
                if torpedo.detonation_timer <= 0:
                    torpedoes_to_detonate.append(torpedo)

            # Auto-detonate when AE depleted
            elif torpedo.ae_remaining <= 0:
                torpedoes_to_detonate.append(torpedo)

        for torpedo in torpedoes_to_detonate:
            # Create blast zone
            blast_zone = BlastZone(
                id=f"{torpedo.id}_blast",
                position=torpedo.position,
                base_damage=torpedo.ae_remaining * 1.5,
                phase=BlastZonePhase.EXPANSION,
                age=0.0,
                current_radius=0.0,
                owner=torpedo.owner
            )
            blast_zones.append(blast_zone)
            torpedoes.remove(torpedo)
```

**Modified resolve_turn():**

```python
def resolve_turn(self, state: GameState, orders_a: Orders, orders_b: Orders):
    # ... initialization ...

    for substep in range(self.substeps):
        # 1. Update resources (AE, cooldowns)
        self._update_resources(new_state.ship_a, valid_orders_a, dt)
        self._update_resources(new_state.ship_b, valid_orders_b, dt)

        # 2. Update physics
        self._update_ship_physics(new_state.ship_a, valid_orders_a, dt)
        self._update_ship_physics(new_state.ship_b, valid_orders_b, dt)
        for torpedo in new_state.torpedoes:
            self._update_torpedo_physics(torpedo, ..., dt)

        # 3. NEW: Update blast zones (expansion/persistence/dissipation)
        self._update_blast_zones(new_state.blast_zones, dt)

        # 4. NEW: Check for torpedo detonations (timed or AE depleted)
        self._handle_torpedo_detonations(new_state.torpedoes, new_state.blast_zones, dt)

        # 5. Check weapon hits
        phaser_events = self._check_phaser_hits(new_state)
        events.extend(phaser_events)

        # 6. NEW: Apply continuous blast damage
        blast_events = self._apply_blast_damage(new_state, dt)
        events.extend(blast_events)

    return new_state, events
```

### Configuration Changes

**Add to config.json:**

```json
{
  "torpedo": {
    "blast_expansion_seconds": 5.0,
    "blast_persistence_seconds": 60.0,
    "blast_dissipation_seconds": 5.0,
    "blast_radius_units": 15.0,
    "blast_damage_multiplier": 1.5
  }
}
```

### LLM Adapter Changes

**Updated System Prompt:**

```
**TORPEDOES (Controlled Projectiles):**
- Launch Cost: 20 AE. Max 4 active.
- Damage = (AE at detonation) × 1.5. Blast Radius: 15 units.
- Torpedoes fly straight for the first 15s after launch.
- Commands: `straight`, `soft_left`, `hard_right`, etc.

**TIMED DETONATION:**
- Format: `{"torpedo_id": "ship_a_torp_1", "action": "detonate_after:8.5"}`
- Delay range: 0.0 to 15.0 seconds (within current turn)
- Creates blast zone at detonation point
- Blast zone lifecycle:
  - Expansion: 5s (0→15 units radius, 3 units/s)
  - Persistence: 60s (stays at 15 units)
  - Dissipation: 5s (15→0 units, 3 units/s)
- Continuous damage: (Base damage ÷ 15) per second while in zone
- Self-damage: YOUR torpedoes can hurt YOU if you're in the blast
- Tactical uses:
  - Immediate: `detonate_after:0.1` (panic button)
  - Trap: `detonate_after:8.0` (catch opponent mid-turn)
  - Area denial: Create overlapping blast zones to force movement
```

**Updated Observation Format:**

```python
# Add blast zones to state observation
state_description += f"\n**BLAST ZONES:** {len(state.blast_zones)} active\n"
for zone in state.blast_zones:
    state_description += f"  - {zone.id}: "
    state_description += f"Phase={zone.phase.value}, "
    state_description += f"Radius={zone.current_radius:.1f}, "
    state_description += f"Age={zone.age:.1f}s, "
    state_description += f"Damage={(zone.base_damage / 15.0):.1f}/s\n"
```

## Impact on Gameplay

### Tactical Depth

**Before (Instant Damage):**
```
Turn 5: Launch torpedo
Turn 7: Torpedo hits → 30 damage → torpedo removed
Result: One-time damage, no area control
```

**After (Blast Zones):**
```
Turn 5: Launch torpedo with detonate_after:8.0
Turn 6: Torpedo flying, detonates at t=8.0s
Turn 6-10: Blast zone active (70s total)
  - Expansion (5s): Zone grows, ships can escape
  - Persistence (60s): Full 15-unit radius for 4 turns
  - Dissipation (5s): Zone shrinks, final damage window
Result: Area denial, forces opponent movement, multi-turn impact
```

### Strategic Scenarios

**Scenario 1: The Trap**
- Ship A launches 2 torpedoes
- Torpedo 1: `detonate_after:6.0` (behind opponent)
- Torpedo 2: `detonate_after:9.0` (ahead of opponent)
- Result: Creates corridor forcing opponent into predictable path

**Scenario 2: The Retreat Cover**
- Ship A launches torpedo while retreating
- `detonate_after:12.0` between ships
- Result: Creates blast zone that opponent must navigate, buying time

**Scenario 3: The Aggressive Push**
- Ship B launches torpedo at Ship A's position
- `detonate_after:0.5` (nearly instant)
- Result: Forces Ship A to evade or take blast damage + ship damage

**Scenario 4: Self-Damage Gambit**
- Ship A launches torpedo at close range
- `detonate_after:10.0` (delayed to allow escape)
- Ship A must move away before detonation or take self-damage
- Result: High-risk, high-reward area control

## Testing Strategy

### Unit Tests

**Blast Zone Lifecycle:**
- Test expansion: radius grows 3 units/second for 5 seconds
- Test persistence: radius stays at 15 units for 60 seconds
- Test dissipation: radius shrinks 3 units/second for 5 seconds
- Test phase transitions: expansion → persistence → dissipation
- Test removal: zone removed when radius reaches 0

**Timed Detonation:**
- Test detonation timer decrements per substep
- Test torpedo creates blast zone at t=0
- Test delayed detonation (t=5.0s, t=10.0s, t=15.0s)
- Test instant detonation (t=0.1s)
- Test AE-based auto-detonation (timer = None, AE depletes)

**Continuous Damage:**
- Test damage applied per substep
- Test damage rate calculation: base_damage ÷ 15.0
- Test ship fully in zone takes full damage
- Test ship partially in/out of zone (edge cases)
- Test multiple blast zones (damage stacks)

**Self-Damage:**
- Test owner ship takes damage from own blast zones
- Test non-owner ship takes damage normally
- Test both ships in same blast zone

### Integration Tests

**Full Match Scenarios:**
1. **Torpedo Trap Match:** Ship uses timed detonations to create corridors
2. **Self-Damage Risk:** Ship launches close-range torpedo, must escape
3. **Multi-Zone Overlap:** Multiple blast zones active, ships navigate damage
4. **Long Persistence:** Blast zone persists for 4+ turns, forces strategy shift

### Determinism Validation

- Run same match 10 times with identical inputs
- Compare replay JSONs byte-for-byte
- Verify blast zone ages, phases, radii are identical
- Verify damage events occur at same substeps

## Risks & Mitigations

### Risk 1: Breaking Determinism
**Impact:** Critical - Replays won't work
**Mitigation:**
- Strict floating-point operations (same as Epic 004)
- Comprehensive regression tests
- Validate replay reproduction

### Risk 2: Performance Degradation
**Impact:** Medium - Multiple blast zones + continuous damage checks
**Mitigation:**
- Profile before/after
- Spatial partitioning if needed (unlikely for MVP)
- Limit max blast zones (config-driven)

### Risk 3: Balance Issues
**Impact:** Medium - Blast zones could be too strong/weak
**Mitigation:**
- Make all timing/damage configurable
- Story 035 dedicated to balance tuning
- Test with multiple scenarios

### Risk 4: Complexity Overwhelming LLMs
**Impact:** Medium - LLMs might not use timed detonation effectively
**Mitigation:**
- Enhanced system prompts with examples
- Observation format shows active blast zones clearly
- Test with both Claude and GPT-4

## Dependencies

### Required
- Epic 004: Continuous physics system (completed)
- Epic 002: Movement/rotation system (completed)
- Epic 001: Configuration system (completed)

### Enables
- Advanced AI tactics (area denial, trapping)
- Tournament scenarios with blast zone meta-game
- Frontend visualization (expanding circles, danger zones)
- Analytics (blast zone effectiveness, self-damage stats)

## Implementation Phases

### Phase 1: Foundation (Stories 028-029)
- Blast zone data models
- Timed detonation commands
- **Deliverable:** Torpedoes can detonate on timer, create blast zones

### Phase 2: Lifecycle (Stories 030-032)
- Expansion mechanics
- Persistence system
- Dissipation mechanics
- **Deliverable:** Blast zones have full 70-second lifecycle

### Phase 3: Damage (Stories 033-034)
- Continuous damage application
- Self-damage implementation
- **Deliverable:** Ships take damage from blast zones

### Phase 4: Integration (Story 035)
- Full integration testing
- Balance tuning
- LLM prompt updates
- **Deliverable:** Production-ready blast zone system

## Rollout Strategy

1. **Feature Branch:** `feature/torpedo-blast-zones`
2. **Incremental PRs:** One PR per phase (or per story if preferred)
3. **Testing:** Run full test suite after each story
4. **Validation:** Compare matches with/without blast zones
5. **Merge:** Only when all tests pass and determinism verified

## Definition of Done

- [ ] All 8 stories completed
- [ ] Blast zones created on torpedo detonation (timed or auto)
- [ ] Full 70-second lifecycle (expansion → persistence → dissipation)
- [ ] Continuous damage applied per substep
- [ ] Self-damage working (ships hurt by own torpedoes)
- [ ] All tests passing (unit + integration)
- [ ] Determinism validated (byte-identical replays)
- [ ] At least 3 full matches with blast zone tactics
- [ ] LLM prompts updated with timed detonation examples
- [ ] Balance tuning complete
- [ ] Documentation updated
- [ ] Merged to main

## Files to Create/Modify

### Create
- `tests/test_blast_zones.py` - Blast zone lifecycle tests
- `tests/test_timed_detonation.py` - Detonation timer tests
- `tests/test_blast_damage.py` - Continuous damage tests
- `tests/test_self_damage.py` - Self-damage tests

### Modify
- `ai_arena/game_engine/data_models.py` - Add BlastZone, BlastZonePhase
- `ai_arena/game_engine/physics.py` - Add blast zone mechanics
- `ai_arena/llm_adapter/adapter.py` - Update prompts, observations
- `ai_arena/config/loader.py` - Validate blast zone config
- `config.json` - Add blast zone parameters
- Existing physics tests - Update for blast zones

## Success Metrics

**Technical:**
- 100% test coverage for blast zone mechanics
- Deterministic physics maintained
- Performance: <5% overhead from blast zones

**Gameplay:**
- LLMs successfully use timed detonation
- Blast zones demonstrably affect tactics
- Multiple viable blast zone strategies emerge

**Balance:**
- Blast zones powerful but not overwhelming
- Self-damage risk is meaningful
- Matches remain 14-20 turns average

## Notes

**Why This Epic Matters:**
- Completes core weapon system from game spec
- Unlocks "area denial" and "battlefield shaping" gameplay
- Creates multi-turn strategic depth (not just instant damage)
- Enables advanced tactics (trapping, herding, zoning)
- Self-damage adds risk/reward decision-making

**Post-Epic 005 Roadmap:**
- Epic 006: Frontend Polish & Thinking Tokens (visualization)
- Epic 007: Tournament & Match Infrastructure (scaling)
- Epic 008: Live Match Streaming (WebSocket, real-time)

---

**Epic 005 Ready for Implementation** 🚀
