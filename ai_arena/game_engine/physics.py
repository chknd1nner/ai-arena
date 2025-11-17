from dataclasses import dataclass
from typing import List, Tuple, Optional
import numpy as np
from enum import Enum
import logging

logger = logging.getLogger(__name__)

from ai_arena.game_engine.data_models import (
    GameState, Orders, Event, ShipState, TorpedoState, Vec2D,
    MovementType, MovementDirection, RotationCommand, PhaserConfig,
    BlastZone, BlastZonePhase
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

        # 2. Apply weapon actions
        weapon_events_a = self._apply_weapon_action(
            new_state, "ship_a", new_state.ship_a, valid_orders_a.weapon_action
        )
        weapon_events_b = self._apply_weapon_action(
            new_state, "ship_b", new_state.ship_b, valid_orders_b.weapon_action
        )
        events.extend(weapon_events_a + weapon_events_b)

        # 2.5. Apply torpedo orders (set detonation timers)
        self._apply_torpedo_orders(new_state, valid_orders_a, valid_orders_b)

        # 3. Simulate action phase with fixed timestep
        # AE costs, regeneration, and cooldown decrement happen per substep in _update_ship_physics()
        for substep in range(self.substeps):
            self._update_ship_physics(new_state.ship_a, valid_orders_a, self.fixed_timestep)
            self._update_ship_physics(new_state.ship_b, valid_orders_b, self.fixed_timestep)

            for torpedo in new_state.torpedoes:
                torpedo_action_str = valid_orders_a.torpedo_orders.get(torpedo.id) \
                    if torpedo.owner == "ship_a" \
                    else valid_orders_b.torpedo_orders.get(torpedo.id)
                self._update_torpedo_physics(torpedo, torpedo_action_str, self.fixed_timestep)

            # Update blast zone lifecycles (expansion/persistence/dissipation)
            # Called BEFORE detonations so newly created zones don't update same substep
            self._update_blast_zones(new_state.blast_zones, self.fixed_timestep)

            # Handle torpedo detonations (creates blast zones)
            self._handle_torpedo_detonations(new_state, events, self.fixed_timestep)

        # 4. Check for hits after full action phase
        phaser_events = self._check_phaser_hits(new_state)
        events.extend(phaser_events)

        torpedo_events = self._check_torpedo_collisions(new_state)
        events.extend(torpedo_events)

        # 5. Clear turn-based flags
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
            torpedoes=[TorpedoState(**t.__dict__) for t in state.torpedoes],
            blast_zones=[BlastZone(**bz.__dict__) for bz in state.blast_zones]
        )

    def _get_movement_ae_rate(self, movement: MovementDirection) -> float:
        """Get AE cost rate for movement direction.

        Args:
            movement: Movement direction command
            config: Game configuration

        Returns:
            AE cost in AE per second
        """
        rates = {
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
        return rates[movement]

    def _get_rotation_ae_rate(self, rotation: RotationCommand) -> float:
        """Get AE cost rate for rotation command.

        Args:
            rotation: Rotation command
            config: Game configuration

        Returns:
            AE cost in AE per second
        """
        rates = {
            RotationCommand.NONE: self.config.rotation.none_ae_per_second,
            RotationCommand.SOFT_LEFT: self.config.rotation.soft_turn_ae_per_second,
            RotationCommand.SOFT_RIGHT: self.config.rotation.soft_turn_ae_per_second,
            RotationCommand.HARD_LEFT: self.config.rotation.hard_turn_ae_per_second,
            RotationCommand.HARD_RIGHT: self.config.rotation.hard_turn_ae_per_second,
        }
        return rates[rotation]

    def _validate_orders(self, ship: ShipState, orders: Orders) -> Orders:
        """Validate orders and adjust if insufficient AE.

        Checks combined cost of movement + rotation.
        If insufficient AE, downgrades to STOP + NONE.
        """
        movement_cost = self._get_movement_ae_rate(orders.movement) * self.action_phase_duration
        rotation_cost = self._get_rotation_ae_rate(orders.rotation) * self.action_phase_duration
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

    def _apply_torpedo_orders(self, state: GameState, orders_a: Orders, orders_b: Orders):
        """Apply torpedo orders at start of turn.

        Sets detonation timers for torpedoes with detonate_after commands.
        Movement commands will be applied during substeps.

        Args:
            state: Current game state
            orders_a: Orders for ship A
            orders_b: Orders for ship B
        """
        for torpedo in state.torpedoes:
            # Get orders for this torpedo from the owning ship
            orders = orders_a if torpedo.owner == "ship_a" else orders_b
            action_str = orders.torpedo_orders.get(torpedo.id)

            if action_str:
                try:
                    action_type, delay = self._parse_torpedo_action(action_str)
                    if action_type == "detonate_after":
                        # Set detonation timer
                        torpedo.detonation_timer = delay
                    # Movement commands will be handled in _update_torpedo_physics
                except ValueError as e:
                    logger.warning(f"Invalid torpedo action '{action_str}' for {torpedo.id}: {e}")

    def _apply_ae_regeneration(self, ship: ShipState, dt: float):
        """Apply AE regeneration for one substep.

        Regenerates AE continuously per substep, capping at maximum AE.
        Part of Story 021: Continuous AE tracking system.

        Args:
            ship: Ship to regenerate AE for
            dt: Time delta in seconds for this substep
        """
        regen_amount = self.config.ship.ae_regen_per_second * dt
        ship.ae += regen_amount
        # Cap AE at maximum
        ship.ae = min(ship.ae, self.config.ship.max_ae)

    def _update_ship_physics(self, ship: ShipState, orders: Orders, dt: float):
        """Update ship position and heading for one timestep.

        Independent movement and rotation system (Stories 005-006):
        1. Apply rotation (changes heading)
        2. Apply movement (sets velocity direction relative to heading)
        3. Update position
        4. Apply movement AE cost per substep (Story 022)
        5. Apply rotation AE cost per substep (Story 023)
        6. Regenerate AE (Story 021)
        7. Decrement phaser cooldown (Story 021)
        """
        # 1. Apply rotation (independent of movement)
        rotation_rate_deg_per_sec = self.ROTATION_RATES[orders.rotation]
        rotation_per_dt_rad = np.radians(rotation_rate_deg_per_sec * dt)
        ship.heading += rotation_per_dt_rad
        ship.heading = ship.heading % (2 * np.pi)  # Wrap to [0, 2π)

        # 2. Apply movement (independent of rotation)
        if orders.movement == MovementDirection.STOP:
            ship.velocity = Vec2D(0, 0)
        else:
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

        # 4. Apply movement AE cost per substep (Story 022)
        movement_ae_rate = self._get_movement_ae_rate(orders.movement)
        ae_cost_movement = movement_ae_rate * dt
        ship.ae -= ae_cost_movement

        # 5. Apply rotation AE cost per substep (Story 023)
        rotation_ae_rate = self._get_rotation_ae_rate(orders.rotation)
        ae_cost_rotation = rotation_ae_rate * dt
        ship.ae -= ae_cost_rotation

        # 6. Regenerate AE per substep (Story 021)
        self._apply_ae_regeneration(ship, dt)

        # 7. Clamp AE at zero (no negative values)
        ship.ae = max(0.0, ship.ae)

        # 8. Decrement phaser cooldown per substep (Story 021)
        if ship.phaser_cooldown_remaining > 0.0:
            ship.phaser_cooldown_remaining -= dt
            ship.phaser_cooldown_remaining = max(0.0, ship.phaser_cooldown_remaining)

    def _update_torpedo_physics(self, torpedo: TorpedoState, action_str: Optional[str], dt: float):
        """Update torpedo physics for one timestep.

        Args:
            torpedo: Torpedo to update
            action_str: Action string (e.g., "HARD_LEFT" or "detonate_after:8.5" or None)
            dt: Time delta for this substep
        """
        # Parse action to determine if it's a movement command
        movement = None
        if action_str and not torpedo.just_launched:
            try:
                action_type, _ = self._parse_torpedo_action(action_str)
                # Only process movement commands (ignore detonate_after)
                if action_type != "detonate_after":
                    # Parse as MovementType
                    try:
                        movement = MovementType[action_type.upper()]
                    except KeyError:
                        logger.warning(f"Invalid torpedo movement '{action_type}', defaulting to STRAIGHT")
                        movement = MovementType.STRAIGHT
            except ValueError:
                # Invalid action format, ignore
                pass

        # Apply movement (rotation)
        if not torpedo.just_launched and movement:
            rotation_per_dt = self.movement_params.get(movement, {"rotation": 0})["rotation"] * dt / self.action_phase_duration
            torpedo.heading += rotation_per_dt
            torpedo.heading = torpedo.heading % (2 * np.pi)

        # Update velocity and position
        torpedo.velocity = Vec2D(
            np.cos(torpedo.heading) * self.torpedo_speed,
            np.sin(torpedo.heading) * self.torpedo_speed
        )
        torpedo.position = torpedo.position + (torpedo.velocity * dt)

        # AE burn
        torpedo.ae_remaining -= self.config.torpedo.ae_burn_straight_per_second * dt

    def _parse_torpedo_action(self, action_str: str) -> Tuple[str, Optional[float]]:
        """Parse torpedo action string.

        Args:
            action_str: e.g., "HARD_LEFT" or "detonate_after:8.5"

        Returns:
            (action_type, delay) where delay is None for movement commands

        Raises:
            ValueError: If delay is outside valid range [0.0, 15.0] or format is invalid
        """
        if ":" in action_str:
            # Handle "detonate_after:X" commands
            parts = action_str.split(":", 1)
            if parts[0].lower() == "detonate_after":
                try:
                    delay = float(parts[1])
                except (ValueError, IndexError) as e:
                    logger.error(f"Invalid detonation delay format: {action_str}")
                    raise ValueError(f"Invalid detonation delay format: {action_str}") from e

                # Validate delay range
                if delay < 0.0 or delay > 15.0:
                    raise ValueError(f"Detonation delay {delay} outside valid range [0.0, 15.0]")

                return ("detonate_after", delay)

        # Regular movement command
        return (action_str, None)

    def _update_blast_zones(self, blast_zones: List[BlastZone], dt: float):
        """Update all blast zones per substep (lifecycle progression).

        Handles expansion, persistence, and dissipation phases.

        Args:
            blast_zones: List of active blast zones to update
            dt: Time step in seconds
        """
        zones_to_remove = []

        for zone in blast_zones:
            # Increment age
            zone.age += dt

            if zone.phase == BlastZonePhase.EXPANSION:
                # Calculate expansion rate from config
                expansion_duration = self.config.torpedo.blast_expansion_seconds
                max_radius = self.config.torpedo.blast_radius_units
                growth_rate = max_radius / expansion_duration  # e.g., 15.0 / 5.0 = 3.0 units/s

                # Grow radius
                zone.current_radius += growth_rate * dt
                zone.current_radius = min(zone.current_radius, max_radius)  # Cap at max

                # Check for phase transition
                if zone.age >= expansion_duration:
                    zone.phase = BlastZonePhase.PERSISTENCE
                    zone.current_radius = max_radius  # Ensure exact max radius

            elif zone.phase == BlastZonePhase.PERSISTENCE:
                # Maintain current radius (no changes to radius)
                # Calculate when persistence ends
                persistence_start = self.config.torpedo.blast_expansion_seconds
                persistence_end = persistence_start + self.config.torpedo.blast_persistence_seconds

                # Check for phase transition to dissipation
                if zone.age >= persistence_end:
                    zone.phase = BlastZonePhase.DISSIPATION

            elif zone.phase == BlastZonePhase.DISSIPATION:
                # Shrink radius: 15.0 → 0.0 over dissipation_duration seconds
                dissipation_duration = self.config.torpedo.blast_dissipation_seconds
                max_radius = self.config.torpedo.blast_radius_units
                shrink_rate = max_radius / dissipation_duration  # e.g., 15.0 / 5.0 = 3.0 units/s

                # Shrink radius
                zone.current_radius -= shrink_rate * dt
                zone.current_radius = max(0.0, zone.current_radius)  # Clamp at 0

                # Mark for removal when fully dissipated
                if zone.current_radius <= 0.0:
                    zones_to_remove.append(zone)

        # Remove dissipated zones
        for zone in zones_to_remove:
            blast_zones.remove(zone)

    def _handle_torpedo_detonations(self, state: GameState, events: List[Event], dt: float):
        """Check for detonations and create blast zones.

        Handles both timed detonations and auto-detonations (AE depleted).

        Args:
            state: Current game state
            events: Event list to append detonation events to
            dt: Time delta for this substep
        """
        torpedoes_to_detonate = []

        for torpedo in state.torpedoes:
            # Decrement timed detonation timer
            if torpedo.detonation_timer is not None:
                torpedo.detonation_timer -= dt
                if torpedo.detonation_timer <= 0.0:
                    torpedoes_to_detonate.append(torpedo)

            # Auto-detonate when AE depleted (existing behavior)
            elif torpedo.ae_remaining <= 0:
                torpedoes_to_detonate.append(torpedo)

        # Create blast zones for detonating torpedoes
        for torpedo in torpedoes_to_detonate:
            blast_zone = BlastZone(
                id=f"{torpedo.id}_blast",
                position=Vec2D(torpedo.position.x, torpedo.position.y),
                base_damage=torpedo.ae_remaining * self.config.torpedo.blast_damage_multiplier,
                phase=BlastZonePhase.EXPANSION,
                age=0.0,
                current_radius=0.0,
                owner=torpedo.owner
            )
            state.blast_zones.append(blast_zone)

            # Record detonation event
            events.append(Event(
                type="torpedo_detonated",
                turn=state.turn,
                data={
                    "torpedo_id": torpedo.id,
                    "owner": torpedo.owner,
                    "position": [torpedo.position.x, torpedo.position.y],
                    "ae_remaining": torpedo.ae_remaining,
                    "blast_zone_id": blast_zone.id,
                    "detonation_type": "timed" if torpedo.detonation_timer is not None else "auto"
                }
            ))

            # Remove torpedo from state
            state.torpedoes.remove(torpedo)

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
        # Story 024: Check cooldown before firing
        if attacker.phaser_cooldown_remaining > 0.0:
            return None  # Cannot fire - still on cooldown

        distance = attacker.position.distance_to(target.position)

        # Determine phaser parameters from config
        if attacker.phaser_config == PhaserConfig.WIDE:
            arc = np.radians(self.config.phaser.wide.arc_degrees)
            max_range = self.config.phaser.wide.range_units
            damage = self.config.phaser.wide.damage
            cooldown = self.config.phaser.wide.cooldown_seconds
        else:  # FOCUSED
            arc = np.radians(self.config.phaser.focused.arc_degrees)
            max_range = self.config.phaser.focused.range_units
            damage = self.config.phaser.focused.damage
            cooldown = self.config.phaser.focused.cooldown_seconds

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

            # Story 024: Set cooldown after successful fire
            attacker.phaser_cooldown_remaining = cooldown

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
