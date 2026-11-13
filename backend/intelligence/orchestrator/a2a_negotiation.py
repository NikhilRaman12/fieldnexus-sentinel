"""
KRISHIVA AI — Agent-to-Agent (A2A) Autonomous Negotiation & Collaboration Protocol
Implements structured, typed protocol for multi-agent inter-communication:
- CropGuardAgent <-> InputTrustAgent (Pathogen favorability & regulatory constraints)
- CropGuardAgent <-> MarketSenseAgent (Harvest quality impact & optimal picking dates)
- InputTrustAgent <-> MarketSenseAgent (Pre-Harvest Interval & market sale window compliance)
- KrishivaSupervisor (Master Consensus & Orchestration)
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
from pydantic import BaseModel, Field
from backend.core.logging import get_logger

logger = get_logger("a2a_protocol")


class A2AMessage(BaseModel):
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender_agent: str
    receiver_agent: str
    intent: str  # QUERY_EVALUATION, RISK_ALERT, CONSTRAINT_NOTICE, PROPOSAL_OFFER, CONSENSUS_ACK
    topic: str   # PATHOGEN_PRESSURE, PHI_RESTRICTION, HARVEST_TIMING, NET_PRICE_OPPORTUNITY
    payload: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class A2ANegotiationSession(BaseModel):
    session_id: str
    messages: List[A2AMessage] = []
    active_consensus: Dict[str, Any] = {}
    consensus_status: str = "IN_PROGRESS"  # IN_PROGRESS, REACHED, ESCALATED


class AgentToAgentNegotiator:
    """Manages autonomous typed negotiation between KRISHIVA specialized intelligence agents."""

    def __init__(self):
        logger.info("Initialized Agent-to-Agent (A2A) Negotiation Engine.")

    def negotiate_harvest_and_treatment(
        self,
        crop: str,
        detected_threat: str,
        threat_level: str,
        selected_chemical_phi_days: int,
        current_mandi_modal_price: float,
        planned_harvest_days_away: int
    ) -> A2ANegotiationSession:
        """
        Coordinates cross-agent negotiation between CropGuard, InputTrust, and MarketSense:
        1. CropGuard alerts InputTrust and MarketSense of active pathogen risk.
        2. InputTrust verifies CIB&RC treatment and imposes mandatory Pre-Harvest Interval (PHI).
        3. MarketSense analyzes if spraying now violates the planned harvest date or market price window.
        4. Agents establish consensus resolution (e.g. bio-fungicide with 0-day PHI vs chemical with harvest delay).
        """
        session_id = f"a2a-neg-{uuid.uuid4().hex[:8]}"
        session = A2ANegotiationSession(session_id=session_id)

        # Message 1: CropGuard -> InputTrust & MarketSense
        m1 = A2AMessage(
            sender_agent="CropGuardAgent",
            receiver_agent="InputTrustAgent",
            intent="RISK_ALERT",
            topic="PATHOGEN_PRESSURE",
            payload={
                "crop": crop,
                "threat": detected_threat,
                "severity": threat_level,
                "urgency": "IMMEDIATE_ACTION_RECOMMENDED"
            }
        )
        session.messages.append(m1)

        # Message 2: InputTrust -> MarketSense (Constraint Notice)
        conflict_detected = (planned_harvest_days_away < selected_chemical_phi_days)
        m2 = A2AMessage(
            sender_agent="InputTrustAgent",
            receiver_agent="MarketSenseAgent",
            intent="CONSTRAINT_NOTICE",
            topic="PHI_RESTRICTION",
            payload={
                "chemical_phi_days": selected_chemical_phi_days,
                "planned_harvest_days": planned_harvest_days_away,
                "regulatory_conflict": conflict_detected,
                "compliance_rule": "Insecticides Act Section 9(3) Pre-Harvest Safety"
            }
        )
        session.messages.append(m2)

        # Message 3: MarketSense -> KrishivaSupervisor (Economic Proposal)
        if conflict_detected:
            proposal = (
                f"Harvest planned in {planned_harvest_days_away} days collides with {selected_chemical_phi_days}-day PHI. "
                f"Market price is currently strong at ₹{current_mandi_modal_price:.2f}/qtl. "
                f"MarketSense recommends: Switch to Bio-Control (Trichoderma or Copper 0-1 day PHI) "
                f"to preserve immediate market selling window, or postpone harvest by {selected_chemical_phi_days - planned_harvest_days_away} days."
            )
            consensus_resolution = {
                "action": "SUBSTITUTE_LOW_PHI_INPUT_OR_DELAY_HARVEST",
                "recommended_input_override": "Eco-friendly Biological / Minimum PHI alternative",
                "allow_immediate_harvest": False,
                "market_window_impact": "Protected from chemical residue rejection at APMC"
            }
        else:
            proposal = "Treatment schedule satisfies regulatory waiting period without impacting harvest realization."
            consensus_resolution = {
                "action": "PROCEED_WITH_STANDARD_SCHEDULE",
                "allow_immediate_harvest": True
            }

        m3 = A2AMessage(
            sender_agent="MarketSenseAgent",
            receiver_agent="KrishivaSupervisor",
            intent="PROPOSAL_OFFER",
            topic="NET_PRICE_OPPORTUNITY",
            payload={"recommendation_proposal": proposal, "current_price": current_mandi_modal_price}
        )
        session.messages.append(m3)

        session.active_consensus = consensus_resolution
        session.consensus_status = "REACHED"
        logger.info(f"A2A Multi-Agent Consensus reached for session {session_id}: {session.consensus_status}")
        return session
