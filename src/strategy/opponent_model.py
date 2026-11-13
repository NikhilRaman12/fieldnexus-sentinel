"""
opponent_model.py — lightweight opponent behavior profiling.

Tracks observed opponent actions/state changes across turns and maintains a
confidence-weighted strategy profile. Influences our strategy only when
confidence is sufficient.
"""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional

from ..kaggriculture.schema import GameState, FarmState


class OpponentProfile(Enum):
    UNKNOWN = "UNKNOWN"
    BALANCED = "BALANCED"
    GROWTH = "GROWTH"              # aggressive land expansion
    CASH_ACCUMULATION = "CASH_ACC" # saves money, minimal spending
    CROP_SPECIALIST = "CROP_SPEC"  # plants densely
    LIVESTOCK_FOCUSED = "LIVESTOCK"
    AGGRESSIVE = "AGGRESSIVE"      # high spending, fast expansion


@dataclass
class OpponentSignal:
    """Running counters of opponent observations."""
    turns_observed: int = 0
    land_expansions: int = 0
    plants_placed: int = 0
    animals_placed: int = 0
    workers_hired: int = 0
    last_money: float = 3000.0
    money_delta_sum: float = 0.0   # sum of Δmoney across turns
    harvest_turns: int = 0         # turns where money increased significantly

    # Derived
    profile: OpponentProfile = OpponentProfile.UNKNOWN
    confidence: float = 0.0


class OpponentModel:
    """
    Observes opponent farm state changes and infers strategic intent.
    """

    # Minimum turns before profile confidence is trusted
    MIN_CONFIDENCE_TURNS: int = 24
    # Minimum confidence before influencing our decisions
    USE_PROFILE_CONFIDENCE: float = 0.4

    def __init__(self):
        self._signal = OpponentSignal()
        self._prev_opp: Optional[FarmState] = None

    def update(self, state: GameState) -> None:
        """Call every turn with the latest game state."""
        opp = state.opponent_farm
        sig = self._signal

        if self._prev_opp is not None:
            prev = self._prev_opp
            # Land expansions
            if len(opp.unlocked_quadrants) > len(prev.unlocked_quadrants):
                sig.land_expansions += 1
            # Plant additions
            curr_plants = len(opp.plants()) if hasattr(opp, "plants") else 0
            prev_plants = len(prev.plants()) if hasattr(prev, "plants") else 0
            if curr_plants > prev_plants:
                sig.plants_placed += curr_plants - prev_plants
            # Animal additions
            curr_animals = len(opp.animals()) if hasattr(opp, "animals") else 0
            prev_animals = len(prev.animals()) if hasattr(prev, "animals") else 0
            if curr_animals > prev_animals:
                sig.animals_placed += curr_animals - prev_animals
            # Worker additions
            if len(opp.hands) > len(prev.hands):
                sig.workers_hired += len(opp.hands) - len(prev.hands)
            # Money delta
            delta = opp.money - prev.money
            sig.money_delta_sum += delta
            if delta > 100:
                sig.harvest_turns += 1

        sig.turns_observed += 1
        sig.last_money = opp.money

        # Update profile
        self._infer_profile()
        self._prev_opp = opp

    def _infer_profile(self) -> None:
        sig = self._signal
        t = max(1, sig.turns_observed)

        if t < 8:
            sig.profile = OpponentProfile.UNKNOWN
            sig.confidence = 0.0
            return

        # Compute confidence (grows with observations, capped at 1.0)
        sig.confidence = min(1.0, t / max(1, self.MIN_CONFIDENCE_TURNS))

        # Score each profile
        land_rate = sig.land_expansions / t
        plant_rate = sig.plants_placed / t
        animal_rate = sig.animals_placed / t
        worker_rate = sig.workers_hired / t
        avg_money_delta = sig.money_delta_sum / t

        scores: Dict[OpponentProfile, float] = defaultdict(float)
        scores[OpponentProfile.GROWTH] += land_rate * 100
        scores[OpponentProfile.CROP_SPECIALIST] += plant_rate * 50
        scores[OpponentProfile.LIVESTOCK_FOCUSED] += animal_rate * 80
        scores[OpponentProfile.CASH_ACCUMULATION] += max(0, -avg_money_delta * 0.01)
        scores[OpponentProfile.AGGRESSIVE] += (land_rate + plant_rate + worker_rate) * 30
        if sig.harvest_turns > t * 0.3:
            scores[OpponentProfile.BALANCED] += 20

        best = max(scores, key=lambda k: scores[k])
        best_score = scores[best]
        if best_score < 2.0:
            sig.profile = OpponentProfile.BALANCED
        else:
            sig.profile = best

    @property
    def profile(self) -> OpponentProfile:
        return self._signal.profile

    @property
    def confidence(self) -> float:
        return self._signal.confidence

    def should_use(self) -> bool:
        return self._signal.confidence >= self.USE_PROFILE_CONFIDENCE

    def profile_adjustment(self) -> float:
        """
        Returns a score modifier [-0.2, +0.2] for our expansion decisions
        based on opponent strategy. Penalize if opponent is GROWTH/AGGRESSIVE.
        """
        if not self.should_use():
            return 0.0
        if self._signal.profile in (OpponentProfile.GROWTH, OpponentProfile.AGGRESSIVE):
            # Opponent expanding fast → we should expand too (positive urge)
            return 0.15
        if self._signal.profile == OpponentProfile.CASH_ACCUMULATION:
            # Opponent saving → price pressure may come later → be cautious
            return -0.05
        return 0.0

    def summary(self) -> str:
        sig = self._signal
        return (
            f"OpponentModel: {sig.profile.value} "
            f"(conf={sig.confidence:.2f}, turns={sig.turns_observed}, "
            f"lands={sig.land_expansions}, plants={sig.plants_placed}, "
            f"animals={sig.animals_placed})"
        )
