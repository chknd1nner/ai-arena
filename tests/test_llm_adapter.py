"""
Tests for LLM adapter prompt engineering and order parsing.

Tests Stories 008 (Prompt Engineering) and 009 (Order Parsing).
"""
import pytest
from ai_arena.llm_adapter.adapter import LLMAdapter
from ai_arena.game_engine.data_models import (
    MovementDirection, RotationCommand, GameState, ShipState,
    Vec2D, PhaserConfig
)


@pytest.fixture
def adapter():
    """Create test LLM adapter."""
    return LLMAdapter(model_a="gpt-4", model_b="gpt-4")


@pytest.fixture
def mock_game_state():
    """Create a mock game state for testing."""
    ship_a = ShipState(
        position=Vec2D(0, 0),
        velocity=Vec2D(0, 0),
        heading=0.0,
        shields=100,
        ae=100,
        phaser_config=PhaserConfig.WIDE
    )
    ship_b = ShipState(
        position=Vec2D(100, 100),
        velocity=Vec2D(0, 0),
        heading=0.0,
        shields=100,
        ae=100,
        phaser_config=PhaserConfig.WIDE
    )
    return GameState(turn=1, ship_a=ship_a, ship_b=ship_b)


# ============= Story 008: Prompt Engineering Tests =============

def test_system_prompt_includes_movement_directions(adapter, mock_game_state):
    """Verify system prompt documents all movement directions."""
    prompt = adapter._build_prompt(mock_game_state, "ship_a")
    system_prompt = prompt[0]["content"]

    assert "FORWARD" in system_prompt
    assert "FORWARD_LEFT" in system_prompt
    assert "FORWARD_RIGHT" in system_prompt
    assert "LEFT" in system_prompt
    assert "RIGHT" in system_prompt
    assert "BACKWARD" in system_prompt
    assert "BACKWARD_LEFT" in system_prompt
    assert "BACKWARD_RIGHT" in system_prompt
    assert "STOP" in system_prompt


def test_system_prompt_includes_rotation_commands(adapter, mock_game_state):
    """Verify system prompt documents all rotation commands."""
    prompt = adapter._build_prompt(mock_game_state, "ship_a")
    system_prompt = prompt[0]["content"]

    assert "NONE" in system_prompt
    assert "SOFT_LEFT" in system_prompt
    assert "SOFT_RIGHT" in system_prompt
    assert "HARD_LEFT" in system_prompt
    assert "HARD_RIGHT" in system_prompt


def test_system_prompt_includes_tactical_examples(adapter, mock_game_state):
    """Verify system prompt includes tactical maneuver examples."""
    prompt = adapter._build_prompt(mock_game_state, "ship_a")
    system_prompt = prompt[0]["content"]

    # Check for tactical maneuver names
    assert "Strafing" in system_prompt or "strafing" in system_prompt
    assert "Retreat" in system_prompt or "retreat" in system_prompt
    assert "Reposition" in system_prompt or "reposition" in system_prompt
    assert "Drift" in system_prompt or "drift" in system_prompt


def test_system_prompt_explains_independence(adapter, mock_game_state):
    """Verify system prompt explains independence of movement vs rotation."""
    prompt = adapter._build_prompt(mock_game_state, "ship_a")
    system_prompt = prompt[0]["content"]

    assert "INDEPENDENT" in system_prompt or "independent" in system_prompt
    assert "heading" in system_prompt.lower()
    assert "velocity" in system_prompt.lower()


def test_system_prompt_explains_phaser_heading(adapter, mock_game_state):
    """Verify system prompt explains phasers point at heading."""
    prompt = adapter._build_prompt(mock_game_state, "ship_a")
    system_prompt = prompt[0]["content"]

    assert "Phasers" in system_prompt or "phasers" in system_prompt
    assert "heading" in system_prompt.lower()


def test_system_prompt_includes_json_format(adapter, mock_game_state):
    """Verify system prompt specifies JSON response format."""
    prompt = adapter._build_prompt(mock_game_state, "ship_a")
    system_prompt = prompt[0]["content"]

    assert "ship_movement" in system_prompt
    assert "ship_rotation" in system_prompt
    assert "weapon_action" in system_prompt


# ============= Story 009: Order Parsing Tests =============

def test_parse_orders_with_movement_and_rotation(adapter, mock_game_state):
    """Parse valid movement and rotation commands."""
    response_json = """{
        "thinking": "Test reasoning",
        "ship_movement": "FORWARD",
        "ship_rotation": "HARD_LEFT",
        "weapon_action": "MAINTAIN_CONFIG",
        "torpedo_orders": {}
    }"""

    orders, thinking = adapter._parse_orders(response_json, mock_game_state, "ship_a")

    assert orders.movement == MovementDirection.FORWARD
    assert orders.rotation == RotationCommand.HARD_LEFT
    assert orders.weapon_action == "MAINTAIN_CONFIG"
    assert thinking == "Test reasoning"


def test_parse_orders_with_invalid_movement(adapter, mock_game_state):
    """Invalid movement should default to STOP."""
    response_json = """{
        "thinking": "Test",
        "ship_movement": "INVALID_MOVEMENT",
        "ship_rotation": "NONE",
        "weapon_action": "MAINTAIN_CONFIG"
    }"""

    orders, thinking = adapter._parse_orders(response_json, mock_game_state, "ship_a")

    assert orders.movement == MovementDirection.STOP
    assert orders.rotation == RotationCommand.NONE


def test_parse_orders_with_invalid_rotation(adapter, mock_game_state):
    """Invalid rotation should default to NONE."""
    response_json = """{
        "thinking": "Test",
        "ship_movement": "LEFT",
        "ship_rotation": "SPIN_WILDLY",
        "weapon_action": "MAINTAIN_CONFIG"
    }"""

    orders, thinking = adapter._parse_orders(response_json, mock_game_state, "ship_a")

    assert orders.movement == MovementDirection.LEFT
    assert orders.rotation == RotationCommand.NONE


def test_parse_orders_missing_rotation_field(adapter, mock_game_state):
    """Missing rotation field should default to NONE."""
    response_json = """{
        "thinking": "Test",
        "ship_movement": "RIGHT",
        "weapon_action": "MAINTAIN_CONFIG"
    }"""

    orders, thinking = adapter._parse_orders(response_json, mock_game_state, "ship_a")

    assert orders.movement == MovementDirection.RIGHT
    assert orders.rotation == RotationCommand.NONE


def test_parse_orders_missing_movement_field(adapter, mock_game_state):
    """Missing movement field should default to STOP."""
    response_json = """{
        "thinking": "Test",
        "ship_rotation": "HARD_RIGHT",
        "weapon_action": "MAINTAIN_CONFIG"
    }"""

    orders, thinking = adapter._parse_orders(response_json, mock_game_state, "ship_a")

    assert orders.movement == MovementDirection.STOP
    assert orders.rotation == RotationCommand.HARD_RIGHT


def test_parse_orders_case_insensitive(adapter, mock_game_state):
    """Parsing should be case-insensitive."""
    response_json = """{
        "thinking": "Test",
        "ship_movement": "forward",
        "ship_rotation": "Hard_Left",
        "weapon_action": "MAINTAIN_CONFIG"
    }"""

    orders, thinking = adapter._parse_orders(response_json, mock_game_state, "ship_a")

    assert orders.movement == MovementDirection.FORWARD
    assert orders.rotation == RotationCommand.HARD_LEFT


def test_parse_all_movement_directions(adapter, mock_game_state):
    """Test parsing all 9 movement directions."""
    directions = [
        "FORWARD", "FORWARD_LEFT", "FORWARD_RIGHT",
        "LEFT", "RIGHT",
        "BACKWARD", "BACKWARD_LEFT", "BACKWARD_RIGHT",
        "STOP"
    ]

    for direction_str in directions:
        response_json = f"""{{
            "thinking": "Test",
            "ship_movement": "{direction_str}",
            "ship_rotation": "NONE",
            "weapon_action": "MAINTAIN_CONFIG"
        }}"""

        orders, _ = adapter._parse_orders(response_json, mock_game_state, "ship_a")
        assert orders.movement == MovementDirection[direction_str], \
            f"Failed to parse {direction_str}"


def test_parse_all_rotation_commands(adapter, mock_game_state):
    """Test parsing all 5 rotation commands."""
    rotations = ["NONE", "SOFT_LEFT", "SOFT_RIGHT", "HARD_LEFT", "HARD_RIGHT"]

    for rotation_str in rotations:
        response_json = f"""{{
            "thinking": "Test",
            "ship_movement": "FORWARD",
            "ship_rotation": "{rotation_str}",
            "weapon_action": "MAINTAIN_CONFIG"
        }}"""

        orders, _ = adapter._parse_orders(response_json, mock_game_state, "ship_a")
        assert orders.rotation == RotationCommand[rotation_str], \
            f"Failed to parse {rotation_str}"


def test_default_orders_on_parse_failure(adapter, mock_game_state):
    """Completely malformed JSON should return default orders."""
    response_json = '{"invalid": "response"'  # Malformed JSON

    orders, thinking = adapter._parse_orders(response_json, mock_game_state, "ship_a")

    # Should return safe defaults
    assert orders.movement == MovementDirection.STOP
    assert orders.rotation == RotationCommand.NONE
    assert "ERROR" in thinking


def test_default_orders_on_empty_response(adapter, mock_game_state):
    """Empty JSON should return default orders."""
    response_json = '{}'

    orders, thinking = adapter._parse_orders(response_json, mock_game_state, "ship_a")

    # Should return safe defaults
    assert orders.movement == MovementDirection.STOP
    assert orders.rotation == RotationCommand.NONE


def test_parse_combined_movements_sample(adapter, mock_game_state):
    """Test a few sample combined movement + rotation scenarios."""
    scenarios = [
        ("FORWARD", "NONE"),
        ("LEFT", "HARD_RIGHT"),
        ("BACKWARD", "NONE"),
        ("FORWARD_LEFT", "SOFT_LEFT"),
        ("RIGHT", "HARD_LEFT"),
    ]

    for movement_str, rotation_str in scenarios:
        response_json = f"""{{
            "thinking": "Tactical maneuver",
            "ship_movement": "{movement_str}",
            "ship_rotation": "{rotation_str}",
            "weapon_action": "MAINTAIN_CONFIG"
        }}"""

        orders, _ = adapter._parse_orders(response_json, mock_game_state, "ship_a")
        assert orders.movement == MovementDirection[movement_str]
        assert orders.rotation == RotationCommand[rotation_str]


def test_default_orders_structure(adapter):
    """Verify default orders have correct structure."""
    orders = adapter._default_orders()

    assert orders.movement == MovementDirection.STOP
    assert orders.rotation == RotationCommand.NONE
    assert orders.weapon_action == "MAINTAIN_CONFIG"
    assert orders.torpedo_orders == {}


def test_parse_with_torpedo_orders(adapter, mock_game_state):
    """Verify torpedo orders still parse correctly."""
    response_json = """{
        "thinking": "Test",
        "ship_movement": "FORWARD",
        "ship_rotation": "NONE",
        "weapon_action": "MAINTAIN_CONFIG",
        "torpedo_orders": {
            "torpedo_1": "SOFT_LEFT"
        }
    }"""

    orders, _ = adapter._parse_orders(response_json, mock_game_state, "ship_a")

    assert orders.movement == MovementDirection.FORWARD
    assert orders.rotation == RotationCommand.NONE
    assert "torpedo_1" in orders.torpedo_orders
