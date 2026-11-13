"""
kaggriculture — typed compatibility layer for the Kaggriculture competition environment.

Converts raw Kaggle observation dicts / Struct objects into validated, typed
internal representations that the strategy engine can safely consume.
"""
from .schema import (
    GameState, FarmState, TileState, MarketState, PrivateState,
    TownState, CropInfo, AnimalInfo, GameConfig,
    CROPS, ANIMALS, PRODUCTS, MARKET_PARAMS, LAND_ORDER, LAND_PRICES,
    SHOPS, PRICE_FLOOR, FARM_HAND_COST_MULT,
)
from .state_parser import StateParser
from .action_space import (
    Action, FarmerOp, MarketOp,
    make_pass, make_move, make_plant, make_water, make_harvest,
    make_fertilize, make_feed, make_care, make_collect_fertilizer,
    make_build_coop, make_build_pasture, make_dig, make_pickup, make_place,
    make_buy_seed, make_buy_product, make_buy_animal, make_sell,
    make_hire, make_buy_land,
    build_action_dict,
)
from .environment_adapter import EnvironmentAdapter

__all__ = [
    "GameState", "FarmState", "TileState", "MarketState", "PrivateState",
    "TownState", "CropInfo", "AnimalInfo", "GameConfig",
    "CROPS", "ANIMALS", "PRODUCTS", "MARKET_PARAMS", "LAND_ORDER", "LAND_PRICES",
    "SHOPS", "PRICE_FLOOR", "FARM_HAND_COST_MULT",
    "StateParser",
    "Action", "FarmerOp", "MarketOp",
    "make_pass", "make_move", "make_plant", "make_water", "make_harvest",
    "make_fertilize", "make_feed", "make_care", "make_collect_fertilizer",
    "make_build_coop", "make_build_pasture", "make_dig", "make_pickup", "make_place",
    "make_buy_seed", "make_buy_product", "make_buy_animal", "make_sell",
    "make_hire", "make_buy_land",
    "build_action_dict",
    "EnvironmentAdapter",
]
