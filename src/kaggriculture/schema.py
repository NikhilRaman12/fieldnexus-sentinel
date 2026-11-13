"""
schema.py — canonical typed representations of the Kaggriculture game state.

All dataclasses use only stdlib types (no external deps) so this module is
safe to import inside the competition sandbox.

Source of truth: kaggle_environments/envs/kaggriculture/kaggriculture.py
Environment version: 0.1.0
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

# ---------------------------------------------------------------------------
# Environment constants (mirrored from kaggriculture.py — verified 2026-08-19)
# ---------------------------------------------------------------------------

CROPS: Dict[str, Dict[str, Any]] = {
    "WHEAT":      {"seed": 10,  "first_yield_day": 2,  "max_yield_day": 4,  "interval": 0, "max_yield": 6, "ongoing": False},
    "CARROT":     {"seed": 20,  "first_yield_day": 2,  "max_yield_day": 3,  "interval": 0, "max_yield": 4, "ongoing": False},
    "TOMATO":     {"seed": 50,  "first_yield_day": 8,  "max_yield_day": 8,  "interval": 1, "max_yield": 4, "ongoing": True},
    "STRAWBERRY": {"seed": 100, "first_yield_day": 10, "max_yield_day": 10, "interval": 2, "max_yield": 4, "ongoing": True},
    "MELON":      {"seed": 80,  "first_yield_day": 10, "max_yield_day": 12, "interval": 0, "max_yield": 6, "ongoing": False},
}

ANIMALS: Dict[str, Dict[str, Any]] = {
    "GOOSE": {"cost": 300, "structure": "COOP",    "first_yield_day": 4, "interval": 1, "max_held": 4, "product": "EGG"},
    "COW":   {"cost": 400, "structure": "PASTURE", "first_yield_day": 8, "interval": 2, "max_held": 6, "product": "MILK"},
    "SHEEP": {"cost": 500, "structure": "PASTURE", "first_yield_day": 6, "interval": 3, "max_held": 6, "product": "WOOL"},
}

PRODUCTS: List[str] = [
    "WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON",
    "EGG", "MILK", "WOOL", "FERTILIZER"
]

MARKET_PARAMS: Dict[str, Dict[str, Any]] = {
    "WHEAT":      {"base": 25,  "I0": 10000, "T": 400, "below_func": "sqrt",   "below_target": 0.80, "above_func": "log",    "above_target": 0.20},
    "CARROT":     {"base": 35,  "I0": 10000, "T": 450, "below_func": "hinge",  "below_target": 1.00, "above_func": "sqrt",   "above_target": 0.70},
    "TOMATO":     {"base": 60,  "I0": 10000, "T": 200, "below_func": "hinge",  "below_target": 0.40, "above_func": "sqrt",   "above_target": 0.60},
    "STRAWBERRY": {"base": 120, "I0": 10000, "T": 100, "below_func": "sqrt",   "below_target": 0.70, "above_func": "linear", "above_target": 1.60},
    "MELON":      {"base": 250, "I0": 10000, "T": 300, "below_func": "log",    "below_target": 0.20, "above_func": "sq",     "above_target": 3.60},
    "EGG":        {"base": 50,  "I0": 10000, "T": 332, "below_func": "hinge",  "below_target": 0.40, "above_func": "log",    "above_target": 0.20},
    "MILK":       {"base": 160, "I0": 10000, "T": 122, "below_func": "sqrt",   "below_target": 0.60, "above_func": "linear", "above_target": 1.60},
    "WOOL":       {"base": 200, "I0": 10000, "T": 105, "below_func": "log",    "below_target": 0.20, "above_func": "sq",     "above_target": 3.20},
    "FERTILIZER": {"base": 100, "I0": 10000, "T": 200, "below_func": "linear", "below_target": 0.40, "above_func": "linear", "above_target": 0.40},
}

LAND_ORDER: List[str] = ["NE", "SW", "SE"]
LAND_PRICES: List[int] = [1000, 2000, 4000]

SHOPS: Dict[str, List[str]] = {
    "BAKERY":         ["EGG", "WHEAT"],
    "PIZZA_SHOP":     ["MILK", "TOMATO", "WHEAT"],
    "BRUNCH_SPOT":    ["EGG", "WHEAT", "STRAWBERRY"],
    "YARN_STORE":     ["WOOL"],
    "ICE_CREAM_SHOP": ["STRAWBERRY", "MILK", "WHEAT"],
    "PET_CAFE":       ["CARROT"],
    "SMOOTHIE_SHOP":  ["STRAWBERRY", "MILK"],
    "FARMERS_MARKET": ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY"],
}

PRICE_FLOOR: int = 1
FARM_HAND_COST_MULT: int = 1

# Fibonacci sequence for farm hand costs
_FIB: List[int] = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]


def farm_hand_cost(hires_today: int, mult: int = FARM_HAND_COST_MULT) -> int:
    """Cost of the (hires_today+1)-th hire of the day."""
    idx = min(hires_today, len(_FIB) - 1)
    return mult * _FIB[idx]


# ---------------------------------------------------------------------------
# Typed internal representations
# ---------------------------------------------------------------------------

@dataclass
class GameConfig:
    """Parsed episode configuration."""
    episode_steps: int = 720
    act_timeout: float = 1.0
    board_size: int = 10
    starting_money: int = 3000
    max_market_orders_per_turn: int = 10
    turns_per_day: int = 24
    shed_capacity: int = 100
    weed_spawn_chance: float = 0.005
    town_shop_unlock_interval: int = 3
    town_shop_sell_interval: int = 4
    town_center_sell_interval: int = 24
    farm_hand_cost_mult: int = 1


@dataclass
class TileState:
    """State of a single farm tile."""
    x: int
    y: int
    locked: bool = False
    empty: bool = True                # None in raw = empty unlocked
    kind: Optional[str] = None        # "PLANT", "COOP", "PASTURE", "WEED", "LOCKED"
    # Plant-specific
    crop: Optional[str] = None
    planted_day: int = 0
    watered_today: bool = False
    consecutive_unwatered: int = 0
    yield_units: int = 0
    max_lifespan_step: int = -1
    fertilized_until_day: int = -1
    # Animal-specific
    animal: Optional[str] = None
    placed_day: int = 0
    yield_units_animal: int = 0
    consecutive_unfed: int = 0
    fed_today: bool = False
    cared_today: bool = False
    fertilizer_available: bool = False
    pending_care_bonus: int = 0


@dataclass
class FarmState:
    """State of one player's farm."""
    player_idx: int
    money: float
    tiles: List[List[TileState]]  # [y][x]
    farmer_pos: List[int]         # [x, y]
    hands: List[List[int]]        # list of [x, y] positions
    unlocked_quadrants: List[str]
    hires_today: int

    def quadrant_of(self, x: int, y: int, board_size: int) -> str:
        half = board_size // 2
        return ("N" if y < half else "S") + ("W" if x < half else "E")

    def tiles_flat(self) -> List[TileState]:
        return [t for row in self.tiles for t in row]

    def plants(self) -> List[TileState]:
        return [t for t in self.tiles_flat() if t.kind == "PLANT"]

    def animals(self) -> List[TileState]:
        return [t for t in self.tiles_flat() if t.kind in ("COOP", "PASTURE")]

    def empty_unlocked(self) -> List[TileState]:
        return [t for t in self.tiles_flat() if t.empty and not t.locked]

    def weeds(self) -> List[TileState]:
        return [t for t in self.tiles_flat() if t.kind == "WEED"]


@dataclass
class MarketState:
    """State of the shared market."""
    inventory: Dict[str, int]    # item -> quantity in market
    prices: Dict[str, int]       # item -> current price per unit


@dataclass
class PrivateState:
    """Private per-player inventory (shed + seeds + worker inventories)."""
    shed: Dict[str, int]         # item -> quantity in shed
    seeds: Dict[str, int]        # crop -> seed quantity
    inventories: List[Dict[str, int]]  # worker inventories


@dataclass
class TownState:
    """State of the shared town."""
    unlocked_shops: List[str]


@dataclass
class CropInfo:
    """Derived crop analysis for a specific tile."""
    tile: TileState
    days_since_plant: int
    days_to_first_yield: int
    days_to_max_yield: int
    harvest_ready: bool
    near_death: bool
    expected_yield: int
    base_price: int
    expected_revenue: float


@dataclass
class AnimalInfo:
    """Derived animal analysis for a specific tile."""
    tile: TileState
    days_since_placed: int
    days_to_first_yield: int
    producing: bool
    yield_ready: bool
    product: str
    base_price: int
    expected_revenue_per_interval: float


@dataclass
class GameState:
    """Complete parsed game state for one agent's turn."""
    step: int
    player: int
    day: int
    hour: int
    my_farm: FarmState
    opponent_farm: FarmState
    market: MarketState
    private: PrivateState
    town: TownState
    config: GameConfig
    remaining_overage_time: float = 60.0

    # Derived fields (populated by StateParser)
    turns_remaining: int = 0
    days_remaining: float = 0.0
    is_early_game: bool = True
    is_mid_game: bool = False
    is_late_game: bool = False
    next_land_cost: Optional[int] = None
    next_land_quadrant: Optional[str] = None
    total_unlocked: int = 1

    def cash(self) -> float:
        return self.my_farm.money

    def shed_total(self) -> int:
        return sum(self.private.shed.values())

    def shed_space(self) -> int:
        return max(0, self.config.shed_capacity - self.shed_total())

    def farm_hand_cost(self) -> int:
        return farm_hand_cost(self.my_farm.hires_today, self.config.farm_hand_cost_mult)
