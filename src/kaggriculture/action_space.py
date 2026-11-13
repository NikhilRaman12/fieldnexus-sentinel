"""
action_space.py — typed action builders and legality checks.

Action format (verified against live environment):
    {
        "farmer": [op, ...args],         # exactly one op for the main farmer
        "hands":  [[op, ...args], ...],  # one op per hired hand (may be empty)
        "market": [[op, ...args], ...],  # up to maxMarketOrdersPerTurn market ops
    }

Farmer/hand ops:
    NORTH | SOUTH | EAST | WEST
    PASS
    PICKUP <item> [n]
    PLANT <crop>
    WATER
    HARVEST
    FERTILIZE
    BUILD_COOP
    BUILD_PASTURE
    DIG
    PLACE <item> [n]
    FEED
    COLLECT_FERTILIZER
    CARE

Market ops:
    BUY_SEED <crop> <n>
    BUY_PRODUCT <item> <n>
    BUY_ANIMAL <animal> <n>
    SELL <item> <n>
    HIRE
    BUY_LAND
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Any, Optional, Dict
from .schema import GameState, CROPS, ANIMALS, PRODUCTS, LAND_ORDER


# ---------------------------------------------------------------------------
# Op name constants
# ---------------------------------------------------------------------------

class FarmerOp:
    NORTH = "NORTH"
    SOUTH = "SOUTH"
    EAST = "EAST"
    WEST = "WEST"
    PASS = "PASS"
    PICKUP = "PICKUP"
    PLANT = "PLANT"
    WATER = "WATER"
    HARVEST = "HARVEST"
    FERTILIZE = "FERTILIZE"
    BUILD_COOP = "BUILD_COOP"
    BUILD_PASTURE = "BUILD_PASTURE"
    DIG = "DIG"
    PLACE = "PLACE"
    FEED = "FEED"
    COLLECT_FERTILIZER = "COLLECT_FERTILIZER"
    CARE = "CARE"


class MarketOp:
    BUY_SEED = "BUY_SEED"
    BUY_PRODUCT = "BUY_PRODUCT"
    BUY_ANIMAL = "BUY_ANIMAL"
    SELL = "SELL"
    HIRE = "HIRE"
    BUY_LAND = "BUY_LAND"


# ---------------------------------------------------------------------------
# Action dataclass
# ---------------------------------------------------------------------------

@dataclass
class Action:
    """Typed representation of one agent turn action."""
    farmer: List[Any] = field(default_factory=lambda: [FarmerOp.PASS])
    hands: List[List[Any]] = field(default_factory=list)
    market: List[List[Any]] = field(default_factory=list)
    label: str = "UNKNOWN"   # human-readable label for diagnostics

    def to_dict(self) -> Dict[str, Any]:
        return {"farmer": self.farmer, "hands": self.hands, "market": self.market}


# ---------------------------------------------------------------------------
# Builder helpers
# ---------------------------------------------------------------------------

def make_pass(market: Optional[List[List[Any]]] = None) -> Action:
    return Action(farmer=[FarmerOp.PASS], hands=[], market=market or [], label="PASS")


def make_move(direction: str, market: Optional[List[List[Any]]] = None) -> Action:
    assert direction in (FarmerOp.NORTH, FarmerOp.SOUTH, FarmerOp.EAST, FarmerOp.WEST)
    return Action(farmer=[direction], hands=[], market=market or [], label=f"MOVE_{direction}")


def make_plant(crop: str, market: Optional[List[List[Any]]] = None) -> Action:
    return Action(farmer=[FarmerOp.PLANT, crop], hands=[], market=market or [], label=f"PLANT_{crop}")


def make_water(market: Optional[List[List[Any]]] = None) -> Action:
    return Action(farmer=[FarmerOp.WATER], hands=[], market=market or [], label="WATER")


def make_harvest(market: Optional[List[List[Any]]] = None) -> Action:
    return Action(farmer=[FarmerOp.HARVEST], hands=[], market=market or [], label="HARVEST")


def make_fertilize(market: Optional[List[List[Any]]] = None) -> Action:
    return Action(farmer=[FarmerOp.FERTILIZE], hands=[], market=market or [], label="FERTILIZE")


def make_feed(market: Optional[List[List[Any]]] = None) -> Action:
    return Action(farmer=[FarmerOp.FEED], hands=[], market=market or [], label="FEED")


def make_care(market: Optional[List[List[Any]]] = None) -> Action:
    return Action(farmer=[FarmerOp.CARE], hands=[], market=market or [], label="CARE")


def make_collect_fertilizer(market: Optional[List[List[Any]]] = None) -> Action:
    return Action(farmer=[FarmerOp.COLLECT_FERTILIZER], hands=[], market=market or [], label="COLLECT_FERTILIZER")


def make_build_coop(market: Optional[List[List[Any]]] = None) -> Action:
    return Action(farmer=[FarmerOp.BUILD_COOP], hands=[], market=market or [], label="BUILD_COOP")


def make_build_pasture(market: Optional[List[List[Any]]] = None) -> Action:
    return Action(farmer=[FarmerOp.BUILD_PASTURE], hands=[], market=market or [], label="BUILD_PASTURE")


def make_dig(market: Optional[List[List[Any]]] = None) -> Action:
    return Action(farmer=[FarmerOp.DIG], hands=[], market=market or [], label="DIG")


def make_pickup(item: str, n: int = 1, market: Optional[List[List[Any]]] = None) -> Action:
    return Action(farmer=[FarmerOp.PICKUP, item, n], hands=[], market=market or [], label=f"PICKUP_{item}_{n}")


def make_place(item: str, n: int = 1, market: Optional[List[List[Any]]] = None) -> Action:
    return Action(farmer=[FarmerOp.PLACE, item, n], hands=[], market=market or [], label=f"PLACE_{item}_{n}")


# Market action builders
def make_buy_seed(crop: str, n: int) -> List[Any]:
    return [MarketOp.BUY_SEED, crop, n]


def make_buy_product(item: str, n: int) -> List[Any]:
    return [MarketOp.BUY_PRODUCT, item, n]


def make_buy_animal(animal: str, n: int = 1) -> List[Any]:
    return [MarketOp.BUY_ANIMAL, animal, n]


def make_sell(item: str, n: int) -> List[Any]:
    return [MarketOp.SELL, item, n]


def make_hire() -> List[Any]:
    return [MarketOp.HIRE]


def make_buy_land() -> List[Any]:
    return [MarketOp.BUY_LAND]


def build_action_dict(farmer_op: List[Any], market_ops: Optional[List[List[Any]]] = None,
                      hand_ops: Optional[List[List[Any]]] = None) -> Dict[str, Any]:
    """Directly build the action dict without going through Action dataclass."""
    return {
        "farmer": farmer_op,
        "hands": hand_ops or [],
        "market": market_ops or [],
    }


# ---------------------------------------------------------------------------
# Legality checks
# ---------------------------------------------------------------------------

def is_farmer_at_tile(state: GameState, tile_x: int, tile_y: int) -> bool:
    fp = state.my_farm.farmer_pos
    return fp[0] == tile_x and fp[1] == tile_y


def can_plant(state: GameState, crop: str) -> bool:
    """Check if farmer can plant on current tile."""
    farm = state.my_farm
    fp = farm.farmer_pos
    x, y = fp[0], fp[1]
    if y >= len(farm.tiles) or x >= len(farm.tiles[0]):
        return False
    tile = farm.tiles[y][x]
    if not tile.empty or tile.locked:
        return False
    if state.private.seeds.get(crop, 0) < 1:
        return False
    return True


def can_water(state: GameState) -> bool:
    """Check if farmer can water current tile."""
    farm = state.my_farm
    fp = farm.farmer_pos
    x, y = fp[0], fp[1]
    if y >= len(farm.tiles) or x >= len(farm.tiles[0]):
        return False
    tile = farm.tiles[y][x]
    return tile.kind == "PLANT" and not tile.watered_today


def can_harvest(state: GameState) -> bool:
    """Check if farmer can harvest current tile."""
    farm = state.my_farm
    fp = farm.farmer_pos
    x, y = fp[0], fp[1]
    if y >= len(farm.tiles) or x >= len(farm.tiles[0]):
        return False
    tile = farm.tiles[y][x]
    if tile.kind != "PLANT":
        return False
    cfg = state.config
    crop_info = CROPS.get(tile.crop or "", {})
    days_alive = state.day - tile.planted_day
    return days_alive >= crop_info.get("first_yield_day", 999)


def can_feed(state: GameState) -> bool:
    """Check if farmer can feed animal on current tile."""
    farm = state.my_farm
    fp = farm.farmer_pos
    x, y = fp[0], fp[1]
    if y >= len(farm.tiles) or x >= len(farm.tiles[0]):
        return False
    tile = farm.tiles[y][x]
    if tile.kind not in ("COOP", "PASTURE"):
        return False
    if tile.fed_today:
        return False
    # Need wheat for feed
    wheat_inv = state.private.inventories[0].get("WHEAT", 0) if state.private.inventories else 0
    wheat_shed = state.private.shed.get("WHEAT", 0)
    return (wheat_inv + wheat_shed) >= 1


def can_buy_seed(state: GameState, crop: str, n: int = 1) -> bool:
    seed_price = CROPS.get(crop, {}).get("seed", 999999)
    return state.my_farm.money >= seed_price * n


def can_buy_land(state: GameState) -> bool:
    if state.next_land_cost is None:
        return False
    return state.my_farm.money >= state.next_land_cost


def can_hire(state: GameState) -> bool:
    cost = state.farm_hand_cost()
    return state.my_farm.money >= cost


def can_move(state: GameState, direction: str) -> bool:
    farm = state.my_farm
    fp = farm.farmer_pos
    x, y = fp[0], fp[1]
    bs = state.config.board_size
    dx_dy = {"NORTH": (0, -1), "SOUTH": (0, 1), "EAST": (1, 0), "WEST": (-1, 0)}
    if direction not in dx_dy:
        return False
    dx, dy = dx_dy[direction]
    nx, ny = x + dx, y + dy
    if nx < 0 or nx >= bs or ny < 0 or ny >= bs:
        return False
    tile = farm.tiles[ny][nx]
    return not tile.locked


def can_dig(state: GameState) -> bool:
    farm = state.my_farm
    fp = farm.farmer_pos
    x, y = fp[0], fp[1]
    if y >= len(farm.tiles) or x >= len(farm.tiles[0]):
        return False
    tile = farm.tiles[y][x]
    return tile.kind == "WEED"


def can_collect_fertilizer(state: GameState) -> bool:
    farm = state.my_farm
    fp = farm.farmer_pos
    x, y = fp[0], fp[1]
    if y >= len(farm.tiles) or x >= len(farm.tiles[0]):
        return False
    tile = farm.tiles[y][x]
    return tile.kind in ("COOP", "PASTURE") and tile.fertilizer_available


def can_sell(state: GameState, item: str, n: int = 1) -> bool:
    shed_qty = state.private.shed.get(item, 0)
    inv_qty = state.private.inventories[0].get(item, 0) if state.private.inventories else 0
    return (shed_qty + inv_qty) >= n and n >= 1
