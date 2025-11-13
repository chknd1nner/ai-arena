from dataclasses import dataclass
from typing import List, Tuple, Optional
import numpy as np
from enum import Enum

from ai_arena.game_engine.data_models import GameState, Orders, Event, ShipState, TorpedoState, Vec2D, MovementType, PhaserConfig

# ============= Physics Constants =============

FIXED_TIMESTEP = 1.0 / 60.0  # 60 Hz simulation
ACTION_PHASE_DURATION = 60.0  # 60 simulated seconds per turn
SUBSTEPS = int(ACTION_PHASE_DURATION / FIXED_TIMESTEP)  # 3600

SHIP_SPEED = 10.0  # units per second
TORPEDO_SPEED = 15.0  # units per second

MOVEMENT_COSTS = {
    MovementType.STRAIGHT: 5,
    MovementType.SOFT_LEFT: 7,
    MovementType.SOFT_RIGHT: 7,
    MovementType.HARD_LEFT: 10,
    MovementType.HARD_RIGHT: 10,
    MovementType.REVERSE: 8,
    MovementType.REVERSE_LEFT: 12,
    MovementType.REVERSE_RIGHT: 12,
    MovementType.STOP: 0,
}

MOVEMENT_PARAMS = {
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

# ============= Core Engine =============

class PhysicsEngine:
    """
    Stateless physics engine - pure function.
    Input: GameState + Orders → Output: New GameState + Events
    """
    
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
        
        # 3. Simulate 60 seconds with fixed timestep
        for substep in range(SUBSTEPS):
            self._update_ship_physics(new_state.ship_a, valid_orders_a, FIXED_TIMESTEP)
            self._update_ship_physics(new_state.ship_b, valid_orders_b, FIXED_TIMESTEP)
            
            for torpedo in new_state.torpedoes:
                torpedo_orders = valid_orders_a.torpedo_orders.get(torpedo.id) \
                    if torpedo.owner == "ship_a" \
                    else valid_orders_b.torpedo_orders.get(torpedo.id)
                self._update_torpedo_physics(torpedo, torpedo_orders, FIXED_TIMESTEP)
        
        # 4. Check for hits after full action phase
        phaser_events = self._check_phaser_hits(new_state)
        events.extend(phaser_events)
        
        torpedo_events = self._check_torpedo_collisions(new_state)
        events.extend(torpedo_events)
        
        # 5. Regenerate AE
        new_state.ship_a.ae = min(new_state.ship_a.ae + 5, 100)
        new_state.ship_b.ae = min(new_state.ship_b.ae + 5, 100)
        
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

    def _validate_orders(self, ship: ShipState, orders: Orders) -> Orders:
        # Basic validation, can be expanded
        if MOVEMENT_COSTS.get(orders.movement, 0) > ship.ae:
            orders.movement = MovementType.STOP
        return orders

    def _apply_weapon_action(self, state: GameState, ship_id: str, ship: ShipState, weapon_action: str) -> List[Event]:
        events = []
        if weapon_action == "LAUNCH_TORPEDO":
            if ship.ae >= 20 and len([t for t in state.torpedoes if t.owner == ship_id]) < 4:
                ship.ae -= 20
                new_torpedo = TorpedoState(
                    id=f"{ship_id}_torpedo_{state.turn}",
                    position=ship.position,
                    velocity=Vec2D(np.cos(ship.heading) * TORPEDO_SPEED, np.sin(ship.heading) * TORPEDO_SPEED),
                    heading=ship.heading,
                    ae_remaining=40,
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
        """Update ship position and heading for one timestep."""
        if orders.movement == MovementType.STOP:
            ship.velocity = Vec2D(0, 0)
            return
        
        # Rotation happens gradually over 60 seconds
        rotation_per_dt = MOVEMENT_PARAMS[orders.movement]["rotation"] * dt / ACTION_PHASE_DURATION
        ship.heading += rotation_per_dt
        ship.heading = ship.heading % (2 * np.pi)
        
        # Update velocity based on heading
        ship.velocity = Vec2D(
            np.cos(ship.heading) * SHIP_SPEED,
            np.sin(ship.heading) * SHIP_SPEED
        )
        
        # Update position
        ship.position = ship.position + (ship.velocity * dt)

    def _update_torpedo_physics(self, torpedo: TorpedoState, movement: Optional[MovementType], dt: float):
        if torpedo.just_launched:
            pass # No turning on launch turn
        elif movement:
            rotation_per_dt = MOVEMENT_PARAMS.get(movement, {"rotation": 0})["rotation"] * dt / ACTION_PHASE_DURATION
            torpedo.heading += rotation_per_dt
            torpedo.heading = torpedo.heading % (2 * np.pi)

        torpedo.velocity = Vec2D(
            np.cos(torpedo.heading) * TORPEDO_SPEED,
            np.sin(torpedo.heading) * TORPEDO_SPEED
        )
        torpedo.position = torpedo.position + (torpedo.velocity * dt)
        torpedo.ae_remaining -= 1 * dt # Simplified AE burn

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
        
        # Determine phaser parameters
        if attacker.phaser_config == PhaserConfig.WIDE:
            arc = np.radians(90)
            max_range = 30
            damage = 15
        else:  # FOCUSED
            arc = np.radians(10)
            max_range = 50
            damage = 35
        
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
                    if distance < 15: # Blast radius
                        damage = int(torpedo.ae_remaining * 1.5)
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
