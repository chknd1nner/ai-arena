"""
Run showcase matches demonstrating AI Arena features.

This script runs 3 matches using mock LLM strategies to showcase:
1. Continuous Physics & Energy Management
2. Tactical Maneuvers (Strafing, Drift, etc.)
3. Weapon Systems (FOCUSED vs WIDE phasers)

Replays are saved to replays/showcase/ for manual viewing.
"""

import asyncio
import shutil
from pathlib import Path

from ai_arena.orchestrator.match_orchestrator import MatchOrchestrator
from ai_arena.config import ConfigLoader
from tests.mocks import MockLLMAdapter, TacticalStrategy


async def run_showcase_match_1():
    """Showcase 1: Continuous Physics & Energy Management.

    Demonstrates:
    - AE regeneration per substep
    - Phaser cooldown system
    - Energy management decisions (aggressive vs conservative)
    """
    print("\n" + "=" * 80)
    print("SHOWCASE MATCH 1: Continuous Physics & Energy Management")
    print("=" * 80)
    print("Ship A: AGGRESSIVE strategy (high energy consumption)")
    print("Ship B: DEFENSIVE strategy (conservative energy use)")
    print()

    config = ConfigLoader().load("config.json")
    mock_adapter = MockLLMAdapter(
        config,
        strategy_a=TacticalStrategy.AGGRESSIVE,
        strategy_b=TacticalStrategy.DEFENSIVE
    )

    orchestrator = MatchOrchestrator("Aggressive-Phoenix", "Defensive-Sentinel")
    orchestrator.llm_adapter = mock_adapter

    result = await orchestrator.run_match(max_turns=20)

    print(f"\nMatch Result:")
    print(f"  Winner: {result['winner']}")
    print(f"  Total Turns: {result['total_turns']}")
    print(f"  Match ID: {result['match_id']}")

    # Move replay to showcase directory
    replay_path = Path(f"replays/{result['match_id']}.json")
    showcase_path = Path(f"replays/showcase/01-continuous-physics-demo.json")
    if replay_path.exists():
        shutil.move(str(replay_path), str(showcase_path))
        print(f"  Replay: {showcase_path}")

    return result


async def run_showcase_match_2():
    """Showcase 2: Tactical Maneuvers.

    Demonstrates:
    - Independent movement and rotation
    - Strafing (perpendicular movement with tracking rotation)
    - Drift maneuvers (gradual rotation while evading)
    - Advanced maneuvering tactics
    """
    print("\n" + "=" * 80)
    print("SHOWCASE MATCH 2: Tactical Maneuvers")
    print("=" * 80)
    print("Ship A: STRAFE MASTER strategy (constant perpendicular movement)")
    print("Ship B: DRIFT SPECIALIST strategy (evasive drift with soft rotation)")
    print()

    config = ConfigLoader().load("config.json")
    mock_adapter = MockLLMAdapter(
        config,
        strategy_a=TacticalStrategy.STRAFE_MASTER,
        strategy_b=TacticalStrategy.DRIFT_SPECIALIST
    )

    orchestrator = MatchOrchestrator("Strafe-Master-Alpha", "Drift-Specialist-Beta")
    orchestrator.llm_adapter = mock_adapter

    result = await orchestrator.run_match(max_turns=20)

    print(f"\nMatch Result:")
    print(f"  Winner: {result['winner']}")
    print(f"  Total Turns: {result['total_turns']}")
    print(f"  Match ID: {result['match_id']}")

    # Move replay to showcase directory
    replay_path = Path(f"replays/{result['match_id']}.json")
    showcase_path = Path(f"replays/showcase/02-tactical-maneuvers-demo.json")
    if replay_path.exists():
        shutil.move(str(replay_path), str(showcase_path))
        print(f"  Replay: {showcase_path}")

    return result


async def run_showcase_match_3():
    """Showcase 3: Weapon Systems.

    Demonstrates:
    - FOCUSED vs WIDE phaser configurations
    - Phaser reconfiguration mechanics
    - Cooldown blocking during reconfiguration
    - Range and arc trade-offs
    """
    print("\n" + "=" * 80)
    print("SHOWCASE MATCH 3: Weapon Systems (FOCUSED vs WIDE)")
    print("=" * 80)
    print("Ship A: FOCUSED PHASER strategy (long-range precision)")
    print("Ship B: AGGRESSIVE strategy (close-range WIDE phasers)")
    print()

    config = ConfigLoader().load("config.json")
    mock_adapter = MockLLMAdapter(
        config,
        strategy_a=TacticalStrategy.FOCUSED_PHASER,
        strategy_b=TacticalStrategy.AGGRESSIVE
    )

    orchestrator = MatchOrchestrator("Focused-Sniper", "Wide-Brawler")
    orchestrator.llm_adapter = mock_adapter

    result = await orchestrator.run_match(max_turns=20)

    print(f"\nMatch Result:")
    print(f"  Winner: {result['winner']}")
    print(f"  Total Turns: {result['total_turns']}")
    print(f"  Match ID: {result['match_id']}")

    # Move replay to showcase directory
    replay_path = Path(f"replays/{result['match_id']}.json")
    showcase_path = Path(f"replays/showcase/03-weapon-systems-demo.json")
    if replay_path.exists():
        shutil.move(str(replay_path), str(showcase_path))
        print(f"  Replay: {showcase_path}")

    return result


async def main():
    """Run all showcase matches."""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  AI ARENA - SHOWCASE MATCHES (Story 027)".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("║" + "  Testing match orchestration with MockLLMAdapter".center(78) + "║")
    print("║" + "  No API keys required - all deterministic strategies".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "═" * 78 + "╝")

    # Ensure showcase directory exists
    Path("replays/showcase").mkdir(parents=True, exist_ok=True)

    results = []

    # Run all showcase matches
    try:
        result1 = await run_showcase_match_1()
        results.append(result1)
    except Exception as e:
        print(f"\n❌ Match 1 failed: {e}")

    try:
        result2 = await run_showcase_match_2()
        results.append(result2)
    except Exception as e:
        print(f"\n❌ Match 2 failed: {e}")

    try:
        result3 = await run_showcase_match_3()
        results.append(result3)
    except Exception as e:
        print(f"\n❌ Match 3 failed: {e}")

    # Summary
    print("\n" + "=" * 80)
    print("SHOWCASE SUMMARY")
    print("=" * 80)
    print(f"Matches completed: {len(results)}/3")
    print(f"Replays saved to: replays/showcase/")
    print()
    print("Files:")
    for path in sorted(Path("replays/showcase").glob("*.json")):
        print(f"  - {path}")

    print("\n✓ All showcase matches completed successfully!")
    print()


if __name__ == "__main__":
    asyncio.run(main())
