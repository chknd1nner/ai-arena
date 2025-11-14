from dataclasses import dataclass
from typing import List, Tuple, Optional
import numpy as np
from enum import Enum

from ai_arena.game_engine.data_models import (
    GameState, Orders, Event, ShipState, TorpedoState, Vec2D,
    MovementType, MovementDirection, RotationCommand, PhaserConfig
)
from ai_arena.config import GameConfig

# ============= Core Engine =============

class PhysicsEngine:
    """
    Configuration-driven physics engine.
    Input: GameState + Orders → Output: New GameState + Events

    All physics constants are loaded from GameConfig to ensure
    single source of truth and easy balance tuning.
    """

    def __init__(self, config: GameConfig):
        """
        Initialize physics engine with game configuration.

        Args:
            config: GameConfig object containing all game parameters
        """
        self.config = config

        # Compute derived simulation values
        self.fixed_timestep = config.simulation.physics_tick_rate_seconds
        self.action_phase_duration = config.simulation.decision_interval_seconds
        self.substeps = int(self.action_phase_duration / self.fixed_timestep)

        # Cache frequently used values
        self.ship_speed = config.ship.base_speed_units_per_second
        self.torpedo_speed = config.torpedo.speed_units_per_second

        # Movement direction offsets (relative to current heading)
        # Used for independent movement system (Story 005)
        # Convention: heading 0 = East (+X), positive angles = counterclockwise
        self.MOVEMENT_DIRECTION_OFFSETS = {
            MovementDirection.FORWARD: 0.0,              # 0° - Straight ahead
            MovementDirection.FORWARD_LEFT: np.pi/4,     # +45° - Diagonal left (counterclockwise)
            MovementDirection.FORWARD_RIGHT: -np.pi/4,   # -45° - Diagonal right (clockwise)
            MovementDirection.LEFT: np.pi/2,             # +90° - Perpendicular left (counterclockwise)
            MovementDirection.RIGHT: -np.pi/2,           # -90° - Perpendicular right (clockwise)
            MovementDirection.BACKWARD: np.pi,           # 180° - Reverse
            MovementDirection.BACKWARD_LEFT: 3*np.pi/4,  # +135° - Diagonal back-left
            MovementDirection.BACKWARD_RIGHT: -3*np.pi/4,# -135° - Diagonal back-right
            MovementDirection.STOP: 0.0,                 # Special case: zero velocity
        }

        # Rotation rates (degrees per second, from config)
        # Used for independent rotation system (Story 006)
        self.ROTATION_RATES = {
            RotationCommand.NONE: 0.0,
            RotationCommand.SOFT_LEFT: config.rotation.soft_turn_degrees_per_second,
            RotationCommand.SOFT_RIGHT: -config.rotation.soft_turn_degrees_per_second,
            RotationCommand.HARD_LEFT: config.rotation.hard_turn_degrees_per_second,
            RotationCommand.HARD_RIGHT: -config.rotation.hard_turn_degrees_per_second,
        }

        # Legacy movement costs for validation (deprecated, will be removed)
        # Kept for backward compatibility during transition
        decision_interval = config.simulation.decision_interval_seconds
        self.movement_costs = {
            MovementType.STRAIGHT: int(config.movement.forward_ae_per_second * decision_interval),
            MovementType.SOFT_LEFT: int(config.movement.diagonal_ae_per_second * decision_interval),
            MovementType.SOFT_RIGHT: int(config.movement.diagonal_ae_per_second * decision_interval),
            MovementType.HARD_LEFT: int(config.movement.perpendicular_ae_per_second * decision_interval),
            MovementType.HARD_RIGHT: int(config.movement.perpendicular_ae_per_second * decision_interval),
            MovementType.REVERSE: int(config.movement.backward_ae_per_second * decision_interval),
            MovementType.REVERSE_LEFT: int(config.movement.backward_diagonal_ae_per_second * decision_interval),
            MovementType.REVERSE_RIGHT: int(config.movement.backward_diagonal_ae_per_second * decision_interval),
            MovementType.STOP: int(config.movement.stop_ae_per_second * decision_interval),
        }

        # Movement parameters (rotation angles) for torpedoes
        # Torpedoes still use the old coupled movement system
        self.movement_params = {
            MovementType.STRAIGHT: {"rotation": 0},
            MovementType.SOFT_LEFT: {"rotation": np.radians(15)},
            MovementType.SOFT_RIGHT: {"rotation": -np.radians(15)},
            MovementType.HARD_LEFT: {"rotation": np.radians(45)},
            MovementType.HARD_RIGHT: {"rotation": -np.radians(45)},
            MovementType.REVERSE: {"rotation": np.radians(180)},
            MovementType.REVERSE_LEFT: {"rotation": np.radians(30)},
            MovementType.REVERSE_RIGHT: {"rotation": -np.radians(30)},
            MovementType.STOP: {"rotation": 0},
        }

        # AE regeneration per turn
        self.ae_regen_per_turn = int(
            config.ship.ae_regen_per_second * decision_interval
        )
    
    def resolve_turn(
        self,
        state: GameState,
        orders_a: Orders,
        orders_b: Orders
    ) -> Tuple[GameState, List[Event]]:
        """
        Resolve one complete turn (60 simulated seconds).
        Uses fixed timestep for determinism.
        """
        events = []
        new_state = self._copy_state(state)
        new_state.turn += 1

        # 1. Validate and apply orders
        valid_orders_a = self._validate_orders(new_state.ship_a, orders_a)
        valid_orders_b = self._validate_orders(new_state.ship_b, orders_b)

        # 2. Deduct combined AE costs (movement + rotation) - Story 007
        movement_cost_a = self._get_movement_ae_cost(valid_orders_a.movement) * self.action_phase_duration
        rotation_cost_a = self._get_rotation_ae_cost(valid_orders_a.rotation) * self.action_phase_duration
        total_cost_a = movement_cost_a + rotation_cost_a

        movement_cost_b = self._get_movement_ae_cost(valid_orders_b.movement) * self.action_phase_duration
        rotation_cost_b = self._get_rotation_ae_cost(valid_orders_b.rotation) * self.action_phase_duration
        total_cost_b = movement_cost_b + rotation_cost_b

        # Deduct combined costs
        new_state.ship_a.ae = max(0, new_state.ship_a.ae - total_cost_a)
        new_state.ship_b.ae = max(0, new_state.ship_b.ae - total_cost_b)

        # 3. Apply weapon actions
        weapon_events_a = self._apply_weapon_action(
            new_state, "ship_a", new_state.ship_a, valid_orders_a.weapon_action
        )
        weapon_events_b = self._apply_weapon_action(
            new_state, "ship_b", new_state.ship_b, valid_orders_b.weapon_action
        )
        events.extend(weapon_events_a + weapon_events_b)

        # 4. Simulate action phase with fixed timestep
        for substep in range(self.substeps):
            self._update_ship_physics(new_state.ship_a, valid_orders_a, self.fixed_timestep)
            self._update_ship_physics(new_state.ship_b, valid_orders_b, self.fixed_timestep)

            for torpedo in new_state.torpedoes:
                torpedo_orders = valid_orders_a.torpedo_orders.get(torpedo.id) \
                    if torpedo.owner == "ship_a" \
                    else valid_orders_b.torpedo_orders.get(torpedo.id)
                self._update_torpedo_physics(torpedo, torpedo_orders, self.fixed_timestep)
        
        # 4. Check for hits after full action phase
        phaser_events = self._check_phaser_hits(new_state)
        events.extend(phaser_events)
        
        torpedo_events = self._check_torpedo_collisions(new_state)
        events.extend(torpedo_events)
        
        # 5. Regenerate AE
        new_state.ship_a.ae = min(
            new_state.ship_a.ae + self.ae_regen_per_turn,
            self.config.ship.max_ae
        )
        new_state.ship_b.ae = min(
            new_state.ship_b.ae + self.ae_regen_per_turn,
            self.config.ship.max_ae
        )
        
        # 6. Clear turn-based flags
        for torpedo in new_state.torpedoes:
            torpedo.just_launched = False
        new_state.ship_a.reconfiguring_phaser = False
        new_state.ship_b.reconfiguring_phaser = False
        
        return new_state, events
    
    def _copy_state(self, state: GameState) -> GameState:
        # A proper deepcopy would be better, but this is fine for now
        return GameState(
            turn=state.turn,
            ship_a=ShipState(**state.ship_a.__dict__),
            ship_b=ShipState(**state.ship_b.__dict__),
            torpedoes=[TorpedoState(**t.__dict__) for t in state.torpedoes]
        )

    def _get_movement_ae_cost(self, movement: MovementDirection) -> float:
        """Get AE cost per second for movement direction."""
        cost_map = {
            MovementDirection.FORWARD: self.config.movement.forward_ae_per_second,
            MovementDirection.FORWARD_LEFT: self.config.movement.diagonal_ae_per_second,
            MovementDirection.FORWARD_RIGHT: self.config.movement.diagonal_ae_per_second,
            MovementDirection.LEFT: self.config.movement.perpendicular_ae_per_second,
            MovementDirection.RIGHT: self.config.movement.perpendicular_ae_per_second,
            MovementDirection.BACKWARD: self.config.movement.backward_ae_per_second,
            MovementDirection.BACKWARD_LEFT: self.config.movement.backward_diagonal_ae_per_second,
            MovementDirection.BACKWARD_RIGHT: self.config.movement.backward_diagonal_ae_per_second,
            MovementDirection.STOP: self.config.movement.stop_ae_per_second,
        }
        return cost_map[movement]

    def _get_rotation_ae_cost(self, rotation: RotationCommand) -> float:
        """Get AE cost per second for rotation command."""
        cost_map = {
            RotationCommand.NONE: self.config.rotation.none_ae_per_second,
            RotationCommand.SOFT_LEFT: self.config.rotation.soft_turn_ae_per_second,
            RotationCommand.SOFT_RIGHT: self.config.rotation.soft_turn_ae_per_second,
            RotationCommand.HARD_LEFT: self.config.rotation.hard_turn_ae_per_second,
            RotationCommand.HARD_RIGHT: self.config.rotation.hard_turn_ae_per_second,
        }
        return cost_map[rotation]

    def _validate_orders(self, ship: ShipState, orders: Orders) -> Orders:
        """Validate orders and adjust if insufficient AE.

        Checks combined cost of movement + rotation.
        If insufficient AE, downgrades to STOP + NONE.
        """
        movement_cost = self._get_movement_ae_cost(orders.movement) * self.action_phase_duration
        rotation_cost = self._get_rotation_ae_cost(orders.rotation) * self.action_phase_duration
        total_cost = movement_cost + rotation_cost

        if total_cost > ship.ae:
            # Insufficient AE - downgrade to STOP + NONE
            orders.movement = MovementDirection.STOP
            orders.rotation = RotationCommand.NONE

        return orders

    def _apply_weapon_action(self, state: GameState, ship_id: str, ship: ShipState, weapon_action: str) -> List[Event]:
        events = []
        if weapon_action == "LAUNCH_TORPEDO":
            launch_cost = self.config.torpedo.launch_cost_ae
            max_torpedoes = self.config.torpedo.max_active_per_ship
            if ship.ae >= launch_cost and len([t for t in state.torpedoes if t.owner == ship_id]) < max_torpedoes:
                ship.ae -= launch_cost
                new_torpedo = TorpedoState(
                    id=f"{ship_id}_torpedo_{state.turn}",
                    position=ship.position,
                    velocity=Vec2D(
                        np.cos(ship.heading) * self.torpedo_speed,
                        np.sin(ship.heading) * self.torpedo_speed
                    ),
                    heading=ship.heading,
                    ae_remaining=self.config.torpedo.max_ae_capacity,
                    owner=ship_id,
                    just_launched=True
                )
                state.torpedoes.append(new_torpedo)
                events.append(Event("torpedo_launched", state.turn, {"ship": ship_id, "torpedo_id": new_torpedo.id}))
        elif weapon_action == "CONFIGURE_FOCUSED":
            if ship.phaser_config != PhaserConfig.FOCUSED:
                ship.reconfiguring_phaser = True
                ship.phaser_config = PhaserConfig.FOCUSED
                events.append(Event("phaser_reconfigured", state.turn, {"ship": ship_id, "config": "FOCUSED"}))
        elif weapon_action == "CONFIGURE_WIDE":
            if ship.phaser_config != PhaserConfig.WIDE:
                ship.reconfiguring_phaser = True
                ship.phaser_config = PhaserConfig.WIDE
                events.append(Event("phaser_reconfigured", state.turn, {"ship": ship_id, "config": "WIDE"}))

        return events

    def _update_ship_physics(self, ship: ShipState, orders: Orders, dt: float):
        """Update ship position and heading for one timestep.

        Independent movement and rotation system (Stories 005-006):
        1. Apply rotation (changes heading)
        2. Apply movement (sets velocity direction relative to heading)
        3. Update position
        """
        # 1. Apply rotation (independent of movement)
        rotation_rate_deg_per_sec = self.ROTATION_RATES[orders.rotation]
        rotation_per_dt_rad = np.radians(rotation_rate_deg_per_sec * dt)
        ship.heading += rotation_per_dt_rad
        ship.heading = ship.heading % (2 * np.pi)  # Wrap to [0, 2π)

        # 2. Apply movement (independent of rotation)
        if orders.movement == MovementDirection.STOP:
            ship.velocity = Vec2D(0, 0)
            return

        # Calculate velocity direction (heading + movement offset)
        movement_offset = self.MOVEMENT_DIRECTION_OFFSETS[orders.movement]
        velocity_angle = ship.heading + movement_offset

        # Set velocity based on movement direction
        ship.velocity = Vec2D(
            np.cos(velocity_angle) * self.ship_speed,
            np.sin(velocity_angle) * self.ship_speed
        )

        # 3. Update position
        ship.position = ship.position + (ship.velocity * dt)

    def _update_torpedo_physics(self, torpedo: TorpedoState, movement: Optional[MovementType], dt: float):
        if torpedo.just_launched:
            pass # No turning on launch turn
        elif movement:
            rotation_per_dt = self.movement_params.get(movement, {"rotation": 0})["rotation"] * dt / self.action_phase_duration
            torpedo.heading += rotation_per_dt
            torpedo.heading = torpedo.heading % (2 * np.pi)

        torpedo.velocity = Vec2D(
            np.cos(torpedo.heading) * self.torpedo_speed,
            np.sin(torpedo.heading) * self.torpedo_speed
        )
        torpedo.position = torpedo.position + (torpedo.velocity * dt)
        # Simplified AE burn (could be more sophisticated based on movement type)
        torpedo.ae_remaining -= self.config.torpedo.ae_burn_straight_per_second * dt

    def _check_phaser_hits(self, state: GameState) -> List[Event]:
        """Check if either ship's phaser hit opponent."""
        events = []
        
        if not state.ship_a.reconfiguring_phaser:
            hit = self._check_single_phaser_hit(
                state.ship_a, state.ship_b, "ship_a", "ship_b", state.turn
            )
            if hit:
                events.append(hit)
        
        if not state.ship_b.reconfiguring_phaser:
            hit = self._check_single_phaser_hit(
                state.ship_b, state.ship_a, "ship_b", "ship_a", state.turn
            )
            if hit:
                events.append(hit)
        
        return events
    
    def _check_single_phaser_hit(
        self,
        attacker: ShipState,
        target: ShipState,
        attacker_id: str,
        target_id: str,
        turn: int
    ) -> Optional[Event]:
        """Check if attacker's phaser hits target."""
        distance = attacker.position.distance_to(target.position)

        # Determine phaser parameters from config
        if attacker.phaser_config == PhaserConfig.WIDE:
            arc = np.radians(self.config.phaser.wide.arc_degrees)
            max_range = self.config.phaser.wide.range_units
            damage = self.config.phaser.wide.damage
        else:  # FOCUSED
            arc = np.radians(self.config.phaser.focused.arc_degrees)
            max_range = self.config.phaser.focused.range_units
            damage = self.config.phaser.focused.damage
        
        # Check range
        if distance > max_range:
            return None
        
        # Check if target is in firing arc
        delta = target.position - attacker.position
        angle_to_target = np.arctan2(delta.y, delta.x)
        
        angle_diff = (angle_to_target - attacker.heading) % (2 * np.pi)
        if angle_diff > np.pi:
            angle_diff -= 2 * np.pi
        
        # Check if within arc
        if abs(angle_diff) <= arc / 2:
            target.shields -= damage
            return Event(
                type="phaser_hit",
                turn=turn,
                data={
                    "attacker": attacker_id,
                    "target": target_id,
                    "damage": damage,
                    "config": attacker.phaser_config.value,
                    "distance": distance
                }
            )
        
        return None

    def _check_torpedo_collisions(self, state: GameState) -> List[Event]:
        events = []
        torpedoes_to_remove = []
        for torpedo in state.torpedoes:
            if torpedo.ae_remaining <= 0:
                torpedoes_to_remove.append(torpedo)
                continue

            for ship_id, ship in [("ship_a", state.ship_a), ("ship_b", state.ship_b)]:
                if torpedo.owner != ship_id:
                    distance = torpedo.position.distance_to(ship.position)
                    if distance < self.config.torpedo.blast_radius_units:
                        damage = int(torpedo.ae_remaining * self.config.torpedo.blast_damage_multiplier)
                        ship.shields -= damage
                        events.append(Event(
                            type="torpedo_hit",
                            turn=state.turn,
                            data={
                                "torpedo_id": torpedo.id,
                                "target": ship_id,
                                "damage": damage
                            }
                        ))
                        torpedoes_to_remove.append(torpedo)
                        break # Torpedo hits one ship and is removed
        
        state.torpedoes = [t for t in state.torpedoes if t not in torpedoes_to_remove]
        return events
