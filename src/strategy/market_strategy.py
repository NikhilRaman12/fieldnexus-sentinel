"""
market_strategy.py — market price tracking and intelligence.

Maintains in-process price history and provides scoring functions for
market-related decisions. Uses ONLY information available to the agent.
"""
from __future__ import annotations
import math
from collections import deque
from typing import Dict, List, Optional, Tuple
from ..kaggriculture.schema import (
    GameState, MarketState, PRODUCTS, MARKET_PARAMS, PRICE_FLOOR,
)


def _shape(func: str, x: float, T: float = 1.0) -> float:
    x = max(0.0, x)
    if func == "linear":
        return x
    if func == "sq":
        return x * x
    if func == "sqrt":
        return math.sqrt(x)
    if func == "log":
        return math.log(1.0 + x)
    if func == "log10":
        return math.log10(1.0 + x)
    if func == "hinge":
        if T <= 0:
            return x
        u = x / T
        return u + 8.0 * max(0.0, u - 1.0) ** 2
    return x


def compute_market_price(item: str, inventory: int,
                         params: Optional[Dict] = None) -> int:
    """Replicate the environment's market_price() function locally."""
    p = (params or MARKET_PARAMS).get(item, {})
    if not p:
        return PRICE_FLOOR
    base = p["base"]
    I0 = p["I0"]
    T = p["T"]
    if inventory < I0:
        f = p["below_func"]
        amp = p["below_target"] * base / _shape(f, T, T)
        price = base + amp * _shape(f, I0 - inventory, T)
    else:
        f = p["above_func"]
        amp = p["above_target"] * base / _shape(f, T, T)
        price = base - amp * _shape(f, inventory - I0, T)
    return max(PRICE_FLOOR, int(round(price)))


class MarketStrategy:
    """
    Tracks market prices across turns and provides sell/buy signals.
    """

    HISTORY_LEN = 48  # keep ~2 in-game days

    def __init__(self):
        self._price_history: Dict[str, deque] = {
            p: deque(maxlen=self.HISTORY_LEN) for p in PRODUCTS
        }
        self._inv_history: Dict[str, deque] = {
            p: deque(maxlen=self.HISTORY_LEN) for p in PRODUCTS
        }
        self._base_prices: Dict[str, int] = {
            p: MARKET_PARAMS[p]["base"] for p in PRODUCTS if p in MARKET_PARAMS
        }

    def update(self, state: GameState) -> None:
        """Record current market snapshot."""
        mkt = state.market
        for p in PRODUCTS:
            price = mkt.prices.get(p, self._base_prices.get(p, 0))
            inv = mkt.inventory.get(p, 10000)
            self._price_history[p].append(price)
            self._inv_history[p].append(inv)

    # ------------------------------------------------------------------
    # Price analysis
    # ------------------------------------------------------------------

    def current_price(self, item: str, state: GameState) -> int:
        return state.market.prices.get(item, self._base_prices.get(item, 0))

    def base_price(self, item: str) -> int:
        return self._base_prices.get(item, 0)

    def price_trend(self, item: str) -> float:
        """Positive = rising, negative = falling. Range roughly -1..+1."""
        hist = list(self._price_history.get(item, []))
        if len(hist) < 4:
            return 0.0
        recent = sum(hist[-4:]) / 4
        older = sum(hist[-8:-4]) / 4 if len(hist) >= 8 else hist[0]
        base = self._base_prices.get(item, 1)
        return (recent - older) / max(1, base)

    def price_vs_base(self, item: str, state: GameState) -> float:
        """
        Returns fraction: current_price / base_price.
        >1.0 means above base (favourable to sell).
        """
        base = self._base_prices.get(item, 1)
        current = self.current_price(item, state)
        return current / max(1, base)

    def sell_score(self, item: str, state: GameState) -> float:
        """
        Composite sell desirability score.
        Higher = more desirable to sell now.
        Considers: price vs base, trend, scarcity.
        """
        pvb = self.price_vs_base(item, state)
        trend = self.price_trend(item)
        inv = state.market.inventory.get(item, 10000)
        I0 = MARKET_PARAMS.get(item, {}).get("I0", 10000)
        scarcity = max(0.0, 1.0 - inv / max(1, I0))  # 0=plentiful, 1=scarce

        # Sell if price is high and/or trending up and market is scarce
        score = pvb * 0.5 + (1.0 + trend) * 0.3 + scarcity * 0.2
        return score

    def expected_sell_price(self, item: str, state: GameState) -> float:
        """Best estimate of price at which we'll sell this turn."""
        return float(self.current_price(item, state))

    def best_crop_to_plant(self, state: GameState, days_remaining: float) -> str:
        """
        Returns the crop name with highest expected profit given current market
        and remaining days.
        """
        from ..kaggriculture.schema import CROPS, MARKET_PARAMS
        best_crop = "WHEAT"
        best_score = -1e9

        for crop, cd in CROPS.items():
            if cd["first_yield_day"] > days_remaining:
                continue
            seed_cost = cd["seed"]
            base_price = self._base_prices.get(crop, 0)
            pvb = self.price_vs_base(crop, state)
            expected_price = base_price * pvb
            expected_yield = cd["max_yield"]
            profit = expected_yield * expected_price - seed_cost
            # Penalise by lock-up time
            lock_up_penalty = cd["first_yield_day"] / max(1.0, days_remaining)
            score = profit * (1.0 - lock_up_penalty * 0.3)
            if score > best_score:
                best_score = score
                best_crop = crop

        return best_crop

    def sell_market_ops(self, state: GameState, max_orders: int = 10) -> List[List]:
        """
        Generate SELL market ops for everything in shed above threshold.
        Returns list of [SELL, item, quantity] lists.
        """
        from ..kaggriculture.action_space import make_sell
        ops = []
        shed = state.private.shed
        for item in PRODUCTS:
            qty = shed.get(item, 0)
            if qty <= 0:
                continue
            # Only sell if price is reasonable
            pvb = self.price_vs_base(item, state)
            if pvb >= 0.7:  # don't sell at crash prices unless forced
                ops.append(make_sell(item, qty))
            if len(ops) >= max_orders:
                break
        return ops

    def emergency_sell_ops(self, state: GameState, max_orders: int = 10) -> List[List]:
        """Sell everything regardless of price (late-game liquidation)."""
        from ..kaggriculture.action_space import make_sell
        ops = []
        shed = state.private.shed
        for item in PRODUCTS:
            qty = shed.get(item, 0)
            if qty > 0:
                ops.append(make_sell(item, qty))
            if len(ops) >= max_orders:
                break
        return ops
