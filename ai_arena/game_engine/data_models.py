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
    STRAIGHT = "STRAIGHT"
    SOFT_LEFT = "SOFT_LEFT"
    SOFT_RIGHT = "SOFT_RIGHT"
    HARD_LEFT = "HARD_LEFT"
    HARD_RIGHT = "HARD_RIGHT"
    REVERSE = "REVERSE"
    REVERSE_LEFT = "REVERSE_LEFT"
    REVERSE_RIGHT = "REVERSE_RIGHT"
    STOP = "STOP"

class PhaserConfig(Enum):
    WIDE = "WIDE"
    FOCUSED = "FOCUSED"

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

@dataclass
class GameState:
    """Complete game state at a single point in time."""
    turn: int
    ship_a: ShipState
    ship_b: ShipState
    torpedoes: List[TorpedoState] = field(default_factory=list)

@dataclass
class Orders:
    """Commands from LLM for one ship."""
    movement: MovementType
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
