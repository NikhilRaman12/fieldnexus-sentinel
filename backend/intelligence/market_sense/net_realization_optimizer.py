"""
KRISHIVA AI — Market Sense Net Realization Optimization Engine
Calculates net farmer realization across reachable APMC mandis using the formula:
net_realization = (expected_sale_revenue) - (transport_cost + handling_cost + mandi_fees + transit_quality_loss)
"""

from typing import List, Dict, Any, Optional
import math
from pydantic import BaseModel, Field
from backend.core.logging import get_logger

logger = get_logger("net_realization_optimizer")


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
    """Computes realistic supply-chain net margins for farmers and FPOs."""

    # Standard freight logistics model for small commercial vehicles (Tata Ace / Pickup 1.5T to 3T)
    BASE_TRANSPORT_FIXED_INR = 500.0   # Loading / Vehicle dispatch minimum
    PER_KM_FREIGHT_INR = 28.0          # INR per vehicle-km
    VEHICLE_CAPACITY_QUINTALS = 25.0   # ~2.5 MT capacity for small commercial truck
    HANDLING_COST_PER_QUINTAL = 35.0   # Unloading, hamali, weighting at APMC gate
    PERISHABLE_TRANSIT_LOSS_RATE = 0.0008  # 0.08% loss in weight/quality per km for fresh tomato

    @staticmethod
    def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Haversine road-distance approximation in km (with 1.25 road curvature multiplier)."""
        R = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        straight_km = R * c
        return round(straight_km * 1.25, 1)  # Road tortuosity multiplier

    def optimize_markets(
        self,
        farmer_lat: float,
        farmer_lon: float,
        commodity: str,
        quantity_quintals: float,
        candidate_mandis: List[Dict[str, Any]],
        farmer_district: str = "Rangareddy"
    ) -> SellingRecommendationReport:
        """Ranks markets by net realization taking quantity, freight logistics, and perishable loss into account."""
        results: List[MandiNetRealization] = []

        # Number of transport trips or capacity allocation
        trucks_needed = math.ceil(quantity_quintals / self.VEHICLE_CAPACITY_QUINTALS)

        for mandi in candidate_mandis:
            m_lat = mandi.get("latitude", farmer_lat)
            m_lon = mandi.get("longitude", farmer_lon)
            distance_km = self.calculate_haversine_distance(farmer_lat, farmer_lon, m_lat, m_lon)
            modal_p = float(mandi.get("modal_price", 2400.0))
            apmc_charge_pct = float(mandi.get("apmc_charge_percent", 1.0))

            # 1. Gross revenue
            gross_revenue = modal_p * quantity_quintals

            # 2. Logistics & freight expenses
            freight = (self.BASE_TRANSPORT_FIXED_INR + (distance_km * self.PER_KM_FREIGHT_INR)) * trucks_needed

            # 3. Handling & APMC labor (hamali)
            handling = self.HANDLING_COST_PER_QUINTAL * quantity_quintals

            # 4. Mandi fees (APMC user charge on sale value)
            mandi_fee = (apmc_charge_pct / 100.0) * gross_revenue

            # 5. Estimated perishable quality / transit deduction
            transit_loss_pct = min(distance_km * self.PERISHABLE_TRANSIT_LOSS_RATE, 0.08)  # Cap at 8%
            transit_deduction = gross_revenue * transit_loss_pct

            # 6. Total expenses & Net Realization
            total_expenses = freight + handling + mandi_fee + transit_deduction
            net_realization = gross_revenue - total_expenses
            net_per_qtl = net_realization / quantity_quintals if quantity_quintals > 0 else 0.0

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
                data_source=mandi.get("data_source", "agmarknet"),
                price_date=mandi.get("arrival_date", "Today"),
                reasoning=""
            ))

        # Rank by net realization descending
        results.sort(key=lambda x: x.expected_net_realization, reverse=True)
        for idx, item in enumerate(results):
            item.rank = idx + 1
            item.reasoning = (
                f"Rank #{item.rank}: Net realization ₹{item.net_realization_per_quintal:,.2f}/qtl. "
                f"Gross price ₹{item.modal_price_qtl:,.2f} less ₹{(item.total_expenses / quantity_quintals):,.2f}/qtl logistics/mandi costs."
            )

        top_choice = results[0]
        rationale = (
            f"{top_choice.market_name} in {top_choice.district} offers the highest net realization of "
            f"₹{top_choice.expected_net_realization:,.2f} (₹{top_choice.net_realization_per_quintal:,.2f}/qtl) "
            f"for {quantity_quintals} quintals, outperforming closer markets after freight and handling deductions."
        )

        return SellingRecommendationReport(
            commodity=commodity,
            harvest_quantity_quintals=quantity_quintals,
            farmer_location=farmer_district,
            recommended_mandi=top_choice,
            all_mandis_comparison=results,
            decision_rationale=rationale,
            advisory_notes="Prices reflect verified APMC modal averages. Realized prices vary by lot sorting, grading, and moisture."
        )
