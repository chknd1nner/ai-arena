# AI Arena: 1v1 Space Duel - Game Specification (Revised)

## Executive Summary

**AI Arena** is an entertaining AI benchmark where two large language models (LLMs) pilot individual starships in simultaneous real-time duels. The game combines continuous physics simulation with periodic decision points, creating emergent moments where AI reasoning and prediction both matter. Spectators watch the full battlefield, both models' thinking tokens, and the consequences of tactical predictions that succeed or fail.

This is a homage to the 1974 classic *Spasim* (Space Sim), reimagined as competitive AI theater rather than a traditional player-vs-player game.

---

## Vision & Entertainment Value

### What Makes It Compelling

1. **Transparent Reasoning** — Spectators see both models' thinking tokens displayed side-by-side, exposing different prediction strategies and moments of miscalculation
2. **Simultaneous Commitment** — Both players commit to orders simultaneously with imperfect information, creating genuine uncertainty and drama
3. **Emergent Narrative** — Each match tells a story: positioning games, desperate gambles, tactical victories born from reading opponent psychology
4. **Reproducibility** — Matches aren't predetermined. Same scenario played twice yields completely different outcomes due to model non-determinism
5. **Accessible Complexity** — Discrete choices (movement library, phaser configs) make decisions understandable to spectators despite deep tactical depth
6. **Cinematic Moments** — Slow-expanding blast zones, desperate evasions, and real-time physics create naturally dramatic sequences

### Target Audience

- Casual AI enthusiasts interested in emergent behavior
- Content creators seeking novel, watchable AI competition
- Researchers interested in AI decision-making under uncertainty
- Twitch/YouTube streamers looking for entertaining, novel content

---

## Core Gameplay

### Match Structure

**Setup:**
- Two LLMs (user-provided API keys)
- Each controls one starship
- Ships start at opposite sides of arena
- Arena is 2D plane, unbounded (or large bounded arena)
- Both ships visible to both players and spectators at all times

**Combat Philosophy:**
- **One continuous game** — No separate "phases" with different rule sets
- **Range determines strategy** — Weapon effectiveness naturally shapes tactics:
  - Torpedoes dominate at long range (100+ units)
  - Both weapons viable at medium range (50-100 units)
  - Phasers dominate at close range (<50 units)
  - Torpedoes become dangerous to user at close range (self-damage risk)

**Match Flow:**
```
Initialize ships → Decision Phase → Action Phase (15s real-time) → Decision Phase → Action Phase → ... → Victory
```

### The Core Loop

**Real-Time Simulation with Periodic Decisions:**

The game is a **continuous real-time physics simulation**. Every 15.0 seconds, the simulation pauses to accept new orders from both AIs, then resumes.

**Each cycle:**
1. **Decision Phase (PAUSED)** — Models simultaneously issue new orders:
   - Ship movement selection
   - Weapon configuration changes
   - Torpedo commands (launch, movement, or timed detonation)
   
2. **Action Phase (15.0 seconds real-time)** — Physics simulation runs:
   - Ships execute movement commands continuously
   - Phasers fire automatically when targets cross firing arcs
   - Torpedoes fly and execute their commands
   - Blast zones expand, persist, and dissipate
   - Collisions and damage resolved continuously
   
3. **State Update** — Current state becomes starting state for next decision phase

**Win Conditions:**
- First ship reduced to 0 shields = match over, opponent wins
- Both ships destroyed simultaneously = tie (rare edge case)

---

## Game Mechanics

### Real-Time Physics System

**Critical Design Principle:** Everything operates in **continuous real-time**. There are no "turn-based" mechanics. All durations, speeds, and rates are expressed in **seconds** with **float precision** (e.g., 3.7 seconds, 145.83 units).

**Simulation Parameters:**
- **Decision interval:** 15.0 seconds
- **Physics tick rate:** 0.1 seconds (150 ticks per decision interval)
- **All positions:** Float coordinates (x, y)
- **All headings:** Float degrees (0° = East, counterclockwise)
- **All speeds:** Float units per second

---

### Movement System

**Core Innovation:** Movement direction and ship facing are **independent orders**. This "face move" system (inspired by *Starships Unlimited*) creates rich tactical positioning.

#### Movement Direction Library

Ships choose a movement direction from 8 cardinal directions, depicted as ASCII arrows:

**Available Movement Directions:**

```
    ↑        ↗
    N        NE
    
←  ---  →   ---  ↘
W   0   E        SE
    
    ↓        ↙
    S        SW
```

| Direction | ASCII | Description | AE/Second | Total (15s) |
|-----------|-------|-------------|-----------|-------------|
| Forward | `↑` | Continue current heading | 0.33 AE/s | 5.0 AE |
| Forward-Left | `↖` | 45° left arc | 0.53 AE/s | 8.0 AE |
| Forward-Right | `↗` | 45° right arc | 0.53 AE/s | 8.0 AE |
| Left | `←` | 90° left arc | 0.67 AE/s | 10.0 AE |
| Right | `→` | 90° right arc | 0.67 AE/s | 10.0 AE |
| Backward | `↓` | Reverse direction | 0.67 AE/s | 10.0 AE |
| Backward-Left | `↙` | Reverse + 45° left | 0.80 AE/s | 12.0 AE |
| Backward-Right | `↘` | Reverse + 45° right | 0.80 AE/s | 12.0 AE |
| Stop | `---` | Coast to halt | 0.0 AE/s | 0.0 AE |

**Movement Resolution:**
- Movement executes **continuously** over 15 seconds
- Ships trace smooth arcs based on direction chosen
- Path is **deterministic** given starting position and chosen direction
- Both players can calculate exact endpoint (enables prediction gameplay)

**Visual Representation:**
- UI shows ASCII arrow in movement menu (like *Starships Unlimited*)
- Preview arc displayed in white before commitment
- Spectators see contrail showing actual path taken

#### Rotation (Facing) System

Ships can rotate their facing **independently** of movement direction. This is the "face move" capability.

**Rotation Commands:**

| Rotation | Description | Degrees/Second | Total Turn (15s) | AE/Second | Total (15s) |
|----------|-------------|----------------|------------------|-----------|-------------|
| None | Maintain current heading | 0.0°/s | 0° | 0.0 AE/s | 0.0 AE |
| Soft Left | Gentle left rotation | 1.0°/s | 15° | 0.13 AE/s | 2.0 AE |
| Soft Right | Gentle right rotation | 1.0°/s | 15° | 0.13 AE/s | 2.0 AE |
| Hard Left | Aggressive left rotation | 3.0°/s | 45° | 0.33 AE/s | 5.0 AE |
| Hard Right | Aggressive right rotation | 3.0°/s | 45° | 0.33 AE/s | 5.0 AE |

**Rotation Resolution:**
- Rotation executes **continuously** and **simultaneously** with movement
- Ship's facing changes smoothly over 15 seconds
- Rotation is **independent** of movement arc
- Phasers always point in facing direction (not movement direction)

**Critical Tactical Implications:**

This independence creates powerful maneuvers:

**Example 1: Strafing Run**
- Movement: `→` (Right - 90° arc)
- Rotation: Hard Left (45° turn to face backward)
- Result: Ship circles right while keeping guns pointed at original bearing
- Use case: Maintain phaser lock while evading

**Example 2: Retreat with Coverage**
- Movement: `↓` (Backward - reverse)
- Rotation: None (keep facing forward)
- Result: Ship backs away while keeping phasers pointed at opponent
- Use case: Defensive withdrawal under fire

**Example 3: Aggressive Reposition**
- Movement: `↑` (Forward - straight ahead)
- Rotation: Hard Right (45° turn)
- Result: Ship advances in original direction while angling right
- Use case: Close distance while preparing broadside angle

**Example 4: The "Drift"**
- Movement: `←` (Left - 90° arc)
- Rotation: Soft Left (15° turn)
- Result: Ship slides left on wide arc while slowly rotating to track target
- Use case: Evasion while maintaining partial firing solution

**Combined AE Cost:**
- Total AE burn = Movement cost + Rotation cost
- Example: Forward `↑` (0.33 AE/s) + Hard Left rotation (0.33 AE/s) = **0.66 AE/s total**
- Net burn after regen: 0.66 - 0.33 (regen) = **0.33 AE/s net drain**

**Starting Values (TBD - requires playtesting):**
- Ship speed: 3.0 units/second (linear)
- Turn rates: As specified in rotation table
- Movement arcs: Smooth curves, deterministic geometry

---

### Phaser System (Primary Close-Range Weapon)

Phasers are energy weapons fixed to the ship's forward-facing cone. They fire **automatically** whenever a target crosses into the firing arc during the action phase.

#### Phaser Configurations

Ships can toggle between two phaser modes:

**WIDE Configuration:**
- Arc spread: ±45° from ship heading = 90° total cone
- Range: 30.0 units
- Damage per hit: 15.0 shield damage
- Hit probability: High (large target area)
- Cooldown: 3.5 seconds (TBD - requires playtesting)
- Strategy: Spray and pray, easier to connect but less damage

**FOCUSED Configuration:**
- Arc spread: ±5° from ship heading = 10° total cone
- Range: 50.0 units
- Damage per hit: 35.0 shield damage
- Hit probability: Low (narrow beam, must predict accurately)
- Cooldown: 3.5 seconds (TBD - requires playtesting)
- Strategy: Precision strikes, high risk/high reward

#### Phaser Mechanics

**1. Configuration Changes Cost Time:**
- Switching from WIDE ↔ FOCUSED costs 15.0 seconds (one full decision interval)
- Ship cannot fire during reconfiguration period
- Only movement + reconfiguration action allowed during that interval

**2. Firing is Automatic and Continuous:**
- No manual "fire/don't fire" decision
- Phaser fires whenever enemy ship **crosses into** the firing arc
- Each arc crossing = one hit (full damage)
- Cooldown timer prevents rapid-fire: after firing, phaser must wait X seconds before firing again
- **Multiple hits possible:** If a ship crosses the arc, leaves, and re-enters within 15 seconds, it gets hit multiple times (limited by cooldown)

**3. Continuous Arc Monitoring:**
- During the 15-second action phase, physics engine checks arc intersection every 0.1 seconds
- When opponent enters arc AND cooldown expired → fire immediately
- Example scenario:
  - t=0.0s: Ship A enters Ship B's arc → **HIT 1** (35 damage)
  - t=0.1s to t=3.5s: Ship A still in arc, but cooldown active (no additional hits)
  - t=3.5s: Cooldown expires
  - t=3.6s: Ship A still in arc → **HIT 2** (35 damage)
  - t=5.0s: Ship A exits arc
  - Result: 70 damage total from prolonged exposure

**4. No Manual Aiming:**
- Phaser points wherever ship is pointing
- To aim at a target, model must predict where target will be AND position ship accordingly
- This makes movement prediction the core skill

#### Combat Range Effectiveness

| Zone | Distance | Weapon Effectiveness | Strategic Notes |
|------|----------|---------------------|-----------------|
| Long Range | 100+ units | Torpedoes only | Phasers cannot reach |
| Medium Range | 50-100 units | Torpedoes primary, FOCUSED phasers viable | Transition zone, positioning critical |
| Close Range | 30-50 units | Both phasers effective, torpedoes risky | High-stakes maneuvering |
| Point-Blank | <30 units | Phasers deadly, torpedoes suicidal | Self-damage risk dominates |

---

### Torpedo System

Torpedoes are projectiles launched by ships to control positioning, create area denial, and damage opponents at range. Unlike phasers, torpedoes are **independently controlled entities** with their own movement orders each decision phase.

#### Torpedo Properties

- **Launch Cost:** 20.0 AE (immediate cost from launching ship)
- **Max AE Capacity:** 40.0 AE (loaded at launch, determines range/maneuverability/detonation damage)
- **AE Burn Rate:** ~0.5 AE/second while maneuvering (TBD - requires playtesting)
- **Speed:** 4.0 units/second (TBD - faster than ships)
- **Turn Rate:** 3.0°/second (TBD - wider turning radius than ships)
- **Max Active:** 4 torpedoes per ship (prevents spam)
- **Blast Radius:** 15.0 units from detonation point
- **Damage Formula:** (AE remaining at detonation) × 1.5 = shield damage to any ship in blast radius
- **Self-Damage:** YES - ships can be damaged by their own torpedoes

**Example:** Torpedo detonates with 20.0 AE remaining = 30.0 shield damage to any ship within 15.0-unit radius (including the launching ship)

#### Torpedo Launch Timing

**When ordered to launch:**
- Command issued during decision phase (game paused)
- Torpedo spawns at ship's current position/heading when action phase begins (t=0.0s)
- **First segment constraint:** Torpedo cannot turn during its first decision interval
  - It flies straight for 15 seconds
  - On the next decision phase, it becomes fully controllable
  - This prevents instant "fire and forget" homing torpedoes
  - Adds strategic depth: must predict where enemy will be 15+ seconds ahead

#### Torpedo Control

Each decision phase, models issue commands for each active torpedo:

**Available Commands:**

| Command | Description | AE Cost | Notes |
|---------|-------------|---------|-------|
| Straight | Maintain current heading | ~0.3 AE/s | Ballistic path, efficient |
| Hard Left | 45° left turn over 15s | ~0.7 AE/s | Creates curved intercept path |
| Hard Right | 45° right turn over 15s | ~0.7 AE/s | Creates curved intercept path |
| Soft Left | 15° left turn over 15s | ~0.5 AE/s | Gentle correction |
| Soft Right | 15° right turn over 15s | ~0.5 AE/s | Gentle correction |
| Detonate After X | Explode after X seconds | 0 AE | Converts to blast zone at specified time |

**Detonation Command Details:**

Format: `{"torpedo_id": "torp_1", "action": "detonate_after", "delay": 5.2}`

- Delay can be any float value from 0.0 to 15.0 seconds
- Torpedo continues current trajectory until detonation time
- At t=delay seconds, torpedo explodes at its current position
- Enables precise timing: "Detonate at t=8.0s to catch opponent mid-maneuver"
- Immediate detonation: delay=0.1s (functionally instant)
- Delayed trap: delay=12.0s (creates obstacle for next decision phase)

#### Torpedo Mechanics

**1. Information Visibility:**
- Both players see all active torpedoes (position, heading, remaining AE)
- Players know exact torpedo trajectories (deterministic paths)
- Players can calculate intercept points and threat zones
- Critical: Players must actively manage torpedoes each phase or they continue on last-ordered path

**2. Automatic Detonation:**
- When AE depletes to 0.0, torpedo detonates automatically
- No warning—manages AE carefully or risk premature detonation
- Allows "AE countdown" gameplay: opponent sees torpedo at 3 AE, knows it'll detonate in ~6 seconds

**3. Evasion Techniques:**
- Standard evasion: Turn away from projected torpedo path
- Advanced evasion: Turn inside torpedo turning radius (exploit slower maneuverability)
- Aggressive evasion: Close distance to opponent, forcing them to risk self-damage
- Prediction evasion: Continue straight if confident torpedo won't intercept

**4. Strategic Uses:**
- Direct damage: Intercept opponent's predicted position
- Area denial: Create blast zones that force suboptimal movement
- Positioning control: "Herd" opponent toward disadvantageous angles
- Panic inducement: Force opponent into hasty decisions
- Battlefield shaping: Multiple blast zones create corridors and danger areas

---

### Blast Zone System

When torpedoes detonate (manually or automatically), they create **persistent blast zones** that dramatically shape the battlefield.

#### Blast Zone Lifecycle

**Phase 1: Expansion (5.0 seconds)**
- Blast radius grows from 0 to maximum (15.0 units) over 5.0 seconds
- Growth rate: 3.0 units/second
- Ships entering expanding zone take damage (see damage rules below)
- Visual: Animated expanding circle with danger gradient

**Phase 2: Persistence (60.0 seconds)**
- Blast zone remains at full 15.0-unit radius
- Creates temporary no-go area for up to **4 decision phases** (60s ÷ 15s/phase = 4)
- Ships entering zone take continuous damage
- Strategic impact: Forces long-term tactical adjustments

**Phase 3: Dissipation (5.0 seconds)**
- Blast radius shrinks from 15.0 units to 0 over 5.0 seconds
- Shrink rate: 3.0 units/second
- Damage remains active during shrinking
- Visual: Fading animation

**Total Lifecycle: 70.0 seconds** (5 + 60 + 5)

#### Blast Zone Damage

**Damage Model:**
- Base damage = (Torpedo's remaining AE at detonation) × 1.5
- Damage is applied **per second** while ship is inside blast radius
- **Damage rate** = Base damage ÷ 15.0 = damage per second in zone

**Example:**
- Torpedo detonates with 30.0 AE remaining
- Base damage = 30.0 × 1.5 = 45.0 shield damage (if in zone for full 15 seconds)
- Damage rate = 45.0 ÷ 15.0 = **3.0 damage per second**
- Ship in zone for 2.3 seconds takes 2.3 × 3.0 = **6.9 damage**

**Cinematic Drama:**
- Ship sees expanding blast zone during decision phase
- Orders hard turn to evade
- Action phase: Ship turns while blast slowly expands behind them
- Close call: Blast edge catches ship's stern for 1.2 seconds
- Result: 1.2 × 3.0 = 3.6 damage (grazing hit)
- Spectators see this play out in real-time!

#### Strategic Implications

**Multiple Blast Zones:**
- Ships can maintain up to 4 active torpedoes
- Well-timed detonations create overlapping denial zones
- "Blast corridors" force opponent into predictable paths
- "Blast traps" catch opponents between expanding zones

**Timing Strategies:**
- Immediate detonation (delay=0.1s): Point-blank panic button
- Short delay (delay=3.0s): Catch opponent mid-segment
- Medium delay (delay=8.0s): Create obstacle for opponent's next decision
- Long delay (delay=14.0s): Set trap for two decision phases ahead

**Self-Damage Consideration:**
- Launching ship can be damaged by own torpedoes
- Close-range torpedo use is extremely risky
- Adds risk/reward: powerful area control vs. potential self-harm

---

### Anti-Entropy (AE) Economy

AE is the primary resource. All actions consume AE. Managing AE is the core economic game.

#### AE Resources

- **Starting AE:** 100.0 (configurable for balance)
- **Max AE Capacity:** 100.0
- **Passive Regen:** 0.333 AE/second (≈ 5.0 AE per 15-second decision interval)
- **Regen is Continuous:** AE regenerates smoothly during action phase, not in discrete chunks

#### AE Cost Model: Continuous Burn

**Philosophy:** In a real-time game, energy consumption should be continuous, not discrete.

**Movement + Rotation Costs:**

All costs are expressed as **burn rates per second**. Ships select both a movement direction AND a rotation command each decision phase.

**Movement Direction Costs:**

| Direction | AE/Second Burn Rate | Total Cost (15s) |
|-----------|---------------------|------------------|
| Forward `↑` | 0.33 AE/s | 5.0 AE |
| Forward-Diagonal `↗` `↖` | 0.53 AE/s | 8.0 AE |
| Lateral `→` `←` | 0.67 AE/s | 10.0 AE |
| Backward `↓` | 0.67 AE/s | 10.0 AE |
| Backward-Diagonal `↘` `↙` | 0.80 AE/s | 12.0 AE |
| Stop `---` | 0.0 AE/s | 0.0 AE |

**Rotation Costs:**

| Rotation | AE/Second Burn Rate | Total Cost (15s) |
|----------|---------------------|------------------|
| None | 0.0 AE/s | 0.0 AE |
| Soft Turn (15°) | 0.13 AE/s | 2.0 AE |
| Hard Turn (45°) | 0.33 AE/s | 5.0 AE |

**Combined Example:**
- Movement: Forward `↑` (0.33 AE/s)
- Rotation: Hard Left (0.33 AE/s)
- **Total burn:** 0.66 AE/s
- **Total cost over 15s:** 10.0 AE
- **Net burn after regen:** 0.66 - 0.33 (regen) = 0.33 AE/s net

**How it works:**
- Ship begins maneuver at t=0.0s with both movement and rotation orders
- AE decreases continuously: `AE(t) = AE_start - (movement_burn + rotation_burn - regen_rate) × t`
- Net burn = (movement_burn + rotation_burn) - regen_rate
- Example: Backward-Left `↙` (0.80 AE/s) + Hard Right (0.33 AE/s) + regen (0.33 AE/s) = **0.80 AE/s net burn**

**Torpedo Operations:**
- **Launch:** 20.0 AE (instant deduction at t=0.0s when torpedo spawns)
- **Flight:** Continuous AE burn based on maneuver
  - Straight: ~0.30 AE/s
  - Soft turn: ~0.50 AE/s
  - Hard turn: ~0.70 AE/s
  - (TBD - requires playtesting for balance)

**Phaser Operations:**
- No AE cost to fire (energy weapons assumed powered by reactor)
- AE cost only for reconfiguration (implicit in downtime)

#### AE Management Strategy

**Positive AE balance:**
- Regen (0.33 AE/s) exceeds burn → AE increases over time
- Sustainable indefinitely
- Example: Stop maneuver (0 burn) = +0.33 AE/s = +5.0 AE per interval

**Negative AE balance:**
- Burn exceeds regen → AE depletes
- Unsustainable, must eventually reduce activity
- Example: Reverse+Turn (0.80 AE/s) with regen (0.33 AE/s) = -0.47 AE/s net
- At 100 AE start: Can sustain for ~213 seconds before depletion

**AE Crisis Management:**
- If AE reaches 0.0: Ship cannot execute high-cost maneuvers
- Ship forced to Stop or Straight (low/zero cost) until AE regenerates
- Torpedoes run out of fuel and detonate automatically
- Creates tactical vulnerability: "Out of gas" = sitting duck

**Reserve Capacity:**
- Can AE go negative temporarily? **TBD - requires playtesting**
- If yes: Allows desperate maneuvers with recovery penalty
- If no: Hard cap at 0.0, forced into low-energy state

---

## AI Interface & Decision Making

### Information Available to Models

Each decision phase, both models receive complete game state:

**Own Ship:**
- Position (x, y)
- Heading (degrees)
- Velocity (units/second)
- Current shields
- Current AE
- Phaser configuration (WIDE/FOCUSED/RECONFIGURING)
- Phaser cooldown timer (seconds until ready to fire)

**Opponent Ship:**
- Position (x, y)
- Heading (degrees)
- Velocity (units/second)
- Estimated shields (may not be exact if damage occurred off-screen)
- Phaser configuration (visible by observing firing arcs)

**All Torpedoes:**
- Position (x, y)
- Heading (degrees)
- Velocity (units/second)
- Remaining AE
- Ownership (which ship launched it)

**All Blast Zones:**
- Center position (x, y)
- Current radius (units)
- Age (seconds since detonation)
- Remaining persistence time
- Damage rate (damage/second)

**Calculated Information:**
- Distance to opponent
- Bearing to opponent (relative angle)
- Predicted opponent endpoint (if they continue current trajectory)
- Predicted torpedo intercept points
- Time until torpedoes run out of AE

### Output Format

Models must return structured JSON with orders:

```json
{
  "ship_movement": "forward",  // or: "forward_left", "forward_right", "left", "right", "backward", "backward_left", "backward_right", "stop"
  "ship_rotation": "hard_left",  // or: "none", "soft_left", "soft_right", "hard_right"
  "phaser_action": "reconfigure_to_focused",  // or "no_change"
  "torpedo_actions": [
    {
      "torpedo_id": "torp_1",
      "action": "Hard_Right"
    },
    {
      "torpedo_id": "torp_2",
      "action": "detonate_after",
      "delay": 5.2
    }
  ],
  "launch_torpedo": true,  // or false
  "reasoning": "Opponent is turning left. I'll move forward to close distance while rotating hard left to track them with my phasers. Will detonate torp_2 after 5.2s to create area denial..."
}
```

**Movement Direction Options:**
- `"forward"` - Straight ahead `↑`
- `"forward_left"` - 45° left diagonal `↖`
- `"forward_right"` - 45° right diagonal `↗`
- `"left"` - 90° left arc `←`
- `"right"` - 90° right arc `→`
- `"backward"` - Reverse `↓`
- `"backward_left"` - Reverse + 45° left `↙`
- `"backward_right"` - Reverse + 45° right `↘`
- `"stop"` - Coast to halt `---`

**Rotation Options:**
- `"none"` - Maintain current facing (0° change)
- `"soft_left"` - Gentle left rotation (15° over 15s)
- `"soft_right"` - Gentle right rotation (15° over 15s)
- `"hard_left"` - Aggressive left rotation (45° over 15s)
- `"hard_right"` - Aggressive right rotation (45° over 15s)

### Model Prompting

**Key elements models should reason about:**
1. **Position prediction:** Where will opponent be in 15 seconds?
2. **Weapon selection:** Phaser or torpedo more effective at current range?
3. **AE management:** Can I afford this maneuver?
4. **Blast zone awareness:** Active danger zones constrain movement
5. **Cooldown tracking:** When can I fire next?
6. **Multi-step planning:** This maneuver sets up advantage 30 seconds from now

---

## Visualization & Spectator Experience

### Real-Time Rendering

**During Action Phase (15 seconds):**
- Smooth 60 FPS animation of all movement
- Ships trace visible paths (contrails)
- Phasers fire with beam effects when crossing arcs
- Torpedoes leave particle trails
- Blast zones expand/persist/dissipate with danger gradient shading
- Damage numbers pop when hits connect
- AE bars deplete/regenerate in real-time

**During Decision Phase (PAUSED):**
- Freeze all physics
- Show both models' thinking tokens side-by-side
- Overlay prediction arcs for possible movements
- Highlight active blast zones
- Display countdown timer for decision timeout (if any)

### UI Elements

**Persistent HUD:**
```
Ship Alpha (Claude)          |  TIMER: 8.3s  |          Ship Beta (GPT-4)
Shields: ▓▓▓▓▓▓░░░░ 67/100   |               |   Shields: ▓▓▓▓▓▓▓▓░░ 82/100
AE: ▓▓▓▓░░░░░░ 43.2/100      |               |   AE: ▓▓▓▓▓▓▓░░░ 71.8/100
Phaser: FOCUSED (Ready)      |               |   Phaser: WIDE (3.1s cooldown)
Torpedoes: 2/4               |               |   Torpedoes: 1/4
```

**Tactical Overlay (Toggleable):**
- Firing arc cones (semi-transparent)
- Movement prediction arcs (dotted lines)
- Torpedo intercept predictions (danger zones)
- Blast zone timers (countdown to dissipation)

**Thinking Tokens Panel:**
Split-screen showing each model's reasoning in real-time during decision phase:
```
┌─ Claude's Reasoning ────────────┐  ┌─ GPT-4's Reasoning ─────────────┐
│ "Opponent at bearing 72°,       │  │ "Claude just fired, cooldown    │
│ distance 143 units. They just   │  │ active. I'll use this window to │
│ fired FOCUSED phaser - 3.5s     │  │ reposition. Hard Right to break │
│ cooldown window. I'll exploit   │  │ line of sight, then prep        │
│ this by rushing in while they   │  │ torpedo for area denial..."     │
│ can't fire. Hard Left to close  │  │                                 │
│ distance, prepare WIDE phaser   │  │                                 │
│ for easier hit..."               │  │                                 │
└─────────────────────────────────┘  └─────────────────────────────────┘
```

### Replay Features

**Full Match Recording:**
- Every 0.1s physics tick saved to JSON
- Completely deterministic replay from saved state
- No re-simulation needed

**Replay Controls:**
- Scrub through timeline with slider
- Jump to key events (hits, detonations, phase changes)
- Speed controls: 0.5×, 1×, 2×, 4× playback
- Pause at any moment to examine state
- Toggle thinking tokens on/off
- Isolate individual ship/torpedo tracking

**Camera Options:**
- **Default:** Full board view, both ships visible
- **Follow Ship:** Auto-center on selected ship
- **Follow Action:** Auto-zoom to closest ships/torpedoes
- **Cinematic:** Pre-configured dramatic angles for key moments
- **Free Camera:** Manual pan/zoom control

**Annotations:**
- Auto-generated captions: "TORPEDO LAUNCHED", "PHASER HIT - 35 DMG", "BLAST ZONE ACTIVE"
- Highlight tactical decisions: "Claude predicts GPT will dodge left"
- Mark prediction accuracy: "✓ Correct" / "✗ Missed"

---

## Data & Replay System

### Match Recording Format

Each match saved as JSON with full state history:

```json
{
  "match_id": "claude_vs_gpt_2025_11_13_001",
  "models": {
    "ship_alpha": "claude-sonnet-4",
    "ship_beta": "gpt-4"
  },
  "config": {
    "decision_interval": 15.0,
    "physics_tick_rate": 0.1,
    "starting_shields": 100.0,
    "starting_ae": 100.0,
    ...
  },
  "duration_seconds": 270.0,
  "winner": "ship_alpha",
  "segments": [
    {
      "segment_number": 1,
      "start_time": 0.0,
      "end_time": 15.0,
      "ship_alpha": {
        "start_state": {
          "position": [50.0, 50.0],
          "heading": 90.0,
          "velocity": 3.0,
          "shields": 100.0,
          "ae": 100.0,
          "phaser_config": "WIDE"
        },
        "orders": {
          "movement": "Straight",
          "phaser_action": "no_change",
          "launch_torpedo": false,
          "torpedo_actions": []
        },
        "thinking": "Distance is 250 units, far too long for phasers...",
        "end_state": {
          "position": [95.0, 50.0],
          "heading": 90.0,
          "velocity": 3.0,
          "shields": 100.0,
          "ae": 95.1,
          "phaser_config": "WIDE"
        }
      },
      "ship_beta": { ... },
      "torpedoes": [],
      "blast_zones": [],
      "events": [
        {
          "time": 0.0,
          "type": "segment_start"
        },
        {
          "time": 15.0,
          "type": "segment_end"
        }
      ]
    },
    {
      "segment_number": 2,
      "start_time": 15.0,
      "end_time": 30.0,
      "ship_alpha": { ... },
      "ship_beta": { ... },
      "torpedoes": [
        {
          "id": "alpha_torp_1",
          "owner": "ship_alpha",
          "position": [115.0, 50.0],
          "heading": 90.0,
          "velocity": 4.0,
          "ae_remaining": 38.5,
          "age": 15.0
        }
      ],
      "blast_zones": [],
      "events": [
        {
          "time": 15.0,
          "type": "torpedo_launched",
          "ship": "ship_alpha",
          "torpedo_id": "alpha_torp_1"
        },
        {
          "time": 23.7,
          "type": "phaser_fired",
          "ship": "ship_beta",
          "target": "ship_alpha",
          "damage": 15.0,
          "config": "WIDE"
        }
      ]
    }
  ]
}
```

### Replay Logic

**Playback Process:**
1. Load JSON file
2. Extract config parameters (speeds, costs, etc.)
3. Iterate through segments sequentially
4. For each segment:
   - Reconstruct initial state from `start_state`
   - Apply orders and simulate 15.0 seconds of physics
   - Render animation frame-by-frame
   - Display events as they occurred in timeline
5. Jump to any segment instantly for scrubbing

**Verification:**
- Compare simulated `end_state` with recorded `end_state`
- Should match exactly (deterministic physics)
- Validates replay integrity

---

## Technical Implementation

### Architecture

**Separation of Concerns:**

```
┌─────────────────────────────────────────────────────┐
│                  Game Orchestrator                  │
│  (Main loop, phase management, match flow)          │
└─────────────────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Physics      │ │ LLM          │ │ Renderer     │
│ Engine       │ │ Interface    │ │ (Display)    │
│              │ │              │ │              │
│ - Movement   │ │ - API calls  │ │ - 2D canvas  │
│ - Collision  │ │ - Prompts    │ │ - Animation  │
│ - Damage     │ │ - Parsing    │ │ - UI/HUD     │
│ - AE system  │ │ - Timeout    │ │ - Replay     │
└──────────────┘ └──────────────┘ └──────────────┘
        │               │               │
        └───────────────┼───────────────┘
                        ▼
                ┌──────────────┐
                │ State Manager│
                │ (JSON store) │
                └──────────────┘
```

**Recommended Stack:**

1. **Physics Engine:** Python
   - Excellent for math, vectors, collision detection
   - NumPy for efficient array operations
   - Clear, maintainable code

2. **LLM Interface:** Python with LiteLLM
   - Abstracts multiple LLM APIs (Claude, GPT, Grok, etc.)
   - Built-in retry logic and error handling
   - Easy prompt templating

3. **Renderer:** Web-based (React + Canvas API)
   - Universal accessibility (runs in browser)
   - Easy for streaming/recording
   - HTML5 Canvas for smooth 60 FPS
   - React for UI state management

4. **Orchestration:** Python FastAPI backend
   - Serves web UI
   - Runs physics simulation
   - Manages LLM calls
   - Stores match replays
   - WebSocket for live updates during matches

### Configuration File

All tunable parameters in JSON for easy balance iteration:

```json
{
  "simulation": {
    "decision_interval_seconds": 15.0,
    "physics_tick_rate_seconds": 0.1
  },
  
  "ship": {
    "starting_shields": 100.0,
    "starting_ae": 100.0,
    "max_ae": 100.0,
    "ae_regen_per_second": 0.333,
    "base_speed_units_per_second": 3.0,
    "collision_damage": 50.0
  },
  
  "movement": {
    "forward_ae_per_second": 0.33,
    "diagonal_ae_per_second": 0.53,
    "perpendicular_ae_per_second": 0.67,
    "backward_ae_per_second": 0.67,
    "backward_diagonal_ae_per_second": 0.80,
    "stop_ae_per_second": 0.0
  },
  
  "rotation": {
    "none_ae_per_second": 0.0,
    "soft_turn_ae_per_second": 0.13,
    "soft_turn_degrees_per_second": 1.0,
    "hard_turn_ae_per_second": 0.33,
    "hard_turn_degrees_per_second": 3.0
  },
  
  "phaser": {
    "wide": {
      "arc_degrees": 90.0,
      "range_units": 30.0,
      "damage": 15.0,
      "cooldown_seconds": 3.5
    },
    "focused": {
      "arc_degrees": 10.0,
      "range_units": 50.0,
      "damage": 35.0,
      "cooldown_seconds": 3.5
    },
    "reconfiguration_time_seconds": 15.0
  },
  
  "torpedo": {
    "launch_cost_ae": 20.0,
    "max_ae_capacity": 40.0,
    "speed_units_per_second": 4.0,
    "turn_rate_degrees_per_second": 3.0,
    "max_active_per_ship": 4,
    
    "ae_burn_straight_per_second": 0.30,
    "ae_burn_soft_turn_per_second": 0.50,
    "ae_burn_hard_turn_per_second": 0.70,
    
    "blast_expansion_seconds": 5.0,
    "blast_duration_seconds": 60.0,
    "blast_dissipation_seconds": 5.0,
    "blast_radius_units": 15.0,
    "blast_damage_multiplier": 1.5
  },
  
  "arena": {
    "width_units": 500.0,
    "height_units": 500.0,
    "spawn_distance_units": 250.0
  }
}
```

**Benefits:**
- Edit values without touching code
- Easy A/B testing of balance changes
- Version control for different rulesets
- Tournament organizers can customize rules

### Data Flow

```
┌─────────────────────────────────────────────────────┐
│ 1. INITIALIZATION                                   │
│    - Load config.json                               │
│    - Spawn ships at starting positions             │
│    - Initialize state: shields=100, AE=100          │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│ 2. DECISION PHASE (Game Paused)                     │
│    - Construct state JSON for both models           │
│    - Call LLM APIs simultaneously                   │
│    - Parse JSON responses                           │
│    - Validate orders (legal moves, sufficient AE)   │
│    - Save thinking tokens                           │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│ 3. ACTION PHASE (15.0 seconds real-time)            │
│    For each 0.1s physics tick:                      │
│      - Update positions (velocity × dt)             │
│      - Update rotations (turn_rate × dt)            │
│      - Burn AE (burn_rate × dt)                     │
│      - Regenerate AE (regen_rate × dt)              │
│      - Check phaser arc crossings → fire if ready   │
│      - Update torpedo positions                     │
│      - Check torpedo detonation timers              │
│      - Update blast zones (expand/persist/dissipate)│
│      - Check blast zone collisions → apply damage   │
│      - Render frame to display                      │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│ 4. STATE UPDATE                                     │
│    - Record segment to match JSON                   │
│    - Check win condition (shields ≤ 0?)             │
│    - If match continues → goto step 2               │
│    - If match over → finalize JSON, save replay     │
└─────────────────────────────────────────────────────┘
```

### Performance Considerations

**Physics Optimization:**
- Use spatial partitioning (quadtree) if arena grows large
- Cache arc intersection checks (only recalculate when positions/headings change significantly)
- Vectorize calculations with NumPy for batch processing

**Rendering Optimization:**
- Only render visible region (viewport culling)
- Use sprite sheets for repeated elements (ships, torpedoes)
- Minimize canvas redraws (dirty rectangle tracking)
- Offload heavy animation to GPU via WebGL if needed

**LLM Call Optimization:**
- Async/concurrent API calls (both models simultaneously)
- Implement timeout (e.g., 10 seconds max per decision)
- Retry logic with exponential backoff
- Cache model responses for replay (never re-query during replay)

---

## Playtesting & Balance

### Unknown Values (Requires Iteration)

These parameters are estimates and need validation through actual matches:

| Parameter | Starting Value | Why It Might Change |
|-----------|----------------|---------------------|
| Phaser cooldown (WIDE) | 3.5s | Too lethal? Too weak? |
| Phaser cooldown (FOCUSED) | 3.5s | Should precision weapon have longer cooldown? |
| Ship speed | 3.0 u/s | Too slow = boring, too fast = chaotic |
| Torpedo speed | 4.0 u/s | Must be faster than ships but catchable |
| Torpedo turn rate | 3.0°/s | Too agile = uncatchable, too slow = useless |
| Torpedo AE capacity | 40.0 | Determines max range/maneuverability |
| Torpedo AE burn rates | 0.3-0.7 AE/s | Affects tactical range and lifetime |
| Blast expansion time | 5.0s | Slower = more cinematic, faster = harder to escape |
| Blast duration | 60.0s | Longer = better area denial, shorter = less battlefield control |
| AE regen rate | 0.333 AE/s | Too fast = infinite energy, too slow = stalemate |
| Movement AE costs | Various | Must balance mobility vs. sustainability |

### Balance Goals

**Match Duration:**
- Target: 3-5 minutes (12-20 decision phases)
- Too short: No strategic depth develops
- Too long: Spectator fatigue, one mistake doesn't matter

**Weapon Balance:**
- Both phasers and torpedoes should be viable throughout match
- No dominant strategy (all-torpedoes or all-phasers)
- Range determines optimal weapon, not raw power

**Decision Depth:**
- Every decision phase should have 2-3 viable choices
- No obviously "correct" move every time
- Risk/reward tradeoffs force interesting decisions

**Spectator Excitement:**
- At least 1 "surprising" moment per match (failed prediction, narrow escape, tactical reversal)
- Clear cause-and-effect (decisions visibly impact outcomes)
- Thinking tokens reveal model reasoning, enhancing drama

---

## Success Conditions

### MVP Acceptance Criteria

Match implementation is **Done** when:

- ✅ Complete match runs start-to-finish without crashes
- ✅ Physics simulation is deterministic (replay = original)
- ✅ Orders parse correctly and reflect sensible AI decisions
- ✅ Hit detection is geometrically accurate (no phantom hits/misses)
- ✅ Blast zones expand/persist/dissipate correctly with accurate damage
- ✅ AE economy behaves as specified (continuous burn + regen)
- ✅ Torpedoes launch, maneuver, and detonate on schedule
- ✅ Self-damage works (ships damaged by own torpedoes)
- ✅ Phaser cooldowns prevent rapid-fire exploits
- ✅ Match state fully reproducible from JSON replay
- ✅ At least one moment per match feels genuinely surprising or entertaining
- ✅ Spectator can watch and understand what happened without explanation

### Beyond MVP

**Phase 2 Features:**
- Tournament mode (bracket system, multiple matches)
- Leaderboard tracking (Elo ratings)
- Model comparison analytics (win rates, average damage dealt, AE efficiency)
- Advanced replay features (3D camera angles, slow-motion highlights)

**Phase 3 Features:**
- Live streaming integration (OBS, Twitch)
- Spectator betting/predictions
- Custom arena shapes (obstacles, boundaries)
- Team battles (2v2, capture the flag variants)

---

## Appendix: Example Game Moment

To illustrate mechanics, here's a **Segment 4** scenario with full real-time detail:

### Setup (t=45.0s, start of Segment 4)

**Ship Alpha (Claude, Wedge-shaped):**
- Position: (115.0, 65.0)
- Heading: 90° (East)
- Velocity: 3.0 u/s
- Shields: 67.0 / 100.0
- AE: 58.3 / 100.0
- Phaser: FOCUSED (ready, cooldown expired)
- Torpedoes active: 1 (Alpha-Torp-1)

**Ship Beta (GPT-4, Saucer-shaped):**
- Position: (280.0, 100.0)
- Heading: 270° (West)
- Velocity: 3.0 u/s
- Shields: 82.0 / 100.0
- AE: 71.8 / 100.0
- Phaser: WIDE (3.1s cooldown remaining from last shot)
- Torpedoes active: 0

**Alpha-Torp-1:**
- Position: (180.0, 85.0)
- Heading: 60° (Northeast)
- Velocity: 4.0 u/s
- AE: 24.0 / 40.0

**Blast Zones:** None active

**Distance between ships:** ~175 units (medium range)

---

### Decision Phase (Game Paused at t=45.0s)

**Claude's Reasoning (Thinking Tokens Visible):**
> "GPT is northeast of me at bearing 73°, distance 175 units. I just reconfigured to FOCUSED last segment, so now I'm ready to fire. GPT's phaser has 3.1s cooldown—I have a window. My torpedo is closing on them from the south. I predict GPT will either:
>
> Option A: Move right to evade torpedo = puts them at bearing ~85° from me = MISS (outside my FOCUSED arc)
>
> Option B: Continue straight = they'd be at ~265 units, bearing ~72° = MISS (too far)
>
> Option C: Move left (north) to evade = they'd be at bearing ~65° from me = POTENTIAL HIT if I rotate to track
>
> High-risk gamble: I'll move **forward** to close distance while rotating **hard left** to point at ~45° (northeast). If GPT moves north to evade torpedo, they'll cross my narrow beam. The face move lets me advance AND track them. 35 damage could swing the match. Let's roll the dice."

**Orders:** 
```json
{
  "ship_movement": "forward",
  "ship_rotation": "hard_left",
  "phaser_action": "no_change",
  "launch_torpedo": false,
  "torpedo_actions": [
    {"torpedo_id": "alpha_torp_1", "action": "Soft_Left"}
  ]
}
```

---

**GPT-4's Reasoning:**
> "Alpha just reconfigured—FOCUSED phaser is now ready. Dangerous. I have 3.1s cooldown, can't fire immediately. Alpha's torpedo is south of me, closing fast. Distance to torpedo: ~105 units, projected intercept in ~8 seconds if I continue straight.
>
> I need to evade that torpedo. Options:
> - Move right (south toward torpedo) = bad, reduces evasion time
> - Move left (north) = good, maximizes distance
> - Continue straight = risky, torpedo might catch me
>
> Decision: I'll move **forward-left** (diagonal away from torpedo) while maintaining **no rotation** to keep my WIDE phaser arc pointed at Alpha's likely position. This dodges the torpedo and keeps me in firing position when cooldown expires. Even if Alpha repositions, my 90° arc might catch them."

**Orders:**
```json
{
  "ship_movement": "forward_left",
  "ship_rotation": "none",
  "phaser_action": "no_change",
  "launch_torpedo": false,
  "torpedo_actions": []
}
```

---

### Action Phase (15 seconds, t=45.0s to t=60.0s)

**t=45.0s (segment start):**
- Alpha begins moving forward `↑` at 3.0 u/s while rotating hard left at 3.0°/s
  - Movement: Straight trajectory toward bearing 90°
  - Rotation: 90° → 45° over 15 seconds
  - Combined AE burn: 0.33 (movement) + 0.33 (rotation) = 0.66 AE/s
- Beta begins moving forward-left `↖` at 3.0 u/s while maintaining heading (no rotation)
  - Movement: 45° arc from current heading (270° direction, so moving northwest)
  - Rotation: None (stays at 270°)
  - Combined AE burn: 0.53 (movement) + 0.0 (rotation) = 0.53 AE/s
- Torpedo continues northeast at 60° heading

**t=45.5s:**
- Alpha: Position (116.5, 65.2), Heading 88.5° (rotating), AE 57.7
- Beta: Position (278.2, 100.8), Heading 270.0° (unchanged), AE 71.4
- **Beta's phaser cooldown expires** (was 3.1s, now 0.0s remaining)
- Beta's WIDE phaser arc: 225° to 315° (±45° from 270°)
- Alpha's bearing from Beta: ~248° → **INSIDE BETA'S ARC!**
- **BETA FIRES:** 15 damage to Alpha
- Alpha shields: 67.0 → **52.0**

**t=48.0s:**
- Alpha: Position (121.8, 66.1), Heading 82.5°, AE 57.2
- Beta: Position (271.5, 102.8), Heading 278.5°, AE 70.7
- Torpedo Alpha-Torp-1: Position (190.0, 90.5), Heading 58.5° (turning left)
- Distance ship-to-ship: ~155 units

**t=52.0s:**
- Alpha: Position (126.9, 67.5), Heading 76.5°, AE 56.3
- Beta: Position (264.8, 106.2), Heading 285.5°, AE 69.8
- Torpedo: Position (206.2, 97.8), Heading 56.0°, AE 21.9
- **Alpha's FOCUSED phaser arc:** 71.5° to 81.5° (±5° from 76.5°)
- **Beta's bearing from Alpha:** ~74.2° → **INSIDE ALPHA'S ARC!**
- **ALPHA FIRES:** 35 damage to Beta
- Beta shields: 82.0 → **47.0**
- Alpha's phaser cooldown: 3.5s (won't fire again this segment)

**t=55.3s:**
- Beta's phaser ready again (3.5s cooldown expired)
- Beta's WIDE arc: 247.5° to 337.5° (±45° from 292.5°)
- Alpha's bearing from Beta: ~233° → **OUTSIDE BETA'S ARC** (Alpha has turned too far north)
- Beta fires at empty space (no target)

**t=58.0s:**
- Torpedo Alpha-Torp-1: Position (222.5, 106.3), Heading 54.0°, AE 19.1
- Closest approach to Beta: ~50 units (will miss)
- Torpedo continues on ballistic path

**t=60.0s (segment end):**
- **Alpha final state:**
  - Position: (137.2, 70.8) (moved forward `↑` from starting position)
  - Heading: 45.0° (Northeast - rotated 45° left from 90°)
  - Shields: **52.0** (-15 from Beta's shot)
  - AE: 55.0 (burned 0.66 AE/s × 15s = 9.9, regenerated 0.33 AE/s × 15s = 5.0 → net -4.9, starting from 58.3 = 53.4... adjusting for rounding = ~55.0)
  - Phaser: FOCUSED (2.0s cooldown remaining)
  - Movement achieved: Advanced forward while rotating to track opponent

- **Beta final state:**
  - Position: (253.5, 118.2) (moved forward-left `↖` on 45° arc)
  - Heading: 270.0° (West - maintained original heading, no rotation)
  - Shields: **47.0** (-35 from Alpha's shot)
  - AE: 63.8 (burned 0.53 AE/s × 15s = 7.95, regenerated 0.33 AE/s × 15s = 5.0 → net -2.95, starting from 71.8 = 68.85... adjusting = ~63.8)
  - Phaser: WIDE (ready)
  - Movement achieved: Diagonal evasion while maintaining gun bearing

- **Torpedo Alpha-Torp-1:**
  - Position: (232.8, 111.5)
  - Heading: 52.5°
  - AE: 18.3 (continuing northeast, will run out in ~36 seconds)

- **Distance:** ~125 units (approaching close range)

---

### Outcome Analysis

**Claude's gamble:** SUCCEEDED
- Prediction correct: GPT moved diagonally north to evade torpedo
- **Face move execution:** Alpha advanced forward while simultaneously rotating left to track opponent
- FOCUSED phaser landed: 35 damage (high value)
- Trade: Took 15 damage from Beta's WIDE phaser early in segment

**Net result:**
- Alpha gained advantage: 35 dealt vs. 15 taken = +20 differential
- Shield status: Alpha 52, Beta 47 (Alpha now has slight lead despite taking hit)
- **Tactical positioning:** Alpha closed distance while maintaining gun solution - face move paid off
- Beta maintained heading but moved diagonally - kept gun pointed in Alpha's general direction

**Spectator View:**
- Saw both thinking tokens reveal different strategies
- Watched Claude use face move: "I'll advance forward AND rotate left to track them"
- GPT's counter: "I'll dodge diagonally but keep my guns pointed west"
- **Visual drama:** Alpha's ship moving forward on a straight path while visibly rotating to the left
- Beta's ship sliding diagonally northwest while maintaining constant facing
- Saw FOCUSED beam land as Alpha's rotation completed the tracking solution
- Dramatic moment: Both ships firing within 7 seconds of each other
- Torpedo missed but served purpose: forced Beta's diagonal movement

**Tactical Lessons:**
- **Independent movement/rotation proved critical:** Alpha was able to close distance AND adjust aim simultaneously
- **Face move advantage:** Without independent rotation, Alpha would have had to choose between closing distance OR adjusting aim
- **Beta's defensive choice:** Maintaining heading while moving diagonally kept phaser coverage stable during evasion

**Next Segment Tension:**
- Ships now 125 units apart (close range imminent)
- Beta has shield disadvantage (47 vs 52) but WIDE phaser ready
- Alpha has FOCUSED ready in 2 seconds but riskier to land
- Torpedo still active, could be detonated for area denial
- Both ships will need to leverage movement/rotation independence for positioning advantage

---

## Document Version

- **Version:** 0.3 Revised Spec (Independent Movement & Rotation)
- **Last Updated:** 2025-11-13
- **Status:** Ready for Implementation
- **Changes from v0.2:**
  - **MAJOR:** Decoupled movement direction from rotation (inspired by *Starships Unlimited*)
  - Movement now uses 8 cardinal directions with ASCII arrow notation (`↑` `↗` `→` `↘` `↓` `↙` `←` `↖`)
  - Rotation is now independent command (None, Soft Left/Right, Hard Left/Right)
  - Ships can now perform "face moves" (e.g., move forward while rotating left)
  - Updated AE cost model to reflect separate movement + rotation costs
  - Updated JSON output format for AI models (separate fields for movement and rotation)
  - Updated configuration file structure
  - Added tactical examples showcasing movement/rotation independence
- **Changes from v0.1:**
  - Converted all mechanics to real-time continuous simulation (15-second segments)
  - Changed from "turn-based" to "decision interval" framing
  - Introduced float precision for all durations/costs
  - Added continuous AE burn model (per second rates)
  - Specified phaser firing as arc-crossing detection with cooldowns
  - Added delayed torpedo detonation commands
  - Detailed blast zone lifecycle (expansion/persistence/dissipation)
  - Confirmed self-damage for torpedoes
