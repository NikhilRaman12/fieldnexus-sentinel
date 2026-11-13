"""
state_parser.py — converts raw Kaggle observation (Struct or dict) into a
typed GameState.  Never crashes the competition agent: all errors produce safe
defaults with a warning flag.
"""
from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional

from .schema import (
    GameState, FarmState, TileState, MarketState, PrivateState, TownState,
    GameConfig, CROPS, ANIMALS, PRODUCTS, LAND_ORDER, LAND_PRICES,
)

_LOG = logging.getLogger("kaggriculture.parser")


def _get(obj: Any, key: str, default: Any = None) -> Any:
    """Access dict or Struct safely."""
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _as_dict(obj: Any) -> Dict[str, Any]:
    if isinstance(obj, dict):
        return obj
    try:
        return dict(obj)
    except Exception:
        return {k: getattr(obj, k) for k in dir(obj) if not k.startswith("_")}


class StateParser:
    """Parses raw Kaggriculture observations into typed GameState objects."""

    def __init__(self, config: Optional[GameConfig] = None):
        self.config = config or GameConfig()

    def update_config(self, raw_config: Any) -> None:
        """Update parser config from raw Kaggle configuration."""
        c = self.config
        c.episode_steps = int(_get(raw_config, "episodeSteps", c.episode_steps))
        c.act_timeout = float(_get(raw_config, "actTimeout", c.act_timeout))
        c.board_size = int(_get(raw_config, "boardSize", c.board_size))
        c.starting_money = int(_get(raw_config, "startingMoney", c.starting_money))
        c.max_market_orders_per_turn = int(_get(raw_config, "maxMarketOrdersPerTurn", c.max_market_orders_per_turn))
        c.turns_per_day = int(_get(raw_config, "turnsPerDay", c.turns_per_day))
        c.shed_capacity = int(_get(raw_config, "shedCapacity", c.shed_capacity))
        c.weed_spawn_chance = float(_get(raw_config, "weedSpawnChance", c.weed_spawn_chance))
        c.town_shop_unlock_interval = int(_get(raw_config, "townShopUnlockInterval", c.town_shop_unlock_interval))
        c.town_shop_sell_interval = int(_get(raw_config, "townShopSellInterval", c.town_shop_sell_interval))
        c.town_center_sell_interval = int(_get(raw_config, "townCenterSellInterval", c.town_center_sell_interval))
        c.farm_hand_cost_mult = int(_get(raw_config, "farmHandCostMult", c.farm_hand_cost_mult))

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def parse(self, obs: Any, config: Any = None) -> GameState:
        """Parse raw observation into GameState.  Never raises."""
        try:
            if config is not None:
                self.update_config(config)
            return self._parse_unsafe(obs)
        except Exception as exc:
            _LOG.error("StateParser.parse() failed: %s — returning minimal safe state", exc)
            return self._safe_fallback(obs)

    # ------------------------------------------------------------------
    # Internal parsers
    # ------------------------------------------------------------------

    def _parse_unsafe(self, obs: Any) -> GameState:
        cfg = self.config
        step = int(_get(obs, "step", 0))
        player = int(_get(obs, "player", 0))
        day = int(_get(obs, "day", 0))
        hour = int(_get(obs, "hour", 0))
        overage = float(_get(obs, "remainingOverageTime", 60.0))

        raw_farms = _get(obs, "farms", [])
        if not raw_farms:
            raw_farms = [{}, {}]

        my_farm = self._parse_farm(raw_farms[player], player, cfg)
        opp_idx = 1 - player
        opp_farm = self._parse_farm(
            raw_farms[opp_idx] if opp_idx < len(raw_farms) else {},
            opp_idx, cfg
        )

        market = self._parse_market(_get(obs, "market", {}))
        private = self._parse_private(_get(obs, "private", {}))
        town = self._parse_town(_get(obs, "town", {}))

        turns_remaining = max(0, cfg.episode_steps - step)
        days_remaining = turns_remaining / max(1, cfg.turns_per_day)
        total_days = cfg.episode_steps / max(1, cfg.turns_per_day)
        day_fraction = day / max(1, total_days)

        # Land expansion info
        unlocked_count = len(my_farm.unlocked_quadrants)
        next_land_idx = unlocked_count - 1  # index into LAND_ORDER
        next_land_quadrant: Optional[str] = None
        next_land_cost: Optional[int] = None
        if next_land_idx < len(LAND_ORDER):
            next_land_quadrant = LAND_ORDER[next_land_idx]
            next_land_cost = LAND_PRICES[next_land_idx]

        gs = GameState(
            step=step,
            player=player,
            day=day,
            hour=hour,
            my_farm=my_farm,
            opponent_farm=opp_farm,
            market=market,
            private=private,
            town=town,
            config=cfg,
            remaining_overage_time=overage,
            turns_remaining=turns_remaining,
            days_remaining=days_remaining,
            is_early_game=day_fraction < 0.33,
            is_mid_game=0.33 <= day_fraction < 0.70,
            is_late_game=day_fraction >= 0.70,
            next_land_cost=next_land_cost,
            next_land_quadrant=next_land_quadrant,
            total_unlocked=unlocked_count,
        )
        return gs

    def _parse_farm(self, raw: Any, player_idx: int, cfg: GameConfig) -> FarmState:
        if not raw:
            return self._empty_farm(player_idx, cfg)
        money = float(_get(raw, "money", cfg.starting_money))
        raw_tiles = _get(raw, "tiles", [])
        tiles = self._parse_tiles(raw_tiles, cfg.board_size)
        farmer = list(_get(raw, "farmer", [0, 0]) or [0, 0])
        hands_raw = _get(raw, "hands", []) or []
        hands = [list(h) for h in hands_raw]
        unlocked = list(_get(raw, "unlocked_quadrants", ["NW"]) or ["NW"])
        hires_today = int(_get(raw, "hires_today", 0))
        return FarmState(
            player_idx=player_idx,
            money=max(0.0, money),
            tiles=tiles,
            farmer_pos=farmer,
            hands=hands,
            unlocked_quadrants=unlocked,
            hires_today=hires_today,
        )

    def _parse_tiles(self, raw_tiles: Any, board_size: int) -> List[List[TileState]]:
        result: List[List[TileState]] = []
        for y in range(board_size):
            row: List[TileState] = []
            raw_row = raw_tiles[y] if y < len(raw_tiles) else []
            for x in range(board_size):
                raw_tile = raw_row[x] if x < len(raw_row) else "LOCKED"
                row.append(self._parse_tile(x, y, raw_tile))
            result.append(row)
        return result

    def _parse_tile(self, x: int, y: int, raw: Any) -> TileState:
        if raw is None:
            return TileState(x=x, y=y, locked=False, empty=True)
        if isinstance(raw, str):
            if raw == "LOCKED":
                return TileState(x=x, y=y, locked=True, empty=False, kind="LOCKED")
            if raw == "WEED":
                return TileState(x=x, y=y, locked=False, empty=False, kind="WEED")
            return TileState(x=x, y=y, locked=False, empty=True)
        if not isinstance(raw, dict):
            try:
                raw = _as_dict(raw)
            except Exception:
                return TileState(x=x, y=y, locked=False, empty=True)
        kind = raw.get("kind", "")
        ts = TileState(x=x, y=y, locked=False, empty=False, kind=kind)
        if kind == "PLANT":
            ts.crop = raw.get("crop")
            ts.planted_day = int(raw.get("planted_day", 0))
            ts.watered_today = bool(raw.get("watered_today", False))
            ts.consecutive_unwatered = int(raw.get("consecutive_unwatered", 0))
            ts.yield_units = int(raw.get("yield_units", 0))
            ts.max_lifespan_step = int(raw.get("max_lifespan_step", -1))
            ts.fertilized_until_day = int(raw.get("fertilized_until_day", -1))
        elif kind in ("COOP", "PASTURE"):
            ts.animal = raw.get("animal")
            ts.placed_day = int(raw.get("placed_day", 0))
            ts.yield_units_animal = int(raw.get("yield_units", 0))
            ts.consecutive_unfed = int(raw.get("consecutive_unfed", 0))
            ts.fed_today = bool(raw.get("fed_today", False))
            ts.cared_today = bool(raw.get("cared_today", False))
            ts.fertilizer_available = bool(raw.get("fertilizer_available", False))
            ts.pending_care_bonus = int(raw.get("pending_care_bonus", 0))
        return ts

    def _parse_market(self, raw: Any) -> MarketState:
        if not raw:
            return MarketState(
                inventory={p: 10000 for p in PRODUCTS},
                prices={},
            )
        inv_raw = _get(raw, "inventory", {}) or {}
        prices_raw = _get(raw, "prices", {}) or {}
        inventory = {p: int(inv_raw.get(p, 10000)) for p in PRODUCTS}
        prices = {p: int(prices_raw.get(p, 0)) for p in PRODUCTS}
        return MarketState(inventory=inventory, prices=prices)

    def _parse_private(self, raw: Any) -> PrivateState:
        if not raw:
            return PrivateState(
                shed={p: 0 for p in PRODUCTS + list(ANIMALS)},
                seeds={c: 0 for c in CROPS},
                inventories=[{}],
            )
        shed_raw = _get(raw, "shed", {}) or {}
        seeds_raw = _get(raw, "seeds", {}) or {}
        inv_raw = _get(raw, "inventories", [{}]) or [{}]
        shed = {k: max(0, int(shed_raw.get(k, 0))) for k in (list(PRODUCTS) + list(ANIMALS))}
        seeds = {c: max(0, int(seeds_raw.get(c, 0))) for c in CROPS}
        inventories = [dict(iv) if isinstance(iv, dict) else {} for iv in inv_raw]
        return PrivateState(shed=shed, seeds=seeds, inventories=inventories)

    def _parse_town(self, raw: Any) -> TownState:
        if not raw:
            return TownState(unlocked_shops=[])
        shops = list(_get(raw, "unlocked_shops", []) or [])
        return TownState(unlocked_shops=shops)

    def _empty_farm(self, player_idx: int, cfg: GameConfig) -> FarmState:
        bs = cfg.board_size
        tiles = [
            [TileState(x=x, y=y, locked=True, empty=False, kind="LOCKED")
             for x in range(bs)]
            for y in range(bs)
        ]
        return FarmState(
            player_idx=player_idx,
            money=float(cfg.starting_money),
            tiles=tiles,
            farmer_pos=[bs // 2 - 1, bs // 2 - 1],
            hands=[],
            unlocked_quadrants=["NW"],
            hires_today=0,
        )

    def _safe_fallback(self, obs: Any) -> GameState:
        cfg = self.config
        step = 0
        try:
            step = int(_get(obs, "step", 0))
        except Exception:
            pass
        player = 0
        try:
            player = int(_get(obs, "player", 0))
        except Exception:
            pass
        turns_remaining = max(0, cfg.episode_steps - step)
        return GameState(
            step=step,
            player=player,
            day=0,
            hour=0,
            my_farm=self._empty_farm(player, cfg),
            opponent_farm=self._empty_farm(1 - player, cfg),
            market=MarketState(inventory={p: 10000 for p in PRODUCTS}, prices={}),
            private=PrivateState(
                shed={k: 0 for k in (list(PRODUCTS) + list(ANIMALS))},
                seeds={c: 0 for c in CROPS},
                inventories=[{}],
            ),
            town=TownState(unlocked_shops=[]),
            config=cfg,
            turns_remaining=turns_remaining,
            days_remaining=turns_remaining / max(1, cfg.turns_per_day),
            is_early_game=True,
            is_mid_game=False,
            is_late_game=False,
        )
