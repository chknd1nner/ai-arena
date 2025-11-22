"""
Shared prompt formatting utilities for LLM adapter.

This module provides functions to format game state into prompts for LLMs.
"""
import numpy as np
from typing import List
from ai_arena.game_engine.data_models import GameState, ShipState, TorpedoState, BlastZone
from ai_arena.config import GameConfig


def format_ship_status(ship: ShipState, ship_id: str) -> str:
    """Format ship status for prompt.

    Args:
        ship: Ship state to format
        ship_id: Ship identifier (e.g., "ship_a")

    Returns:
        Formatted ship status string
    """
    return f"""- Position: ({ship.position.x:.1f}, {ship.position.y:.1f})
- Heading: {np.degrees(ship.heading):.1f}°
- Shields: {ship.shields}/100
- AE: {ship.ae}/100
- Phaser: {ship.phaser_config.value}
- Phaser Cooldown: {ship.phaser_cooldown_remaining:.1f}s (0 = ready to fire)"""


def format_enemy_status(us: ShipState, enemy: ShipState) -> str:
    """Format enemy status for prompt.

    Args:
        us: Our ship state (for distance calculation)
        enemy: Enemy ship state

    Returns:
        Formatted enemy status string
    """
    distance = us.position.distance_to(enemy.position)
    return f"""- Position: ({enemy.position.x:.1f}, {enemy.position.y:.1f})
- Shields: {enemy.shields}/100
- Distance: {distance:.1f} units"""


def format_torpedo_list(torpedoes: List[TorpedoState], count: int, max_count: int = 4) -> str:
    """Format torpedo list for prompt.

    Args:
        torpedoes: List of torpedo states
        count: Number of torpedoes
        max_count: Maximum torpedoes allowed (default: 4)

    Returns:
        Formatted torpedo list string
    """
    result = ""
    for t in torpedoes:
        result += f"\n- {t.id}: pos ({t.position.x:.1f}, {t.position.y:.1f}), AE {t.ae_remaining}"
    return result


def format_blast_zones(
    blast_zones: List[BlastZone],
    ship_id: str,
    our_position: 'Vec2D'
) -> str:
    """Format blast zone information for prompt.

    Args:
        blast_zones: List of active blast zones
        ship_id: Our ship identifier (to mark zones as "YOUR" or "ENEMY")
        our_position: Our ship position (for distance calculation)

    Returns:
        Formatted blast zone information string
    """
    if not blast_zones:
        return "\n\nBLAST ZONES: None active"

    result = f"\n\nBLAST ZONES ({len(blast_zones)} active):"
    for zone in blast_zones:
        owner_marker = "YOUR" if zone.owner == ship_id else "ENEMY"
        result += f"\n- {zone.id} ({owner_marker}):"
        result += f"\n  Position: ({zone.position.x:.1f}, {zone.position.y:.1f})"
        result += f"\n  Phase: {zone.phase.value}, Age: {zone.age:.1f}s"
        result += f"\n  Radius: {zone.current_radius:.1f} units"
        damage_rate = zone.base_damage / 15.0
        result += f"\n  Damage rate: {damage_rate:.2f}/second"
        distance = our_position.distance_to(zone.position)
        result += f"\n  Distance from you: {distance:.1f} units"
        if distance < zone.current_radius:
            result += f"\n  ⚠️  YOU ARE INSIDE THIS BLAST ZONE! Taking {damage_rate:.2f} damage/second!"

    return result


def build_user_prompt(state: GameState, ship_id: str) -> str:
    """Build user prompt from game state.

    Args:
        state: Current game state
        ship_id: "ship_a" or "ship_b"

    Returns:
        Formatted user prompt string
    """
    us = state.ship_a if ship_id == "ship_a" else state.ship_b
    enemy = state.ship_b if ship_id == "ship_a" else state.ship_a
    our_torpedoes = [t for t in state.torpedoes if t.owner == ship_id]
    enemy_torpedoes = [t for t in state.torpedoes if t.owner != ship_id]

    prompt = f"""TURN {state.turn}

YOUR STATUS ({ship_id}):
{format_ship_status(us, ship_id)}

ENEMY:
{format_enemy_status(us, enemy)}

YOUR TORPEDOES ({len(our_torpedoes)}/4):{format_torpedo_list(our_torpedoes, len(our_torpedoes))}

ENEMY TORPEDOES ({len(enemy_torpedoes)}):{format_torpedo_list(enemy_torpedoes, len(enemy_torpedoes))}{format_blast_zones(state.blast_zones, ship_id, us.position)}

Your orders (JSON only):"""

    return prompt


def format_system_prompt_with_config(system_prompt: str, config: GameConfig) -> str:
    """Format system prompt with configuration values.

    Args:
        system_prompt: Raw system prompt template with placeholders
        config: Game configuration object

    Returns:
        Formatted system prompt with values filled in
    """
    turn_duration = config.simulation.decision_interval_seconds
    cooldown = config.phaser.wide.cooldown_seconds
    max_shots = int(turn_duration / cooldown) if cooldown > 0 else 99

    return system_prompt.format(
        wide_arc=config.phaser.wide.arc_degrees,
        wide_range=config.phaser.wide.range_units,
        wide_damage=config.phaser.wide.damage,
        focused_arc=config.phaser.focused.arc_degrees,
        focused_range=config.phaser.focused.range_units,
        focused_damage=config.phaser.focused.damage,
        reconfig_time=config.phaser.reconfiguration_time_seconds,
        cooldown=cooldown,
        turn_duration=turn_duration,
        max_shots=max_shots
    )
