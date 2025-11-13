"""
Configuration loader for AI Arena.

Loads and validates game configuration from config.json.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


class ConfigError(Exception):
    """Raised when config cannot be loaded or is invalid."""
    pass


@dataclass
class SimulationConfig:
    """Simulation timing parameters."""
    decision_interval_seconds: float
    physics_tick_rate_seconds: float


@dataclass
class ShipConfig:
    """Ship base parameters."""
    starting_shields: float
    starting_ae: float
    max_ae: float
    ae_regen_per_second: float
    base_speed_units_per_second: float
    collision_damage: float


@dataclass
class MovementConfig:
    """Movement AE costs per second."""
    forward_ae_per_second: float
    forward_diagonal_ae_per_second: float
    lateral_ae_per_second: float
    backward_ae_per_second: float
    backward_diagonal_ae_per_second: float
    stop_ae_per_second: float


@dataclass
class RotationConfig:
    """Rotation parameters and AE costs."""
    none_ae_per_second: float
    soft_turn_ae_per_second: float
    soft_turn_degrees_per_second: float
    hard_turn_ae_per_second: float
    hard_turn_degrees_per_second: float


@dataclass
class PhaserModeConfig:
    """Configuration for a single phaser mode (wide or focused)."""
    arc_degrees: float
    range_units: float
    damage: float
    cooldown_seconds: float


@dataclass
class PhaserConfig:
    """Phaser weapon configuration."""
    wide: PhaserModeConfig
    focused: PhaserModeConfig
    reconfiguration_time_seconds: float


@dataclass
class TorpedoConfig:
    """Torpedo weapon configuration."""
    launch_cost_ae: float
    max_ae_capacity: float
    speed_units_per_second: float
    turn_rate_degrees_per_second: float
    max_active_per_ship: int
    ae_burn_straight_per_second: float
    ae_burn_soft_turn_per_second: float
    ae_burn_hard_turn_per_second: float
    blast_expansion_seconds: float
    blast_duration_seconds: float
    blast_dissipation_seconds: float
    blast_radius_units: float
    blast_damage_multiplier: float


@dataclass
class ArenaConfig:
    """Arena dimensions and spawn configuration."""
    width_units: float
    height_units: float
    spawn_distance_units: float


@dataclass
class GameConfig:
    """Complete game configuration."""
    simulation: SimulationConfig
    ship: ShipConfig
    movement: MovementConfig
    rotation: RotationConfig
    phaser: PhaserConfig
    torpedo: TorpedoConfig
    arena: ArenaConfig


class ConfigLoader:
    """Loads and validates game configuration from JSON files."""

    def load(self, filepath: str = "config.json") -> GameConfig:
        """
        Load configuration from a JSON file.

        Args:
            filepath: Path to the configuration file (relative to project root)

        Returns:
            GameConfig object with all configuration data

        Raises:
            ConfigError: If file cannot be loaded or config is invalid
        """
        try:
            # Convert to Path object for easier handling
            config_path = Path(filepath)

            # Read the JSON file
            with open(config_path, 'r') as f:
                data = json.load(f)

            # Parse into typed dataclasses
            config = self._parse_config(data)

            # Validate configuration values
            self._validate(config)

            return config

        except FileNotFoundError as e:
            raise ConfigError(
                f"Configuration file not found: {filepath}\n"
                f"Please ensure config.json exists in the project root."
            ) from e
        except json.JSONDecodeError as e:
            raise ConfigError(
                f"Invalid JSON in configuration file: {filepath}\n"
                f"Error at line {e.lineno}, column {e.colno}: {e.msg}"
            ) from e
        except (KeyError, TypeError) as e:
            raise ConfigError(
                f"Invalid configuration structure: {e}\n"
                f"Please ensure all required fields are present."
            ) from e

    def _parse_config(self, data: Dict) -> GameConfig:
        """Parse raw JSON data into typed GameConfig object."""
        try:
            # Parse simulation config
            simulation = SimulationConfig(**data['simulation'])

            # Parse ship config
            ship = ShipConfig(**data['ship'])

            # Parse movement config
            movement = MovementConfig(**data['movement'])

            # Parse rotation config
            rotation = RotationConfig(**data['rotation'])

            # Parse phaser config (nested structure)
            phaser_data = data['phaser']
            phaser = PhaserConfig(
                wide=PhaserModeConfig(**phaser_data['wide']),
                focused=PhaserModeConfig(**phaser_data['focused']),
                reconfiguration_time_seconds=phaser_data['reconfiguration_time_seconds']
            )

            # Parse torpedo config
            torpedo = TorpedoConfig(**data['torpedo'])

            # Parse arena config
            arena = ArenaConfig(**data['arena'])

            # Combine into GameConfig
            return GameConfig(
                simulation=simulation,
                ship=ship,
                movement=movement,
                rotation=rotation,
                phaser=phaser,
                torpedo=torpedo,
                arena=arena
            )
        except KeyError as e:
            raise ConfigError(f"Missing required configuration field: {e}")
        except TypeError as e:
            raise ConfigError(f"Invalid configuration value type: {e}")

    def _validate(self, config: GameConfig):
        """
        Validate configuration values.

        Checks that all values are within acceptable ranges and logically consistent.

        Args:
            config: GameConfig object to validate

        Raises:
            ConfigError: If any validation rules are violated
        """
        errors = []

        # Simulation validation
        if config.simulation.decision_interval_seconds <= 0:
            errors.append(
                f"simulation.decision_interval_seconds must be > 0 "
                f"(got: {config.simulation.decision_interval_seconds})"
            )
        if config.simulation.physics_tick_rate_seconds <= 0:
            errors.append(
                f"simulation.physics_tick_rate_seconds must be > 0 "
                f"(got: {config.simulation.physics_tick_rate_seconds})"
            )
        if config.simulation.physics_tick_rate_seconds > config.simulation.decision_interval_seconds:
            errors.append(
                f"simulation.physics_tick_rate_seconds must be <= decision_interval_seconds "
                f"(got: {config.simulation.physics_tick_rate_seconds} > {config.simulation.decision_interval_seconds})"
            )

        # Ship validation
        if config.ship.starting_shields <= 0:
            errors.append(
                f"ship.starting_shields must be > 0 (got: {config.ship.starting_shields})"
            )
        if config.ship.starting_ae <= 0:
            errors.append(
                f"ship.starting_ae must be > 0 (got: {config.ship.starting_ae})"
            )
        if config.ship.max_ae < config.ship.starting_ae:
            errors.append(
                f"ship.max_ae must be >= starting_ae "
                f"(got: {config.ship.max_ae} < {config.ship.starting_ae})"
            )
        if config.ship.ae_regen_per_second < 0:
            errors.append(
                f"ship.ae_regen_per_second must be >= 0 (got: {config.ship.ae_regen_per_second})"
            )
        if config.ship.base_speed_units_per_second <= 0:
            errors.append(
                f"ship.base_speed_units_per_second must be > 0 "
                f"(got: {config.ship.base_speed_units_per_second})"
            )
        if config.ship.collision_damage < 0:
            errors.append(
                f"ship.collision_damage must be >= 0 (got: {config.ship.collision_damage})"
            )

        # Movement validation
        if config.movement.forward_ae_per_second < 0:
            errors.append(
                f"movement.forward_ae_per_second must be >= 0 "
                f"(got: {config.movement.forward_ae_per_second})"
            )
        if config.movement.stop_ae_per_second < 0:
            errors.append(
                f"movement.stop_ae_per_second must be >= 0 "
                f"(got: {config.movement.stop_ae_per_second})"
            )

        # Rotation validation
        if config.rotation.soft_turn_degrees_per_second < 0:
            errors.append(
                f"rotation.soft_turn_degrees_per_second must be >= 0 "
                f"(got: {config.rotation.soft_turn_degrees_per_second})"
            )
        if config.rotation.hard_turn_degrees_per_second < 0:
            errors.append(
                f"rotation.hard_turn_degrees_per_second must be >= 0 "
                f"(got: {config.rotation.hard_turn_degrees_per_second})"
            )

        # Phaser validation (wide)
        if config.phaser.wide.arc_degrees <= 0 or config.phaser.wide.arc_degrees > 360:
            errors.append(
                f"phaser.wide.arc_degrees must be > 0 and <= 360 "
                f"(got: {config.phaser.wide.arc_degrees})"
            )
        if config.phaser.wide.range_units <= 0:
            errors.append(
                f"phaser.wide.range_units must be > 0 (got: {config.phaser.wide.range_units})"
            )
        if config.phaser.wide.damage <= 0:
            errors.append(
                f"phaser.wide.damage must be > 0 (got: {config.phaser.wide.damage})"
            )
        if config.phaser.wide.cooldown_seconds < 0:
            errors.append(
                f"phaser.wide.cooldown_seconds must be >= 0 "
                f"(got: {config.phaser.wide.cooldown_seconds})"
            )

        # Phaser validation (focused)
        if config.phaser.focused.arc_degrees <= 0 or config.phaser.focused.arc_degrees > 360:
            errors.append(
                f"phaser.focused.arc_degrees must be > 0 and <= 360 "
                f"(got: {config.phaser.focused.arc_degrees})"
            )
        if config.phaser.focused.range_units <= 0:
            errors.append(
                f"phaser.focused.range_units must be > 0 "
                f"(got: {config.phaser.focused.range_units})"
            )
        if config.phaser.focused.damage <= 0:
            errors.append(
                f"phaser.focused.damage must be > 0 (got: {config.phaser.focused.damage})"
            )
        if config.phaser.focused.cooldown_seconds < 0:
            errors.append(
                f"phaser.focused.cooldown_seconds must be >= 0 "
                f"(got: {config.phaser.focused.cooldown_seconds})"
            )

        # Torpedo validation
        if config.torpedo.launch_cost_ae <= 0:
            errors.append(
                f"torpedo.launch_cost_ae must be > 0 (got: {config.torpedo.launch_cost_ae})"
            )
        if config.torpedo.max_ae_capacity <= 0:
            errors.append(
                f"torpedo.max_ae_capacity must be > 0 (got: {config.torpedo.max_ae_capacity})"
            )
        if config.torpedo.speed_units_per_second <= 0:
            errors.append(
                f"torpedo.speed_units_per_second must be > 0 "
                f"(got: {config.torpedo.speed_units_per_second})"
            )
        if config.torpedo.max_active_per_ship <= 0:
            errors.append(
                f"torpedo.max_active_per_ship must be > 0 "
                f"(got: {config.torpedo.max_active_per_ship})"
            )
        if config.torpedo.blast_radius_units <= 0:
            errors.append(
                f"torpedo.blast_radius_units must be > 0 "
                f"(got: {config.torpedo.blast_radius_units})"
            )
        if config.torpedo.blast_damage_multiplier <= 0:
            errors.append(
                f"torpedo.blast_damage_multiplier must be > 0 "
                f"(got: {config.torpedo.blast_damage_multiplier})"
            )

        # Arena validation
        if config.arena.width_units <= 0:
            errors.append(
                f"arena.width_units must be > 0 (got: {config.arena.width_units})"
            )
        if config.arena.height_units <= 0:
            errors.append(
                f"arena.height_units must be > 0 (got: {config.arena.height_units})"
            )
        if config.arena.spawn_distance_units <= 0:
            errors.append(
                f"arena.spawn_distance_units must be > 0 "
                f"(got: {config.arena.spawn_distance_units})"
            )

        # Logical consistency checks
        if config.arena.spawn_distance_units > config.arena.width_units:
            errors.append(
                f"arena.spawn_distance_units must be <= width_units "
                f"(got: {config.arena.spawn_distance_units} > {config.arena.width_units})"
            )

        # Raise error if any validation failed
        if errors:
            error_msg = "Invalid configuration:\n" + "\n".join(f"  - {e}" for e in errors)
            raise ConfigError(error_msg)
