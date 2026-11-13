"""
configs/strategy_config.py — competition strategy weights and thresholds.

All parameters are pure Python (no YAML dependency).
Tune via tournament_runner.py benchmark results.
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class StrategyConfig:
    # -----------------------------------------------------------------------
    # Action scoring weights (must sum doesn't matter; relative importance)
    # -----------------------------------------------------------------------
    weight_economy: float = 0.35
    weight_future: float = 0.25
    weight_risk: float = 0.20
    weight_opponent: float = 0.10
    weight_terminal: float = 0.10

    # -----------------------------------------------------------------------
    # Crop strategy
    # -----------------------------------------------------------------------
    # Minimum turns remaining before we plant a crop (avoids dead investments)
    min_turns_for_plant: int = 10
    # Water priority: unwatered count to start stressing
    water_stress_threshold: int = 2
    # Fertilizer ROI multiplier threshold for usage
    fertilizer_roi_threshold: float = 1.5

    # -----------------------------------------------------------------------
    # Land expansion
    # -----------------------------------------------------------------------
    # Only buy land when expected_ROI over remaining game >= this
    land_roi_threshold: float = 1.2
    # Minimum cash buffer after land purchase
    land_cash_buffer_fraction: float = 0.4

    # -----------------------------------------------------------------------
    # Worker strategy
    # -----------------------------------------------------------------------
    # Only hire when turns_remaining >= this (not worth it near end)
    min_turns_to_hire: int = 48
    # Minimum expected productivity gain per hire (in currency equivalent)
    hire_productivity_threshold: float = 200.0

    # -----------------------------------------------------------------------
    # Livestock strategy
    # -----------------------------------------------------------------------
    # Only buy animal when days_remaining >= first_yield_day * this multiple
    animal_roi_days_multiple: float = 2.0

    # -----------------------------------------------------------------------
    # Market / selling
    # -----------------------------------------------------------------------
    # Sell when price is above this fraction of base price
    sell_price_threshold: float = 0.9
    # Emergency sell threshold (price crash) — sell anyway if below this
    emergency_sell_fraction: float = 0.5

    # -----------------------------------------------------------------------
    # Risk thresholds
    # -----------------------------------------------------------------------
    # Cash fraction below which we switch to SAFE mode
    safe_mode_cash_fraction: float = 0.15
    # Cash fraction above which we allow AGGRESSIVE expansion
    aggressive_mode_cash_fraction: float = 0.60

    # -----------------------------------------------------------------------
    # Lookahead
    # -----------------------------------------------------------------------
    rollout_depth: int = 1
    rollout_enabled: bool = True

    # -----------------------------------------------------------------------
    # Terminal horizon
    # -----------------------------------------------------------------------
    # Days remaining below which we stop planting non-ongoing crops
    terminal_horizon_days: float = 5.0
    # Days remaining below which we start emergency liquidation
    liquidation_horizon_days: float = 3.0

    # -----------------------------------------------------------------------
    # Debug
    # -----------------------------------------------------------------------
    debug: bool = False


# Default instance used by main.py and strategy engine
DEFAULT_CONFIG = StrategyConfig()
