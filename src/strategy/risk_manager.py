"""
risk_manager.py — classifies current game risk and adjusts strategy mode.
"""
from __future__ import annotations
from enum import Enum
from ..kaggriculture.schema import GameState


class RiskMode(Enum):
    SAFE = "SAFE"
    NORMAL = "NORMAL"
    AGGRESSIVE = "AGGRESSIVE"


class RiskManager:
    """
    Determines the current risk mode based on game state.
    Modes:
        SAFE       — low cash or late game → conserve, harvest, sell
        NORMAL     — standard operation → balanced grow/invest
        AGGRESSIVE — high cash, early game, behind opponent → expand fast
    """

    def __init__(self, safe_fraction: float = 0.15, aggressive_fraction: float = 0.60):
        self.safe_fraction = safe_fraction
        self.aggressive_fraction = aggressive_fraction

    def classify(self, state: GameState) -> RiskMode:
        cash = state.cash()
        total_turns = state.config.episode_steps
        turns_rem = state.turns_remaining
        horizon_fraction = turns_rem / max(1, total_turns)

        # Late game → always safe (preserve value)
        if horizon_fraction < 0.15:
            return RiskMode.SAFE

        # Cash risk
        starting = float(state.config.starting_money)
        cash_fraction = cash / max(1.0, starting)

        if cash_fraction < self.safe_fraction:
            return RiskMode.SAFE
        if cash_fraction > self.aggressive_fraction and horizon_fraction > 0.40:
            return RiskMode.AGGRESSIVE
        return RiskMode.NORMAL

    def can_expand(self, state: GameState, mode: RiskMode, cost: float) -> bool:
        """Returns True if expansion is permitted in current risk mode."""
        if mode == RiskMode.SAFE:
            return False
        cash = state.cash()
        # Always keep a buffer
        buffer = cost * 0.4 if mode == RiskMode.NORMAL else cost * 0.2
        return cash >= cost + buffer

    def max_seeds_to_buy(self, state: GameState, mode: RiskMode,
                         seed_price: int) -> int:
        """Maximum seeds to buy given risk mode."""
        cash = state.cash()
        reserve = cash * (0.3 if mode == RiskMode.NORMAL else 0.15)
        spendable = max(0.0, cash - reserve)
        if seed_price <= 0:
            return 0
        return int(spendable // seed_price)
