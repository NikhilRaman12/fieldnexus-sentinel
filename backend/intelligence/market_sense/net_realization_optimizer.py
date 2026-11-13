"""
KRISHIVA AI — Market Sense Net Realization Optimization Engine
Calculates net farmer realization across reachable APMC mandis using the formula:
net_realization = (expected_sale_revenue) - (transport_cost + handling_cost + mandi_fees + transit_quality_loss)

Fixes applied:
- Strict validation: quantity > 0 (rejects zero/negative volumes).
- Transparent exposure of all individual cost assumptions and formulas to the UI/API.
- Fix modal_price vs base_modal_price mapping.
- Clear labeling of simulated vs live price sources.
"""

from typing import List, Dict, Any, Optional
import math
from pydantic import BaseModel, Field
from backend.core.logging import get_logger

logger = get_logger("net_realization_optimizer")


class CostBreakdownAssumptions(BaseModel):
    base_fixed_freight_inr: float = 500.0
    per_km_freight_inr: float = 28.0
    vehicle_capacity_quintals: float = 25.0
    trucks_allocated: int
    handling_per_quintal_inr: float = 35.0
    mandi_fee_percent: float = 1.0
    perishability_loss_rate_per_km: float = 0.0008
    perishability_cap_percent: float = 8.0


class MandiNetRealization(BaseModel):
    market_name: str
    district: str
    state: str
    distance_km: float
    modal_price_qtl: float
    expected_gross_revenue: float
    transport_cost: float
    handling_cost: float
    mandi_fees: float
    transit_quality_loss: float
    total_expenses: float
    expected_net_realization: float
    net_realization_per_quintal: float
    rank: int
    data_source: str
    price_date: str
    is_live: bool = False
    warning_notice: Optional[str] = None
    cost_assumptions: CostBreakdownAssumptions
    reasoning: str


class SellingRecommendationReport(BaseModel):
    commodity: str
    harvest_quantity_quintals: float
    farmer_location: str
    recommended_mandi: MandiNetRealization
    all_mandis_comparison: List[MandiNetRealization]
    decision_rationale: str
    advisory_notes: str


class NetRealizationOptimizer:
    """Computes transparent supply-chain net margins for farmers and FPOs."""

    BASE_TRANSPORT_FIXED_INR = 500.0
    PER_KM_FREIGHT_INR = 28.0
    VEHICLE_CAPACITY_QUINTALS = 25.0
    HANDLING_COST_PER_QUINTAL = 35.0
    PERISHABLE_TRANSIT_LOSS_RATE = 0.0008

    @staticmethod
    def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Haversine road-distance approximation in km (with 1.25 road curvature multiplier)."""
        R = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return round((R * c) * 1.25, 1)

    def optimize_markets(
        self,
        farmer_lat: float,
        farmer_lon: float,
        commodity: str,
        quantity_quintals: float,
        candidate_mandis: List[Dict[str, Any]],
        farmer_district: str = "Rangareddy"
    ) -> SellingRecommendationReport:
        """Ranks markets by net realization with validated quantity > 0 and transparent cost disclosures."""
        if quantity_quintals <= 0:
            raise ValueError(f"Harvest quantity must be greater than zero. Received: {quantity_quintals} quintals.")

        results: List[MandiNetRealization] = []
        trucks_needed = max(1, math.ceil(quantity_quintals / self.VEHICLE_CAPACITY_QUINTALS))

        for mandi in candidate_mandis:
            m_lat = mandi.get("latitude", farmer_lat)
            m_lon = mandi.get("longitude", farmer_lon)
            distance_km = self.calculate_haversine_distance(farmer_lat, farmer_lon, m_lat, m_lon)

            # FIX: Ensure modal_price is retrieved accurately regardless of base_modal_price vs modal_price key
            modal_p = float(mandi.get("modal_price", mandi.get("base_modal_price", 2400.0)))
            apmc_charge_pct = float(mandi.get("apmc_charge_percent", 1.0))
            is_live_data = bool(mandi.get("is_live", False))
            src = mandi.get("data_source", "DEMO_SIMULATED")

            # 1. Gross revenue
            gross_revenue = modal_p * quantity_quintals

            # 2. Logistics & freight expenses
            freight = (self.BASE_TRANSPORT_FIXED_INR + (distance_km * self.PER_KM_FREIGHT_INR)) * trucks_needed

            # 3. Handling & APMC labor (hamali)
            handling = self.HANDLING_COST_PER_QUINTAL * quantity_quintals

            # 4. Mandi fees (APMC user charge on sale value)
            mandi_fee = (apmc_charge_pct / 100.0) * gross_revenue

            # 5. Estimated perishable quality / transit deduction
            transit_loss_pct = min(distance_km * self.PERISHABLE_TRANSIT_LOSS_RATE, 0.08)
            transit_deduction = gross_revenue * transit_loss_pct

            # 6. Total expenses & Net Realization
            total_expenses = freight + handling + mandi_fee + transit_deduction
            net_realization = gross_revenue - total_expenses
            net_per_qtl = net_realization / quantity_quintals

            cost_assumptions = CostBreakdownAssumptions(
                base_fixed_freight_inr=self.BASE_TRANSPORT_FIXED_INR,
                per_km_freight_inr=self.PER_KM_FREIGHT_INR,
                vehicle_capacity_quintals=self.VEHICLE_CAPACITY_QUINTALS,
                trucks_allocated=trucks_needed,
                handling_per_quintal_inr=self.HANDLING_COST_PER_QUINTAL,
                mandi_fee_percent=apmc_charge_pct,
                perishability_loss_rate_per_km=self.PERISHABLE_TRANSIT_LOSS_RATE,
                perishability_cap_percent=8.0
            )

            results.append(MandiNetRealization(
                market_name=mandi.get("market", "APMC Mandi"),
                district=mandi.get("district", "Unknown"),
                state=mandi.get("state", "Telangana"),
                distance_km=distance_km,
                modal_price_qtl=modal_p,
                expected_gross_revenue=round(gross_revenue, 2),
                transport_cost=round(freight, 2),
                handling_cost=round(handling, 2),
                mandi_fees=round(mandi_fee, 2),
                transit_quality_loss=round(transit_deduction, 2),
                total_expenses=round(total_expenses, 2),
                expected_net_realization=round(net_realization, 2),
                net_realization_per_quintal=round(net_per_qtl, 2),
                rank=0,
                data_source=src,
                price_date=mandi.get("arrival_date", "SIMULATED_REFERENCE_WINDOW"),
                is_live=is_live_data,
                warning_notice=mandi.get("warning_notice"),
                cost_assumptions=cost_assumptions,
                reasoning=""
            ))

        # Rank by net realization descending
        results.sort(key=lambda x: x.expected_net_realization, reverse=True)
        for idx, item in enumerate(results):
            item.rank = idx + 1
            item.reasoning = (
                f"Rank #{item.rank}: Net realization ₹{item.net_realization_per_quintal:,.2f}/qtl. "
                f"Gross price ₹{item.modal_price_qtl:,.2f} less ₹{(item.total_expenses / quantity_quintals):,.2f}/qtl "
                f"transport/mandi expenses ({trucks_needed} truck{'s' if trucks_needed > 1 else ''} for {quantity_quintals} qtl)."
            )

        top_choice = results[0]
        rationale = (
            f"{top_choice.market_name} in {top_choice.district} yields highest net realization of "
            f"₹{top_choice.expected_net_realization:,.2f} (₹{top_choice.net_realization_per_quintal:,.2f}/qtl) "
            f"for {quantity_quintals} quintals after freight (₹{top_choice.transport_cost}), handling (₹{top_choice.handling_cost}), "
            f"and mandi charges (₹{top_choice.mandi_fees})."
        )

        return SellingRecommendationReport(
            commodity=commodity,
            harvest_quantity_quintals=quantity_quintals,
            farmer_location=farmer_district,
            recommended_mandi=top_choice,
            all_mandis_comparison=results,
            decision_rationale=rationale,
            advisory_notes="All freight and handling rates are explicitly broken down. When using DEMO_SIMULATED data, figures represent reference scenarios."
        )
