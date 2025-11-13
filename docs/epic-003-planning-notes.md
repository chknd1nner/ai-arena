# Epic 003: Planning Notes (Note to Future Self)

**Status:** Planning / Not Started
**Created:** 2025-11-13
**Last Epic Completed:** Epic 002 (pending implementation)

---

## Quick Recap: What We've Built So Far

### Epic 001: Configuration Loading System ✅ COMPLETE

**Status:** Merged to main 2025-11-13

**What it did:**
- Replaced hardcoded physics constants with config.json
- Added comprehensive validation on startup (fails fast with clear errors)
- Created ConfigLoader with validation rules
- Established single source of truth for all game parameters

**Key files:**
- `ai_arena/config/loader.py` - Configuration loading and validation
- `config.json` - All game parameters
- `ai_arena/web_server/main.py` - Startup validation

**Why it matters:**
Foundation for everything. Now we can tune game balance by editing config.json without touching code. Epic 002 heavily relies on this.

**Test coverage:** 35+ tests, all passing

---

### Epic 002: Independent Movement & Rotation System 🚧 READY FOR IMPLEMENTATION

**Status:** Fully planned, ready for Claude Code Web

**What it will do:**
Implement the "face move" system where ships can move in one direction while facing another. This is THE core tactical mechanic from the game spec that unlocks:
- **Strafing runs:** Circle around enemy while keeping guns pointed at them
- **Retreat with coverage:** Back away while phasers still face forward
- **Aggressive reposition:** Advance while rotating for better firing arc
- **The drift:** Slide laterally while gradually tracking target

**Current problem:**
Movement and rotation are coupled - ship always faces where it's moving. Can't do any of the cool tactical maneuvers.

**Solution:**
- Movement sets velocity direction (where you move)
- Rotation sets heading (where you face)
- Phasers point at heading, not velocity
- Both have separate AE costs

**8 Stories planned:**
1. Data Model Foundation (new enums: MovementDirection, RotationCommand)
2. Movement Direction System (decouple velocity from heading)
3. Independent Rotation System (separate heading control)
4. Combined AE Cost System (movement + rotation costs)
5. LLM Prompt Engineering (teach models the new system)
6. LLM Order Parsing (parse new JSON format)
7. Physics Testing Suite (comprehensive tests)
8. Tactical Validation (verify all 4 maneuvers work)

**Key files that will change:**
- `ai_arena/game_engine/data_models.py` - New enums, Orders update
- `ai_arena/game_engine/physics.py` - Complete refactor of `_update_ship_physics()`
- `ai_arena/llm_adapter/adapter.py` - New prompts and parsing
- `config.json` - Movement costs updated
- Tests everywhere

**Implementation approach:**
- **Phase 1** (Stories 1-4): Physics foundation - testable without LLM changes
- **Phase 2** (Stories 5-6): LLM integration
- **Phase 3** (Stories 7-8): Testing and validation

**Estimated effort:** 8-12 hours Claude Code Web time (split across 2-3 sessions if needed)

**Why it matters:**
This is the difference between "ships fly in arcs" and "ships execute naval combat maneuvers". Unlocks the tactical depth promised in the game spec. After this, LLMs can actually play tactically interesting matches.

---

## What Should Epic 003 Be?

### Context: Where We'll Be After Epic 002

After Epic 002 completes:
- ✅ Config system solid (Epic 001)
- ✅ Core movement mechanics working (Epic 002)
- ✅ Ships can strafe, retreat, drift, reposition
- ✅ LLMs can use both movement and rotation commands
- ⚠️ Physics still discrete (per-turn, not continuous)
- ⚠️ No visualization (can't see the cool maneuvers!)
- ⚠️ Phasers have no cooldown (fire every turn if in arc)
- ⚠️ AE economy is per-turn, not continuous
- ⚠️ Torpedoes can't detonate on command

### Option A: Continuous Physics & Real-Time Feel 🎯 RECOMMENDED

**Epic 003: Continuous Physics System**

**Problem:**
Current physics is discrete (per-turn). Each turn:
- Deduct full AE cost upfront
- Regenerate full AE at end
- Phasers fire once per turn (no cooldown)
- Everything happens in discrete chunks

This works but feels "turn-based" rather than "real-time simulation".

**Game spec says:**
- Everything operates in continuous real-time
- AE burns continuously (0.33 AE/s regen vs 0.66 AE/s burn for some maneuvers)
- Phasers have 3.5s cooldown (can fire ~4 times per 15s turn)
- All durations, speeds, rates are in seconds with float precision

**What Epic 003 would do:**
1. **Continuous AE tracking** - Track AE per substep, not per turn
2. **Phaser cooldown system** - Add cooldown timer to ShipState
3. **Substep-level AE burn** - Movement and rotation costs applied each substep
4. **Phaser rate limiting** - Can only fire once per cooldown period
5. **Better AE economy** - Net AE drain/gain feels more realistic

**Stories (rough):**
- Story 012: Add phaser cooldown to ShipState and config
- Story 013: Track AE changes per substep
- Story 014: Apply continuous AE burn during action phase
- Story 015: Implement phaser cooldown enforcement
- Story 016: Test continuous physics (determinism critical!)
- Story 017: Balance tuning (phaser cooldown, costs, etc.)

**Complexity:** Medium (similar to Epic 002)
**Estimated effort:** 6-8 stories, 8-10 hours
**Risk:** Medium - Must maintain determinism

**Why this makes sense next:**
- Natural evolution of physics system
- Makes combat feel more dynamic
- Enables better tactical decisions (AE management more important)
- Still foundational work (no UI needed)
- Can be tested entirely with physics tests

**Why this might NOT be next:**
- Another physics refactor (might want to see results first)
- No visible impact without matches running
- Could wait until we have visualization

---

### Option B: Frontend Replay Viewer 🎨 HIGH IMPACT

**Epic 003: Canvas-Based Match Visualization**

**Problem:**
We've built this cool tactical combat system but can only see it through JSON replays and logs. Can't actually WATCH the matches happen. Epic 002's tactical maneuvers would be so much cooler if we could SEE them.

**What Epic 003 would do:**
Build a React canvas viewer that:
1. Loads replay JSON
2. Renders ships, torpedoes, phasers on canvas
3. Shows real-time playback with controls (play/pause/speed)
4. Displays ship headings (where they face) vs velocity (where they move)
5. Shows phaser arcs and firing
6. Visualizes torpedo trajectories and blasts
7. Displays game state (shields, AE, turn number)

**Stories (rough):**
- Story 012: Canvas setup and coordinate system
- Story 013: Ship rendering (position, heading, velocity vector)
- Story 014: Weapon rendering (phasers, torpedoes)
- Story 015: Playback controls (play/pause/scrub/speed)
- Story 016: Game state overlay (shields, AE, scores)
- Story 017: Trajectory visualization (ship paths, torpedo trails)
- Story 018: Polish and UX improvements

**Complexity:** Medium-High (frontend work, different skillset)
**Estimated effort:** 7-8 stories, 10-12 hours
**Risk:** Low - Doesn't touch game logic

**Why this makes sense next:**
- **HIGH IMPACT** - Actually see the game in action!
- Lets us appreciate Epic 002's work
- Makes playtesting much easier
- Great for demos and marketing
- Helps identify balance issues visually
- Fun to build!

**Why this might NOT be next:**
- Different domain (frontend vs physics)
- Doesn't add gameplay depth
- Could be done later
- Frontend tech stack (React, Canvas API)

---

### Option C: Enhanced Torpedo Tactics 💣

**Epic 003: Torpedo Command System**

**Problem:**
Torpedoes are currently pretty simple:
- Launch with 20 AE
- Move straight (or use basic MovementType commands)
- Explode on contact or when AE depletes
- Can't detonate on command

**Game spec mentions:**
- Timed detonation: `detonate_after: 5.0` (explode in 5 seconds)
- Proximity detonation: Explode when near enemy
- Zone denial: Create blast zones to control space
- Torpedo as mines: Launch, stop, wait for enemy

**What Epic 003 would do:**
1. Add timed detonation command
2. Add manual detonation command
3. Improve torpedo movement options
4. Better torpedo AI (LLM prompts)
5. Tactical scenarios (mines, traps, barrages)

**Complexity:** Small-Medium
**Estimated effort:** 4-5 stories, 4-6 hours
**Risk:** Low

**Why this makes sense next:**
- Smaller scope (easier win after Epic 002)
- Adds tactical variety
- Fun to implement
- Builds on existing torpedo system

**Why this might NOT be next:**
- Lower priority than core physics
- Torpedoes already work okay
- Could wait until after visualization

---

### Option D: Tournament & Match Infrastructure 🏆

**Epic 003: Tournament System**

**Problem:**
Currently can only run one-off matches. No way to:
- Run best-of-N series
- Compare model performance
- Track win rates
- Run tournaments
- Test balance changes systematically

**What Epic 003 would do:**
1. Tournament configuration (model lineup, match count)
2. Automated match scheduling
3. Result aggregation and statistics
4. Elo ratings or similar
5. Balance testing tools
6. Performance benchmarks

**Complexity:** Medium
**Estimated effort:** 6-7 stories, 8-10 hours
**Risk:** Low

**Why this makes sense next:**
- Makes testing much easier
- Systematic balance tuning
- Compare models scientifically
- Content for research papers/blog posts

**Why this might NOT be next:**
- Infrastructure work (less exciting)
- Needs good baseline gameplay first
- Visualization would help tournament viewing

---

## My Recommendation: Epic 003 Path

### Path A (Conservative): Continuous Physics → Frontend → Tournaments
1. **Epic 003: Continuous Physics** - Finish physics foundation
2. **Epic 004: Frontend Viewer** - See the game in action
3. **Epic 005: Tournament System** - Systematic testing
4. **Epic 006: Torpedo Enhancements** - Add variety

**Rationale:** Complete the physics before showing it off. Solid foundation first.

### Path B (Show & Tell): Frontend → Continuous Physics → Tournaments
1. **Epic 003: Frontend Viewer** - See Epic 002 results immediately!
2. **Epic 004: Continuous Physics** - Improve what we're seeing
3. **Epic 005: Tournament System** - Systematic testing
4. **Epic 006: Torpedo Enhancements** - Add variety

**Rationale:** Visualization helps with everything else. Easier to debug, tune, and demo with visuals.

### Path C (Quick Win): Torpedoes → Frontend → Continuous Physics
1. **Epic 003: Torpedo Enhancements** - Small, fun addition
2. **Epic 004: Frontend Viewer** - See everything in action
3. **Epic 005: Continuous Physics** - Polish the physics
4. **Epic 006: Tournament System** - Testing infrastructure

**Rationale:** Quick tactical win, then big visualization win, then finish physics.

---

## Personal Take (Note to Self)

**I'd probably do Path B: Frontend First**

**Why:**
- Epic 002 adds cool movement but we can't SEE it
- Visualization makes everything else easier
- Demo-able progress (show stakeholders)
- Debugging is easier with visuals
- More fun to work on (change of pace from physics)
- Continuous physics can wait - discrete physics works fine for now

**Then after frontend:**
- Epic 004: Continuous Physics (make it feel real-time)
- Epic 005: Tournament System (systematic testing)
- Epic 006: Advanced Tactics (torpedoes, formations, etc.)

**Long-term roadmap thoughts:**
- Epic 007: Multi-match narratives (rivalries, story mode)
- Epic 008: Spectator features (live streaming, commentary)
- Epic 009: Balance & Polish (tuning based on data)
- Epic 010: Advanced AI (better prompts, few-shot learning)

---

## Key Questions for Epic 003 Planning Session

When you (future self) come back to plan Epic 003, answer these:

1. **Has Epic 002 been implemented and tested?**
   - If not, finish it first
   - If yes, how did it go? Any lessons learned?

2. **What's the current pain point?**
   - Can't see matches? → Frontend
   - Physics feels chunky? → Continuous Physics
   - Need more variety? → Torpedoes
   - Need testing tools? → Tournament

3. **What's the goal for next 2-3 epics?**
   - Build foundation? → Continue physics work
   - Show progress? → Build frontend
   - Test thoroughly? → Build tournaments
   - Add content? → New mechanics

4. **Who's the audience right now?**
   - Just you testing? → Pick what's fun
   - Showing to others? → Build frontend
   - Writing paper? → Build tournaments for data
   - Marketing? → All of the above

5. **How did Epic 002 implementation go?**
   - Smooth? → Tackle something bigger
   - Rough? → Take a break with smaller epic
   - Too long? → Split epics more
   - Just right? → Similar scope for Epic 003

---

## Files to Review Before Planning Epic 003

- `docs/game_spec_revised.md` - Full game specification
- `docs/architecture.md` - System design patterns
- `docs/development-workflow.md` - Claude Code Web best practices
- `docs/epic-001-*.md` (archived) - Lessons from Epic 001
- `docs/epic-002-*.md` - Lessons from Epic 002
- Epic 002 implementation PR - What actually happened vs plan?

---

## Final Thought

**The beauty of this system:** Any of these options are viable. The architecture is clean enough that we can do them in almost any order. Pick based on what's fun, what's needed, and what makes sense for the current state of the project.

**Best advice to future self:**
- Don't overthink it
- Pick what excites you
- Write clear stories like Epic 002
- Keep epics focused
- Ship incrementally
- Have fun!

---

**Now go implement Epic 002 and come back when you're ready for Epic 003! 🚀**
