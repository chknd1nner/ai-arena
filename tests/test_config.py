"""
Tests for configuration loading system.
"""

import pytest
import json
import tempfile
from pathlib import Path

from ai_arena.config import ConfigLoader, GameConfig
from ai_arena.config.loader import (
    ConfigError,
    SimulationConfig,
    ShipConfig,
    MovementConfig,
    RotationConfig,
    PhaserConfig,
    TorpedoConfig,
    ArenaConfig,
)


class TestConfigLoader:
    """Test configuration loading functionality."""

    def test_load_valid_config(self):
        """Test loading the actual config.json file."""
        loader = ConfigLoader()
        config = loader.load("config.json")

        # Verify we got a GameConfig object
        assert isinstance(config, GameConfig)

    def test_config_structure(self):
        """Test that all config sections are present and typed correctly."""
        loader = ConfigLoader()
        config = loader.load("config.json")

        # Check all sections exist and have correct types
        assert isinstance(config.simulation, SimulationConfig)
        assert isinstance(config.ship, ShipConfig)
        assert isinstance(config.movement, MovementConfig)
        assert isinstance(config.rotation, RotationConfig)
        assert isinstance(config.phaser, PhaserConfig)
        assert isinstance(config.torpedo, TorpedoConfig)
        assert isinstance(config.arena, ArenaConfig)

    def test_simulation_values(self):
        """Test that simulation config values are loaded correctly."""
        loader = ConfigLoader()
        config = loader.load("config.json")

        assert config.simulation.decision_interval_seconds == 15.0
        assert config.simulation.physics_tick_rate_seconds == 0.1

    def test_ship_values(self):
        """Test that ship config values are loaded correctly."""
        loader = ConfigLoader()
        config = loader.load("config.json")

        assert config.ship.starting_shields == 100.0
        assert config.ship.starting_ae == 100.0
        assert config.ship.max_ae == 100.0
        assert config.ship.ae_regen_per_second == 0.333
        assert config.ship.base_speed_units_per_second == 3.0
        assert config.ship.collision_damage == 50.0

    def test_phaser_nested_structure(self):
        """Test that nested phaser config is loaded correctly."""
        loader = ConfigLoader()
        config = loader.load("config.json")

        # Test wide phaser
        assert config.phaser.wide.arc_degrees == 90.0
        assert config.phaser.wide.range_units == 30.0
        assert config.phaser.wide.damage == 15.0
        assert config.phaser.wide.cooldown_seconds == 3.5

        # Test focused phaser
        assert config.phaser.focused.arc_degrees == 10.0
        assert config.phaser.focused.range_units == 50.0
        assert config.phaser.focused.damage == 35.0
        assert config.phaser.focused.cooldown_seconds == 3.5

        # Test reconfiguration time
        assert config.phaser.reconfiguration_time_seconds == 15.0

    def test_torpedo_values(self):
        """Test that torpedo config values are loaded correctly."""
        loader = ConfigLoader()
        config = loader.load("config.json")

        assert config.torpedo.launch_cost_ae == 20.0
        assert config.torpedo.max_ae_capacity == 40.0
        assert config.torpedo.speed_units_per_second == 4.0
        assert config.torpedo.max_active_per_ship == 4
        assert config.torpedo.blast_radius_units == 15.0
        assert config.torpedo.blast_damage_multiplier == 1.5

    def test_file_not_found(self):
        """Test that ConfigError is raised for non-existent files."""
        loader = ConfigLoader()

        with pytest.raises(ConfigError) as exc_info:
            loader.load("nonexistent_config.json")

        assert "not found" in str(exc_info.value).lower()

    def test_invalid_json(self):
        """Test that ConfigError is raised for malformed JSON."""
        # Create a temporary file with invalid JSON
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{ invalid json content }')
            temp_path = f.name

        loader = ConfigLoader()

        try:
            with pytest.raises(ConfigError) as exc_info:
                loader.load(temp_path)

            assert "invalid json" in str(exc_info.value).lower()
        finally:
            # Clean up temp file
            Path(temp_path).unlink()

    def test_missing_section(self):
        """Test that ConfigError is raised for missing config sections."""
        # Create a temporary file with incomplete config
        incomplete_config = {
            "simulation": {
                "decision_interval_seconds": 15.0,
                "physics_tick_rate_seconds": 0.1
            }
            # Missing all other sections
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(incomplete_config, f)
            temp_path = f.name

        loader = ConfigLoader()

        try:
            with pytest.raises(ConfigError) as exc_info:
                loader.load(temp_path)

            error_msg = str(exc_info.value).lower()
            assert "missing" in error_msg or "required" in error_msg
        finally:
            # Clean up temp file
            Path(temp_path).unlink()

    def test_missing_fields(self):
        """Test that ConfigError is raised for missing fields in a section."""
        # Create config with missing fields in ship section
        incomplete_config = {
            "simulation": {
                "decision_interval_seconds": 15.0,
                "physics_tick_rate_seconds": 0.1
            },
            "ship": {
                "starting_shields": 100.0
                # Missing other required fields
            },
            "movement": {
                "forward_ae_per_second": 0.33,
                "forward_diagonal_ae_per_second": 0.53,
                "lateral_ae_per_second": 0.67,
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
                "width_units": 1000.0,
                "height_units": 500.0,
                "spawn_distance_units": 800.0
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(incomplete_config, f)
            temp_path = f.name

        loader = ConfigLoader()

        try:
            with pytest.raises(ConfigError):
                loader.load(temp_path)
        finally:
            # Clean up temp file
            Path(temp_path).unlink()


class TestConfigUsage:
    """Test that config can be used as intended."""

    def test_example_usage(self):
        """Test the example usage from the documentation."""
        loader = ConfigLoader()
        config = loader.load("config.json")

        # Verify we can access nested values as shown in docs
        assert config.ship.starting_shields == 100.0
        assert config.phaser.wide.damage == 15.0

    def test_all_values_accessible(self):
        """Test that all config values are accessible via dot notation."""
        loader = ConfigLoader()
        config = loader.load("config.json")

        # Test accessing various nested values
        assert config.simulation.decision_interval_seconds > 0
        assert config.ship.base_speed_units_per_second > 0
        assert config.movement.forward_ae_per_second >= 0
        assert config.rotation.soft_turn_degrees_per_second > 0
        assert config.phaser.wide.arc_degrees > 0
        assert config.phaser.focused.range_units > 0
        assert config.torpedo.speed_units_per_second > 0
        assert config.arena.width_units > 0


class TestConfigValidation:
    """Test configuration validation rules."""

    def test_validate_negative_speeds(self):
        """Test that negative speeds are rejected."""
        loader = ConfigLoader()

        with pytest.raises(ConfigError) as exc_info:
            loader.load("tests/fixtures/invalid_negative_values.json")

        error_msg = str(exc_info.value).lower()
        assert "invalid configuration" in error_msg
        # Should report multiple errors
        assert "decision_interval_seconds" in error_msg
        assert "starting_shields" in error_msg
        assert "base_speed_units_per_second" in error_msg
        assert "damage" in error_msg

    def test_validate_range_violations(self):
        """Test that range violations are rejected."""
        loader = ConfigLoader()

        with pytest.raises(ConfigError) as exc_info:
            loader.load("tests/fixtures/invalid_range_violations.json")

        error_msg = str(exc_info.value).lower()
        assert "invalid configuration" in error_msg
        # Check for specific violations
        assert "physics_tick_rate_seconds" in error_msg or "decision_interval" in error_msg
        assert "max_ae" in error_msg or "starting_ae" in error_msg
        assert "arc_degrees" in error_msg
        assert "spawn_distance" in error_msg

    def test_validate_zero_values(self):
        """Test that zero is rejected for required positive values."""
        # Create config with zero speed
        invalid_config = {
            "simulation": {
                "decision_interval_seconds": 15.0,
                "physics_tick_rate_seconds": 0.1
            },
            "ship": {
                "starting_shields": 0.0,  # Invalid: must be > 0
                "starting_ae": 100.0,
                "max_ae": 100.0,
                "ae_regen_per_second": 0.333,
                "base_speed_units_per_second": 0.0,  # Invalid: must be > 0
                "collision_damage": 50.0
            },
            "movement": {
                "forward_ae_per_second": 0.33,
                "forward_diagonal_ae_per_second": 0.53,
                "lateral_ae_per_second": 0.67,
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
                "speed_units_per_second": 0.0,  # Invalid: must be > 0
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
                "width_units": 1000.0,
                "height_units": 500.0,
                "spawn_distance_units": 800.0
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(invalid_config, f)
            temp_path = f.name

        loader = ConfigLoader()

        try:
            with pytest.raises(ConfigError) as exc_info:
                loader.load(temp_path)

            error_msg = str(exc_info.value).lower()
            assert "invalid configuration" in error_msg
        finally:
            Path(temp_path).unlink()

    def test_validate_multiple_errors_reported(self):
        """Test that all validation errors are reported at once."""
        loader = ConfigLoader()

        with pytest.raises(ConfigError) as exc_info:
            loader.load("tests/fixtures/invalid_negative_values.json")

        error_msg = str(exc_info.value)
        # Should contain multiple error messages (at least 3 distinct ones)
        error_lines = [line for line in error_msg.split('\n') if line.strip().startswith('-')]
        assert len(error_lines) >= 3

    def test_validate_phaser_arc_limits(self):
        """Test that phaser arc must be > 0 and <= 360."""
        # Already tested with invalid_range_violations.json (450 degrees)
        loader = ConfigLoader()

        with pytest.raises(ConfigError) as exc_info:
            loader.load("tests/fixtures/invalid_range_violations.json")

        error_msg = str(exc_info.value).lower()
        assert "arc_degrees" in error_msg
        assert "360" in error_msg or "450" in error_msg

    def test_validate_logical_consistency(self):
        """Test logical consistency checks."""
        loader = ConfigLoader()

        with pytest.raises(ConfigError) as exc_info:
            loader.load("tests/fixtures/invalid_range_violations.json")

        error_msg = str(exc_info.value).lower()
        # Check spawn_distance > arena_width is caught
        assert "spawn_distance" in error_msg
        # Check max_ae < starting_ae is caught
        assert "max_ae" in error_msg

    def test_valid_config_passes_validation(self):
        """Test that the default config.json passes all validation."""
        loader = ConfigLoader()
        # Should not raise any errors
        config = loader.load("config.json")
        assert config is not None
