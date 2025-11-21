# Development Workflow for Claude Code Web

This guide explains how to work with Claude Code Web on the AI Arena project, optimized for its one-branch-per-session model.

---

## Claude Code Web Characteristics

**Key constraints:**
- ✅ Creates one feature branch per chat session
- ✅ Automatically creates PR when done
- ✅ Cannot switch branches mid-session
- ✅ Works best with well-scoped, single-purpose tasks

**Best practices:**
- Complete one epic or user story per session
- Keep scope small and focused
- Have clear acceptance criteria before starting
- Prepare test cases in advance

---

## Workflow: Feature Branch Development

### 1. **Before Starting Claude Code Web**

**Prepare your work:**
- [ ] Choose a specific epic or user story
- [ ] Read all acceptance criteria
- [ ] Identify all files to be modified/created
- [ ] Ensure main branch is up to date
- [ ] Have test strategy ready

**Example preparation:**
```bash
# Update main branch
git checkout main
git pull origin main

# Review the epic/story
cat docs/epic-001-configuration-system.md
cat docs/stories/story-001-load-config.md
```

### 2. **Starting a Claude Code Web Session**

**First message template:**
```
I want to implement [Epic/Story Name].

Epic: docs/epic-001-configuration-system.md
Story: docs/stories/story-001-load-config.md

Please:
1. Create feature branch: feature/config-loading-system
2. Implement all acceptance criteria
3. Write tests as specified
4. Ensure all existing tests pass
5. Create PR when complete

Let me know if you need any clarification before starting.
```

### 3. **During Development**

**Monitor progress:**
- Claude Code Web will create the branch automatically
- Watch for test failures and address them
- Review code as it's written
- Provide feedback if direction needs adjustment

**If stuck or blocked:**
- Ask for clarification
- Suggest alternative approaches
- Check if scope should be reduced

### 4. **When Session Completes**

**Claude Code Web will:**
- ✅ Create PR automatically
- ✅ Include all changes in one commit (or multiple logical commits)
- ✅ Link PR to any issues/epics mentioned

**Your review checklist:**
- [ ] All acceptance criteria met
- [ ] Tests pass locally and in CI
- [ ] Code follows project conventions
- [ ] No unintended changes
- [ ] Documentation updated if needed

### 5. **After PR is Merged**

**Cleanup:**
```bash
# Update local main
git checkout main
git pull origin main

# Delete feature branch (if not auto-deleted)
git branch -d feature/config-loading-system
```

**Plan next session:**
- Mark completed story/epic as done
- Choose next story from backlog
- Prepare for next Claude Code Web session

---

## Project-Specific Guidelines

### Epic 001: Configuration System

**Recommended approach:**
- **Session 1**: Complete all three user stories together (they're tightly coupled)
- **Branch name**: `feature/config-loading-system`
- **Scope**: Config loader + physics integration + validation
- **Estimated time**: 1-2 hours for Claude Code Web

**Why do all stories together:**
1. Config loader alone isn't useful without consumers
2. Physics integration requires config loader to exist
3. Validation should be built in from the start
4. Natural order: build → use → validate

**Alternative approach:**
- **Session 1**: Story 001 only (config loader)
- **Session 2**: Story 002 (physics integration)
- **Session 3**: Story 003 (validation)

Choose based on:
- Your comfort with Claude Code Web
- Whether you want to review incrementally
- Preference for larger vs smaller PRs

### Testing Strategy

For comprehensive testing guidelines including test file organization, unit testing strategies, visual/gameplay testing, and debugging, see **`docs/testing-guidelines.md`**.

**Quick checklist before creating PR:**
```bash
pytest                           # All tests pass
pytest tests/ -v                 # Verify all tests with details
```

(For detailed testing procedures, visual validation, and Playwright automation, refer to `docs/testing-guidelines.md`)

### Common Pitfalls

**❌ Scope creep**
- Starting with config system, then adding frontend visualization
- Solution: Stick to the user story, create new epic for extras

**❌ Unclear acceptance criteria**
- "Make config system better"
- Solution: Use specific criteria from user stories

**❌ Missing tests**
- Code works but no tests
- Solution: User stories specify required tests

**❌ Breaking existing functionality**
- New code breaks unrelated tests
- Solution: Run full test suite before PR

---

## User Story Template

When creating new user stories for Claude Code Web, use this format:

```markdown
# Story XXX: [Clear, Specific Title]

**Epic:** Link to epic
**Status:** Ready for Development
**Size:** Small/Medium/Large
**Priority:** P0/P1/P2

## User Story
As a [role]
I want [feature]
So that [benefit]

## Acceptance Criteria
- [ ] Specific, testable criterion 1
- [ ] Specific, testable criterion 2
- [ ] ...

## Technical Details
### Files to Create
- path/to/new/file.py

### Files to Modify
- path/to/existing/file.py

### Implementation Notes
[Specific guidance for Claude Code Web]

## Test Requirements
[Exactly which tests to write]

## Definition of Done
- [ ] All acceptance criteria met
- [ ] Tests written and passing
- [ ] Code reviewed
- [ ] Documentation updated
```

---

## Branch Naming Convention

Use descriptive, kebab-case names:
- `feature/config-loading-system`
- `feature/independent-movement-rotation`
- `feature/replay-viewer-ui`
- `fix/phaser-cooldown-bug`
- `refactor/llm-adapter-error-handling`

**Pattern:** `<type>/<short-description>`

**Types:**
- `feature/` - New functionality
- `fix/` - Bug fixes
- `refactor/` - Code improvements without behavior change
- `docs/` - Documentation only
- `test/` - Test improvements

---

## Success Metrics

**Good Claude Code Web session:**
- ✅ Clear scope accomplished
- ✅ All tests pass
- ✅ PR can be merged with minimal changes
- ✅ Next session can build on this work

**Session that needs improvement:**
- ❌ Scope was too large, some work unfinished
- ❌ Tests failing, unclear how to fix
- ❌ PR needs significant rework
- ❌ Unclear what to do next

**Learn from each session and adjust planning accordingly.**

---

## Next Steps After Epic 001

Once configuration system is complete, consider:

1. **Epic 002: Independent Movement & Rotation**
   - Implement decoupled movement system from game spec
   - Size: Medium (2-3 sessions)

2. **Epic 003: Phaser Cooldown System**
   - Add continuous cooldown tracking
   - Size: Small (1 session)

3. **Epic 004: Frontend Replay Viewer**
   - Build Canvas-based visualization
   - Size: Large (3-4 sessions)

4. **Epic 005: Continuous AE Economy**
   - Implement per-second burn rates
   - Size: Medium (2 sessions)

Choose based on priorities and what you want to test with Claude Code Web.
