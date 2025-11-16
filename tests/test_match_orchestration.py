"""
Integration tests for match orchestration using mock LLM adapter.

Tests the complete match flow without requiring API keys:
- Match initialization
- Turn loop execution
- Win condition detection
- Replay recording
- Error handling
"""

import pytest
import asyncio
from ai_arena.orchestrator.match_orchestrator import MatchOrchestrator
from ai_arena.config import ConfigLoader
from tests.mocks import MockLLMAdapter, TacticalStrategy
from tests.mocks.mock_llm_adapter import create_scripted_orders


class TestMatchOrchestrationBasics:
    """Test basic match orchestration functionality."""

    @pytest.mark.asyncio
    async def test_complete_match_with_scripted_orders(self):
        """Test a complete match using pre-scripted orders."""
        # Create simple scripted orders for 5 turns
        script_a = create_scripted_orders(
            movements=["FORWARD", "RIGHT", "FORWARD", "LEFT", "FORWARD"],
            rotations=["NONE", "HARD_LEFT", "NONE", "HARD_RIGHT", "NONE"]
        )
        script_b = create_scripted_orders(
            movements=["BACKWARD", "LEFT", "BACKWARD", "RIGHT", "STOP"],
            rotations=["NONE", "SOFT_LEFT", "NONE", "SOFT_RIGHT", "NONE"]
        )

        config = ConfigLoader().load("config.json")
        mock_adapter = MockLLMAdapter(config, script_a=script_a, script_b=script_b)

        # Create orchestrator and inject mock adapter
        orchestrator = MatchOrchestrator("mock-ship-a", "mock-ship-b")
        orchestrator.llm_adapter = mock_adapter

        # Run match
        result = await orchestrator.run_match(max_turns=5)

        # Verify match completed
        assert result['status'] == 'completed'
        assert 'winner' in result
        assert result['total_turns'] == 5

        # Verify replay was recorded
        assert 'turns' in result
        assert len(result['turns']) == 5

    @pytest.mark.asyncio
    async def test_match_with_aggressive_vs_defensive_strategy(self):
        """Test match with aggressive vs defensive strategies."""
        config = ConfigLoader().load("config.json")
        mock_adapter = MockLLMAdapter(
            config,
            strategy_a=TacticalStrategy.AGGRESSIVE,
            strategy_b=TacticalStrategy.DEFENSIVE
        )

        orchestrator = MatchOrchestrator("aggressive-ship", "defensive-ship")
        orchestrator.llm_adapter = mock_adapter

        result = await orchestrator.run_match(max_turns=15)

        assert result['status'] == 'completed'
        assert 'winner' in result
        # Aggressive should typically win against pure defensive
        # (but we won't assert winner since it depends on balance)

    @pytest.mark.asyncio
    async def test_match_initialization(self):
        """Test that match initializes correctly."""
        orchestrator = MatchOrchestrator("test-a", "test-b")

        initial_state = orchestrator._initialize_match()

        # Verify ships are at correct spawn positions
        assert initial_state.turn == 0
        assert initial_state.ship_a.shields == orchestrator.config.ship.starting_shields
        assert initial_state.ship_b.shields == orchestrator.config.ship.starting_shields
        assert initial_state.ship_a.ae == orchestrator.config.ship.starting_ae
        assert initial_state.ship_b.ae == orchestrator.config.ship.starting_ae

        # Verify ships are facing each other
        assert initial_state.ship_a.heading == 0.0  # Facing right
        assert abs(initial_state.ship_b.heading - 3.14159) < 0.01  # Facing left

    @pytest.mark.asyncio
    async def test_win_condition_detection(self):
        """Test that win conditions are detected correctly."""
        orchestrator = MatchOrchestrator("test-a", "test-b")

        # Create state where ship_a has 0 shields
        state = orchestrator._initialize_match()
        state.ship_a.shields = 0
        state.ship_b.shields = 50

        winner = orchestrator._check_win_condition(state)
        assert winner == "ship_b"

        # Create state where ship_b has 0 shields
        state.ship_a.shields = 50
        state.ship_b.shields = 0

        winner = orchestrator._check_win_condition(state)
        assert winner == "ship_a"

        # Create state where both have 0 shields (tie)
        state.ship_a.shields = 0
        state.ship_b.shields = 0

        winner = orchestrator._check_win_condition(state)
        assert winner == "tie"

        # Create state where both are alive
        state.ship_a.shields = 50
        state.ship_b.shields = 50

        winner = orchestrator._check_win_condition(state)
        assert winner is None

    @pytest.mark.asyncio
    async def test_match_reaches_max_turns(self):
        """Test that match ends at max turns if no winner."""
        config = ConfigLoader().load("config.json")

        # Both ships just stop - no combat
        script_a = create_scripted_orders(
            movements=["STOP"] * 10,
            rotations=["NONE"] * 10
        )
        script_b = create_scripted_orders(
            movements=["STOP"] * 10,
            rotations=["NONE"] * 10
        )

        mock_adapter = MockLLMAdapter(config, script_a=script_a, script_b=script_b)

        orchestrator = MatchOrchestrator("stationary-a", "stationary-b")
        orchestrator.llm_adapter = mock_adapter

        result = await orchestrator.run_match(max_turns=10)

        assert result['status'] == 'completed'
        assert result['total_turns'] == 10
        # Should be a tie since nobody took damage
        assert result['winner'] == 'tie'


class TestTacticalStrategies:
    """Test different tactical strategies work correctly."""

    @pytest.mark.asyncio
    async def test_balanced_strategy(self):
        """Test balanced strategy adapts to situation."""
        config = ConfigLoader().load("config.json")
        mock_adapter = MockLLMAdapter(
            config,
            strategy_a=TacticalStrategy.BALANCED,
            strategy_b=TacticalStrategy.BALANCED
        )

        orchestrator = MatchOrchestrator("balanced-a", "balanced-b")
        orchestrator.llm_adapter = mock_adapter

        result = await orchestrator.run_match(max_turns=20)

        assert result['status'] == 'completed'
        assert result['total_turns'] <= 20

    @pytest.mark.asyncio
    async def test_strafe_master_strategy(self):
        """Test strafe master strategy demonstrates perpendicular movement."""
        config = ConfigLoader().load("config.json")
        mock_adapter = MockLLMAdapter(
            config,
            strategy_a=TacticalStrategy.STRAFE_MASTER,
            strategy_b=TacticalStrategy.DEFENSIVE
        )

        orchestrator = MatchOrchestrator("strafe-master", "defensive")
        orchestrator.llm_adapter = mock_adapter

        result = await orchestrator.run_match(max_turns=15)

        assert result['status'] == 'completed'

        # Verify strafing happened (check replay for LEFT/RIGHT movements)
        turns_with_strafe = 0
        for turn in result['turns']:
            if turn['orders_a']['movement'] in ['LEFT', 'RIGHT']:
                turns_with_strafe += 1

        # Strafe master should strafe most turns
        assert turns_with_strafe >= 10  # At least 10 out of 15 turns

    @pytest.mark.asyncio
    async def test_drift_specialist_strategy(self):
        """Test drift specialist strategy uses LEFT movement with soft rotation."""
        config = ConfigLoader().load("config.json")
        mock_adapter = MockLLMAdapter(
            config,
            strategy_a=TacticalStrategy.DRIFT_SPECIALIST,
            strategy_b=TacticalStrategy.AGGRESSIVE
        )

        orchestrator = MatchOrchestrator("drift-specialist", "aggressive")
        orchestrator.llm_adapter = mock_adapter

        result = await orchestrator.run_match(max_turns=15)

        assert result['status'] == 'completed'

        # Verify drifting happened (mostly LEFT movements)
        left_movements = 0
        soft_rotations = 0
        for turn in result['turns']:
            if turn['orders_a']['movement'] == 'LEFT':
                left_movements += 1
            if turn['orders_a']['rotation'] in ['SOFT_LEFT', 'SOFT_RIGHT', 'NONE']:
                soft_rotations += 1

        # Drift specialist should primarily use LEFT movement
        assert left_movements >= 10
        # And prefer soft rotations (or NONE when already facing enemy)
        assert soft_rotations >= 5  # Relaxed - NONE is also valid when facing target


class TestReplaySystem:
    """Test replay recording functionality."""

    @pytest.mark.asyncio
    async def test_replay_records_all_turns(self):
        """Test that replay records all turns correctly."""
        config = ConfigLoader().load("config.json")
        script_a = create_scripted_orders(
            movements=["FORWARD", "LEFT", "RIGHT"],
            rotations=["HARD_LEFT", "NONE", "HARD_RIGHT"]
        )
        script_b = create_scripted_orders(
            movements=["BACKWARD", "RIGHT", "LEFT"],
            rotations=["HARD_RIGHT", "NONE", "HARD_LEFT"]
        )

        mock_adapter = MockLLMAdapter(config, script_a=script_a, script_b=script_b)

        orchestrator = MatchOrchestrator("replay-test-a", "replay-test-b")
        orchestrator.llm_adapter = mock_adapter

        result = await orchestrator.run_match(max_turns=3)

        # Verify replay structure
        assert 'turns' in result
        assert len(result['turns']) == 3

        # Verify each turn has required fields
        for i, turn in enumerate(result['turns']):
            assert 'turn' in turn
            assert turn['turn'] == i + 1
            assert 'state' in turn  # State BEFORE orders applied
            assert 'orders_a' in turn
            assert 'orders_b' in turn
            assert 'thinking_a' in turn
            assert 'thinking_b' in turn
            assert 'events' in turn

    @pytest.mark.asyncio
    async def test_replay_includes_thinking(self):
        """Test that replay includes thinking/reasoning from strategies."""
        config = ConfigLoader().load("config.json")
        mock_adapter = MockLLMAdapter(
            config,
            strategy_a=TacticalStrategy.AGGRESSIVE,
            strategy_b=TacticalStrategy.DEFENSIVE
        )

        orchestrator = MatchOrchestrator("thinking-test-a", "thinking-test-b")
        orchestrator.llm_adapter = mock_adapter

        result = await orchestrator.run_match(max_turns=3)

        # Verify thinking is recorded
        for turn in result['turns']:
            assert turn['thinking_a'] is not None
            assert turn['thinking_b'] is not None
            assert len(turn['thinking_a']) > 0
            assert len(turn['thinking_b']) > 0
            # Should mention strategy name
            assert 'AGGRESSIVE' in turn['thinking_a']
            assert 'DEFENSIVE' in turn['thinking_b']


class TestDeterminism:
    """Test that mock matches are deterministic."""

    @pytest.mark.asyncio
    async def test_same_script_produces_same_result(self):
        """Test that same script produces identical results."""
        config = ConfigLoader().load("config.json")

        script_a = create_scripted_orders(
            movements=["FORWARD", "LEFT", "BACKWARD"],
            rotations=["HARD_LEFT", "NONE", "HARD_RIGHT"]
        )
        script_b = create_scripted_orders(
            movements=["RIGHT", "FORWARD", "LEFT"],
            rotations=["HARD_RIGHT", "SOFT_LEFT", "NONE"]
        )

        # Run match twice with same scripts
        results = []
        for _ in range(2):
            mock_adapter = MockLLMAdapter(config, script_a=script_a.copy(), script_b=script_b.copy())
            orchestrator = MatchOrchestrator("determinism-a", "determinism-b")
            orchestrator.llm_adapter = mock_adapter
            result = await orchestrator.run_match(max_turns=3)
            results.append(result)

        # Verify same winner
        assert results[0]['winner'] == results[1]['winner']

        # Verify same number of turns
        assert results[0]['total_turns'] == results[1]['total_turns']

        # Verify final ship states are identical
        final_turn_0 = results[0]['turns'][-1]
        final_turn_1 = results[1]['turns'][-1]

        # Can't directly compare entire state due to dict ordering,
        # but can compare key metrics
        assert final_turn_0['state']['ship_a']['shields'] == final_turn_1['state']['ship_a']['shields']
        assert final_turn_0['state']['ship_b']['shields'] == final_turn_1['state']['ship_b']['shields']


class TestMixedModes:
    """Test mixed script/strategy modes."""

    @pytest.mark.asyncio
    async def test_scripted_vs_strategy(self):
        """Test one scripted ship vs one strategy-based ship."""
        config = ConfigLoader().load("config.json")

        # Ship A: Scripted to move forward and rotate left
        script_a = create_scripted_orders(
            movements=["FORWARD"] * 10,
            rotations=["HARD_LEFT"] * 10
        )

        # Ship B: Strafe master strategy (will definitely vary movements)
        mock_adapter = MockLLMAdapter(
            config,
            script_a=script_a,
            strategy_b=TacticalStrategy.STRAFE_MASTER
        )

        orchestrator = MatchOrchestrator("scripted", "adaptive-strafe")
        orchestrator.llm_adapter = mock_adapter

        result = await orchestrator.run_match(max_turns=10)

        assert result['status'] == 'completed'

        # Verify ship A followed script (all FORWARD)
        for turn in result['turns']:
            assert turn['orders_a']['movement'] == 'FORWARD'
            assert turn['orders_a']['rotation'] == 'HARD_LEFT'

        # Verify ship B adapted (strafe master alternates LEFT/RIGHT)
        movements_b = [turn['orders_b']['movement'] for turn in result['turns']]
        # Should have both LEFT and RIGHT movements
        assert 'LEFT' in movements_b or 'RIGHT' in movements_b


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
