"""
economy_strategy.py — lightweight economic model for the agent.

Calculates:
  - current wealth (cash + inventory value + asset value)
  - projected income from planted crops and animals
  - liquidity
  - opportunity cost of candidate expenditures
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional

from ..kaggriculture.schema import (
    GameState, CROPS, ANIMALS, PRODUCTS, MARKET_PARAMS,
)


@dataclass
class EconomicSnapshot:
    cash: float
    shed_value: float
    planted_value: float        # expected value of all planted crops
    animal_value: float         # expected value from animals
    total_wealth: float
    projected_income: float     # remaining expected income this game
    days_remaining: float
    turns_remaining: int
    liquidity: float            # fraction of wealth that is liquid (cash + shed)


class EconomyStrategy:
    """
    Computes economic metrics and spending categories.
    """

    def snapshot(self, state: GameState, market) -> EconomicSnapshot:
        cash = state.cash()
        shed_value = self._shed_value(state, market)
        planted_value = self._planted_value(state, market)
        animal_value = self._animal_value(state, market)
        total = cash + shed_value + planted_value + animal_value
        liquid = cash + shed_value
        projected = planted_value + animal_value

        return EconomicSnapshot(
            cash=cash,
            shed_value=shed_value,
            planted_value=planted_value,
            animal_value=animal_value,
            total_wealth=total,
            projected_income=projected,
            days_remaining=state.days_remaining,
            turns_remaining=state.turns_remaining,
            liquidity=liquid / max(1.0, total),
        )

    def _shed_value(self, state: GameState, market) -> float:
        total = 0.0
        shed = state.private.shed
        for item in PRODUCTS:
            qty = shed.get(item, 0)
            if qty > 0:
                price = market.current_price(item, state)
                total += qty * price
        return total

    def _planted_value(self, state: GameState, market) -> float:
        """Expected revenue from all planted tiles."""
        total = 0.0
        day = state.day
        days_rem = state.days_remaining
        for tile in state.my_farm.plants():
            crop = tile.crop
            if not crop:
                continue
            cd = CROPS.get(crop, {})
            days_alive = day - tile.planted_day
            first_yield = cd.get("first_yield_day", 999)
            max_yield = cd.get("max_yield", 0)
            if days_alive >= first_yield and days_rem >= 0:
                price = market.current_price(crop, state)
                total += max_yield * price * 0.8  # 80% confidence discount
        return total

    def _animal_value(self, state: GameState, market) -> float:
        """Expected remaining production from animals."""
        total = 0.0
        day = state.day
        days_rem = state.days_remaining
        for tile in state.my_farm.animals():
            animal = tile.animal
            if not animal:
                continue
            ad = ANIMALS.get(animal, {})
            first_yield = ad.get("first_yield_day", 999)
            interval = ad.get("interval", 1)
            product = ad.get("product", "")
            if not product:
                continue
            days_alive = day - tile.placed_day
            if days_alive >= first_yield and interval > 0:
                remaining_yields = max(0, int(days_rem / interval))
                price = market.current_price(product, state)
                total += remaining_yields * price * 0.7
        return total

    def action_roi(self, cost: float, expected_gain: float,
                   days_to_gain: float, days_remaining: float) -> float:
        """
        Compute simple ROI for an action.
        Returns fraction: gain / cost  discounted by how close to game end.
        """
        if cost <= 0:
            return 1.0
        if days_remaining <= 0 or days_to_gain > days_remaining:
            return -1.0  # can't recoup before game ends
        time_discount = 1.0 - (days_to_gain / max(1.0, days_remaining)) * 0.5
        return (expected_gain * time_discount) / cost

    def classify_spending(self, cost: float, state: GameState) -> str:
        """
        Classify whether a spend is survival, productive, expansion, or speculative.
        """
        cash = state.cash()
        if cash - cost < 200:
            return "SURVIVAL_RISK"
        fraction = cost / max(1.0, cash)
        if fraction < 0.10:
            return "PRODUCTIVE"
        if fraction < 0.30:
            return "EXPANSION"
        return "SPECULATIVE"

    def minimum_cash_reserve(self, state: GameState) -> float:
        """
        Compute minimum cash we should keep on hand.
        Accounts for seed needs, potential hires, etc.
        """
        cfg = state.config
        # Base reserve: enough for 1 land purchase or 1 day of seeds
        base = min(cfg.starting_money * 0.15, 500)
        # If late game, reduce reserve (no point hoarding)
        if state.is_late_game:
            base *= 0.5
        return max(50.0, base)
