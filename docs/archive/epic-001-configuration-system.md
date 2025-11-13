# Epic 001: Configuration Loading System

**Status:** Ready for Development
**Priority:** P0 (Foundational)
**Estimated Size:** Small (1 feature branch)
**Target for:** Claude Code Web testing

---

## Overview

Replace hardcoded physics constants with a configuration loading system that reads from `config.json`. This establishes the foundation for all game mechanics and enables easy balance tuning without code changes.

## Problem Statement

Currently, game parameters are hardcoded in `ai_arena/game_engine/physics.py`:
- Values don't match `config.json` (e.g., `SHIP_SPEED = 10.0` in code vs `3.0` in config)
- Balance changes require code modifications
- No single source of truth for game parameters
- Testing different configurations is difficult

## Goals

1. **Single Source of Truth**: All game parameters defined in `config.json`
2. **No Hardcoded Values**: Physics engine loads all constants from config
3. **Validation**: Config is validated on application startup
4. **Clear Errors**: Helpful error messages for invalid/missing config values

## Success Criteria

- [ ] All physics constants loaded from `config.json`
- [ ] Physics engine matches config values exactly
- [ ] Config validation catches missing/invalid values
- [ ] Tests verify config loading works correctly
- [ ] No hardcoded game parameters remain in physics engine

## User Stories

1. [Story 001: Load and Parse Configuration](stories/story-001-load-config.md)
2. [Story 002: Use Configuration in Physics Engine](stories/story-002-physics-constants.md)
3. [Story 003: Configuration Validation](stories/story-003-config-validation.md)

## Technical Approach

### Architecture

```
config.json
    ↓
ConfigLoader (new module)
    ↓
PhysicsEngine (modified to use config)
```

### Files to Create
- `ai_arena/config/loader.py` - Configuration loading module
- `ai_arena/config/__init__.py` - Module initialization
- `tests/test_config.py` - Configuration tests

### Files to Modify
- `ai_arena/game_engine/physics.py` - Remove hardcoded constants
- `ai_arena/orchestrator/match_orchestrator.py` - Pass config to physics engine
- `main.py` - Load config on startup

## Dependencies

None - this is foundational infrastructure.

## Risk Assessment

**Low Risk**
- Pure refactor, no new functionality
- Easy to test (config values → physics values)
- Clear rollback path (keep original constants as fallback)

## Testing Strategy

1. **Unit Tests**: Config loading and parsing
2. **Integration Tests**: Physics engine uses config correctly
3. **Validation Tests**: Invalid configs are rejected
4. **Regression Tests**: Existing physics tests still pass

## Definition of Done

- All acceptance criteria met for all user stories
- Tests pass (existing + new)
- No hardcoded physics constants in `physics.py`
- Documentation updated (CLAUDE.md mentions config system)
- Code reviewed and merged to main

## Notes for Claude Code Web

This epic is designed for one feature branch:
- Clear scope (config loading only)
- All user stories can be completed together
- Natural progression: load → use → validate
- Easy to test incrementally
- Creates foundation for future work
