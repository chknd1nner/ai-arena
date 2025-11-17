from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional
from enum import Enum
import numpy as np

# ============= Data Structures =============

@dataclass
class Vec2D:
    """2D vector for positions and velocities."""
    x: float = 0.0
    y: float = 0.0
    
    def __add__(self, other):
        return Vec2D(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Vec2D(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar):
        return Vec2D(self.x * scalar, self.y * scalar)
    
    def magnitude(self) -> float:
        return np.sqrt(self.x**2 + self.y**2)
    
    def normalized(self) -> 'Vec2D':
        mag = self.magnitude()
        if mag == 0:
            return Vec2D(0, 0)
        return Vec2D(self.x / mag, self.y / mag)
    
    def distance_to(self, other: 'Vec2D') -> float:
        return (self - other).magnitude()
    
    def to_tuple(self) -> Tuple[float, float]:
        return (self.x, self.y)

class MovementType(Enum):
    """Legacy movement type for torpedo orders (still uses coupled system)."""
    STRAIGHT = "STRAIGHT"
    SOFT_LEFT = "SOFT_LEFT"
    SOFT_RIGHT = "SOFT_RIGHT"
    HARD_LEFT = "HARD_LEFT"
    HARD_RIGHT = "HARD_RIGHT"
    REVERSE = "REVERSE"
    REVERSE_LEFT = "REVERSE_LEFT"
    REVERSE_RIGHT = "REVERSE_RIGHT"
    STOP = "STOP"

class MovementDirection(Enum):
    """Movement direction relative to current heading.

    Movement sets the velocity direction but does NOT change heading.
    Combine with RotationCommand for independent facing control.
    """
    FORWARD = "FORWARD"               # 0° - Continue straight ahead
    FORWARD_LEFT = "FORWARD_LEFT"     # -45° - Diagonal left-forward
    FORWARD_RIGHT = "FORWARD_RIGHT"   # +45° - Diagonal right-forward
    LEFT = "LEFT"                     # -90° - Perpendicular left
    RIGHT = "RIGHT"                   # +90° - Perpendicular right
    BACKWARD = "BACKWARD"             # 180° - Reverse direction
    BACKWARD_LEFT = "BACKWARD_LEFT"   # -135° - Diagonal left-backward
    BACKWARD_RIGHT = "BACKWARD_RIGHT" # +135° - Diagonal right-backward
    STOP = "STOP"                     # 0 velocity - Coast to halt

class RotationCommand(Enum):
    """Ship rotation command independent of movement.

    Rotation changes heading but does NOT change velocity direction.
    Phasers always point in heading direction.
    """
    NONE = "NONE"               # 0.0°/s - Maintain current heading
    SOFT_LEFT = "SOFT_LEFT"     # +1.0°/s - Gentle left rotation
    SOFT_RIGHT = "SOFT_RIGHT"   # -1.0°/s - Gentle right rotation
    HARD_LEFT = "HARD_LEFT"     # +3.0°/s - Aggressive left rotation
    HARD_RIGHT = "HARD_RIGHT"   # -3.0°/s - Aggressive right rotation

class PhaserConfig(Enum):
    WIDE = "WIDE"
    FOCUSED = "FOCUSED"

class BlastZonePhase(Enum):
    """Lifecycle phase for blast zones."""
    EXPANSION = "expansion"       # Growing from 0→15 units
    PERSISTENCE = "persistence"   # Holding at 15 units
    DISSIPATION = "dissipation"   # Shrinking from 15→0 units

@dataclass
class ShipState:
    """Complete state for one ship."""
    position: Vec2D
    velocity: Vec2D
    heading: float            # radians, 0 = East
    shields: int              # 0-100
    ae: int                   # 0-100
    phaser_config: PhaserConfig
    reconfiguring_phaser: bool = False
    phaser_cooldown_remaining: float = 0.0  # seconds until can fire again

    def __post_init__(self):
        """Validate ship state fields."""
        if self.phaser_cooldown_remaining < 0.0:
            raise ValueError(
                f"phaser_cooldown_remaining must be >= 0.0, got {self.phaser_cooldown_remaining}"
            )

@dataclass
class TorpedoState:
    """Complete state for one torpedo."""
    id: str
    position: Vec2D
    velocity: Vec2D
    heading: float            # radians
    ae_remaining: int
    owner: str                # "ship_a" or "ship_b"
    just_launched: bool = False
    detonation_timer: Optional[float] = None  # Seconds until timed detonation

@dataclass
class BlastZone:
    """Persistent area of damage from torpedo detonation.

    Lifecycle: Expansion (5s) → Persistence (60s) → Dissipation (5s) = 70s total

    Attributes:
        id: Unique identifier (e.g., "ship_a_torp_5_blast")
        position: Center point of blast zone (fixed for lifetime)
        base_damage: Total damage potential ((AE at detonation) × 1.5)
        phase: Current lifecycle phase (EXPANSION/PERSISTENCE/DISSIPATION)
        age: Time since creation in seconds (0.0 → 70.0)
        current_radius: Current blast radius in units (0.0 → 15.0 → 15.0 → 0.0)
        owner: Ship that launched torpedo ("ship_a" or "ship_b")
    """
    id: str
    position: Vec2D
    base_damage: float
    phase: BlastZonePhase
    age: float
    current_radius: float
    owner: str

@dataclass
class GameState:
    """Complete game state at a single point in time."""
    turn: int
    ship_a: ShipState
    ship_b: ShipState
    torpedoes: List[TorpedoState] = field(default_factory=list)
    blast_zones: List[BlastZone] = field(default_factory=list)

@dataclass
class Orders:
    """Commands from LLM for one ship.

    Movement and rotation are independent:
    - movement: Sets velocity direction relative to heading
    - rotation: Changes heading independent of velocity
    """
    movement: MovementDirection      # Changed from MovementType
    rotation: RotationCommand        # NEW: Independent rotation
    weapon_action: str
    torpedo_orders: Dict[str, MovementType] = field(default_factory=dict)

@dataclass
class Event:
    """Something that happened during a turn."""
    type: str
    turn: int
    data: dict

@dataclass
class MatchConfig:
    model_a: str
    model_b: str
    max_turns: int = 50
    initial_ae: int = 100
    initial_shields: int = 100

@dataclass
class MatchResult:
    match_id: str
    winner: str
    total_turns: int
    replay_path: str
    final_state: GameState
