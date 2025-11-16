# Next Sprint: Story 026 - Balance Tuning & Integration Testing

**SPRINT START: Story 026 - Balance Tuning & Integration Testing**

**Epic:** Epic 004: Continuous Physics System
**Status:** Ready for Development
**Branch:** `claude/plan-sprint-01WBvgYYmWn22Qhz6fAA6WKM`

## Your Mission

You are the **Dev Agent** implementing **Story 026: Balance Tuning & Integration Testing** - the final story of Epic 004. This story validates that the continuous physics system implemented in Stories 020-025 is balanced and production-ready.

## Context

Stories 020-025 have successfully implemented the continuous physics system:
- ✅ Phaser cooldown enforcement (3.5s between shots)
- ✅ Per-substep AE regeneration (0.33 AE/s)
- ✅ Continuous movement AE costs
- ✅ Continuous rotation AE costs
- ✅ Comprehensive test coverage (137 tests passing)

Your job is to **validate game balance** through playtesting and tune parameters if needed.

## Acceptance Criteria

- [ ] Run at least 3 full LLM vs LLM matches
- [ ] Analyze match outcomes and energy patterns
- [ ] Tune phaser cooldown if needed (adjust config.json)
- [ ] Document balance changes and rationale
- [ ] Verify tuned parameters feel balanced
- [ ] Update game documentation with new mechanics

## Implementation Steps

### 1. Run Baseline Matches (30-40 min)

Run at least 3 full matches using the backend API:

```bash
# Start backend
python3 main.py

# In another terminal, start matches via API
curl -X POST http://localhost:8000/api/match/start \
  -H "Content-Type: application/json" \
  -d '{"model_a": "anthropic/claude-3-haiku-20240307", "model_b": "anthropic/claude-3-haiku-20240307", "max_turns": 20}'

# Repeat for multiple matches, varying models if possible
```

**Record for each match:**
- Match ID and duration
- Winner and final scores
- Total phaser shots fired (estimate from replays)
- Average AE levels over time
- Any unusual behavior or patterns

### 2. Analyze Match Data (20-30 min)

Review replay JSONs in `replays/` directory:

```python
# Example analysis script
import json
import glob

replay_files = glob.glob('replays/*.json')
for replay_file in replay_files:
    with open(replay_file) as f:
        replay = json.load(f)
        # Analyze:
        # - Number of phaser hits
        # - AE patterns over time
        # - Movement/rotation usage
        # - Match duration
```

**Key questions:**
- Are phasers firing too frequently? (should be ~4 shots per 15s turn max)
- Is energy economy working? (ships should manage AE strategically, not always full or empty)
- Are matches too short/long?
- Do LLMs understand cooldown mechanics?

### 3. Tune Parameters (10-20 min, if needed)

Based on analysis, adjust `config.json` if needed:

**If phasers too strong:**
- Increase `cooldown_seconds`: 3.5 → 5.0 or 7.5
- Reduce damage slightly

**If phasers too weak:**
- Decrease `cooldown_seconds`: 3.5 → 2.5

**If energy economy broken:**
- Adjust AE rates in config.json

**Document all changes with rationale.**

### 4. Create Balance Analysis Document (20-30 min)

Create `docs/epic-004-balance-analysis.md`:

```markdown
# Epic 004: Continuous Physics Balance Analysis

## Test Matches

### Match 1: Claude vs Claude
- Match ID: [match_id]
- Duration: [X] turns
- Winner: [ship_a/ship_b]
- Final Scores: Ship A: [X shields, Y AE], Ship B: [X shields, Y AE]
- Phaser Shots: [estimate count]
- Observations: [key findings]

[Repeat for each match]

## Analysis

### Phaser Cooldown
- [Analysis of 3.5s cooldown effectiveness]
- [Firing frequency observations]
- [LLM understanding of cooldown]

### Energy Economy
- [AE management patterns]
- [Movement vs rotation costs]
- [Regeneration balance]

### Match Duration
- [Average match length]
- [Is it engaging?]

## Tuning Decisions

### Changes Made (if any)
- [Parameter changes with rationale]

### Rationale
- [Why these changes improve balance]

## Recommendation
- [Ready for production? Further tuning needed?]
```

### 5. Update Documentation (10-15 min)

Update `docs/architecture.md` or relevant docs to reflect continuous physics:

- Document phaser cooldown mechanics
- Document continuous AE economy
- Update any outdated per-turn references

### 6. Complete Dev Agent Record

Fill in the "Dev Agent Record" section in `docs/stories/story-026-balance-tuning-integration.md`:

- Implementation date
- Summary of matches run
- Files created/modified
- Balance findings
- Technical notes

**Update YAML status to "Ready for QA"** in the story file.

## Success Criteria

- ✅ At least 3 matches completed successfully
- ✅ Balance analysis document created
- ✅ Parameters tuned (if needed) with documented rationale
- ✅ Documentation updated
- ✅ Dev Agent Record filled in
- ✅ All tests still passing

## Important Notes

- **API Keys Required:** Ensure `.env` file has valid `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`
- **Match Duration:** Each match may take 2-5 minutes depending on model response times
- **Cost Awareness:** LLM API calls cost money - budget accordingly
- **Determinism:** Run same match twice to verify deterministic replays if time permits

## Deliverables

1. `docs/epic-004-balance-analysis.md` - Balance analysis report
2. Updated `config.json` (if tuning needed)
3. Updated `docs/architecture.md` (continuous physics documentation)
4. Completed Dev Agent Record in story file
5. Status changed to "Ready for QA"

---

**BEGIN IMPLEMENTATION**

Please proceed with Story 026 implementation following the steps above. When complete, hand off to QA Agent for validation.
