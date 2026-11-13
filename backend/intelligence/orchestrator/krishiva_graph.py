"""
KRISHIVA AI — Central LangGraph Multi-Agent Orchestrator
Coordinates three independent intelligence subgraphs:
1. Crop Guard Subgraph (Pest, disease, weather, crop risk)
2. Market Sense Subgraph (APMC discovery, arrivals, price forecasting, net realization)
3. Input Trust Subgraph (Differential diagnosis, CIB&RC/FCO regulatory verification)
"""

from typing import Dict, Any, List, Optional, TypedDict
from datetime import datetime
from langgraph.graph import StateGraph, END
from pydantic import BaseModel

from backend.intelligence.crop_guard.crop_guard_engine import CropGuardEngine, RiskAssessmentOutput
from backend.intelligence.market_sense.net_realization_optimizer import NetRealizationOptimizer, SellingRecommendationReport
from backend.intelligence.input_trust.input_trust_engine import InputTrustEngine, DiagnosticInterventionReport
from backend.integrations.weather.weather_adapter import WeatherAdapter
from backend.integrations.agmarknet.agmarknet_adapter import AgmarknetAdapter
from backend.integrations.google_ai.gemini_client import GoogleAIProvider, GeminiExplanationRequest
from backend.core.logging import get_logger

logger = get_logger("krishiva_orchestrator")


class KrishivaAgentState(TypedDict):
    # Context
    session_id: str
    farmer_id: str
    plot_id: Optional[str]
    crop: str
    variety: Optional[str]
    district: str
    latitude: float
    longitude: float
    crop_stage: str

    # User inputs
    farmer_query: Optional[str]
    symptom_location: Optional[str]
    harvest_quantity_quintals: Optional[float]
    soil_ph: Optional[float]
    has_soil_test: bool
    preferred_language: str

    # System telemetry & external data
    weather_data: Optional[Dict[str, Any]]
    mandi_data: Optional[List[Dict[str, Any]]]

    # Subsystem outputs
    crop_guard_results: Optional[List[Dict[str, Any]]]
    market_sense_results: Optional[Dict[str, Any]]
    input_trust_results: Optional[Dict[str, Any]]

    # Synthesis & Audit
    synthesized_explanation: Optional[Dict[str, Any]]
    human_review_required: bool
    status: str
    errors: List[str]
    execution_trace: List[str]


class KrishivaOrchestrator:
    """Production LangGraph orchestrator coordinating modular agricultural intelligence."""

    def __init__(self):
        self.weather_adapter = WeatherAdapter()
        self.agmarknet_adapter = AgmarknetAdapter()
        self.crop_guard_engine = CropGuardEngine()
        self.market_sense_engine = NetRealizationOptimizer()
        self.input_trust_engine = InputTrustEngine()
        self.google_ai_provider = GoogleAIProvider()
        self.workflow = self._build_graph()

    def _build_graph(self):
        builder = StateGraph(KrishivaAgentState)

        # Nodes
        builder.add_node("context_and_telemetry_node", self._context_and_telemetry_node)
        builder.add_node("crop_guard_node", self._crop_guard_node)
        builder.add_node("input_trust_node", self._input_trust_node)
        builder.add_node("market_sense_node", self._market_sense_node)
        builder.add_node("supervisor_synthesis_node", self._supervisor_synthesis_node)

        # Edges
        builder.set_entry_point("context_and_telemetry_node")
        builder.add_edge("context_and_telemetry_node", "crop_guard_node")
        builder.add_edge("crop_guard_node", "input_trust_node")
        builder.add_edge("input_trust_node", "market_sense_node")
        builder.add_edge("market_sense_node", "supervisor_synthesis_node")
        builder.add_edge("supervisor_synthesis_node", END)

        return builder.compile()

    def _context_and_telemetry_node(self, state: KrishivaAgentState) -> Dict[str, Any]:
        """Fetches live meteorological observations and APMC market prices."""
        trace = list(state.get("execution_trace", []))
        trace.append("Executed Context & Telemetry Node: Acquired live weather and mandi baseline.")
        errors = list(state.get("errors", []))

        weather_dict = None
        mandi_list = None

        try:
            weather_snap = self.weather_adapter.fetch_weather(state["latitude"], state["longitude"])
            weather_dict = {
                "temperature_c": weather_snap.current.temperature_c,
                "relative_humidity_percent": weather_snap.current.relative_humidity_percent,
                "precipitation_mm": weather_snap.current.precipitation_mm,
                "wind_speed_kmh": weather_snap.current.wind_speed_kmh,
                "forecast_days": len(weather_snap.forecast_7d)
            }
        except Exception as e:
            errors.append(f"Weather acquisition error: {str(e)}")

        try:
            mandis = self.agmarknet_adapter.fetch_mandi_prices(
                state="Telangana",
                commodity=state["crop"],
                limit=10
            )
            mandi_list = [m.model_dump() for m in mandis]
        except Exception as e:
            errors.append(f"Mandi acquisition error: {str(e)}")

        return {
            "weather_data": weather_dict,
            "mandi_data": mandi_list,
            "execution_trace": trace,
            "errors": errors
        }

    def _crop_guard_node(self, state: KrishivaAgentState) -> Dict[str, Any]:
        """Evaluates micro-climatic pest and disease risks."""
        trace = list(state.get("execution_trace", []))
        trace.append("Executed Crop Guard Subgraph: Evaluated disease favorability indexes.")

        weather = state.get("weather_data") or {
            "temperature_c": 28.0,
            "relative_humidity_percent": 75.0,
            "precipitation_mm": 2.0
        }

        assessments = self.crop_guard_engine.evaluate_tomato_risks(
            temperature_c=weather["temperature_c"],
            relative_humidity_percent=weather["relative_humidity_percent"],
            rainfall_24h_mm=weather["precipitation_mm"],
            crop_stage=state.get("crop_stage", "flowering"),
            variety=state.get("variety", "Hybrid Tomato"),
            district=state.get("district", "Rangareddy")
        )

        requires_review = any(a.human_review_required for a in assessments)

        return {
            "crop_guard_results": [a.model_dump() for a in assessments],
            "human_review_required": requires_review,
            "execution_trace": trace
        }

    def _input_trust_node(self, state: KrishivaAgentState) -> Dict[str, Any]:
        """Executes differential diagnosis and CIB&RC/FCO regulatory input validation."""
        trace = list(state.get("execution_trace", []))
        trace.append("Executed Input Trust Subgraph: Completed differential diagnosis and regulatory verification.")

        query = state.get("farmer_query") or "Concentric dark brown spots on lower foliage with slight yellow halos."
        loc = state.get("symptom_location") or "lower_leaf"

        report = self.input_trust_engine.diagnose_and_recommend(
            crop=state.get("crop", "Tomato"),
            symptom_description=query,
            symptom_location=loc,
            crop_stage=state.get("crop_stage", "flowering"),
            has_soil_test=state.get("has_soil_test", False),
            soil_ph=state.get("soil_ph")
        )

        return {
            "input_trust_results": report.model_dump(),
            "execution_trace": trace
        }

    def _market_sense_node(self, state: KrishivaAgentState) -> Dict[str, Any]:
        """Calculates net realization across nearby APMC mandis."""
        trace = list(state.get("execution_trace", []))
        trace.append("Executed Market Sense Subgraph: Computed net realization across APMC mandis.")

        qty = state.get("harvest_quantity_quintals") or 50.0  # Default 50 quintals (5 tonnes)
        mandi_pool = self.agmarknet_adapter.TELANGANA_MANDIS

        report = self.market_sense_engine.optimize_markets(
            farmer_lat=state["latitude"],
            farmer_lon=state["longitude"],
            commodity=state["crop"],
            quantity_quintals=qty,
            candidate_mandis=mandi_pool,
            farmer_district=state["district"]
        )

        return {
            "market_sense_results": report.model_dump(),
            "execution_trace": trace
        }

    def _supervisor_synthesis_node(self, state: KrishivaAgentState) -> Dict[str, Any]:
        """Synthesizes unified farm intelligence using Google Gemini."""
        trace = list(state.get("execution_trace", []))
        trace.append("Executed Supervisor Synthesis Node: Formulated multilingual farmer explanation.")

        cg_summary = ""
        if state.get("crop_guard_results"):
            top_risk = state["crop_guard_results"][0]
            cg_summary += f"Crop risk: {top_risk['threat']} ({top_risk['risk_category']}). "

        it_summary = ""
        if state.get("input_trust_results"):
            it = state["input_trust_results"]
            prods = ", ".join([p["brand_name"] for p in it.get("verified_regulatory_products", [])])
            it_summary += f"Diagnosis: {it['primary_symptom']}. Approved inputs: {prods}. "

        ms_summary = ""
        if state.get("market_sense_results"):
            rec_mandi = state["market_sense_results"]["recommended_mandi"]
            ms_summary += f"Market advisory: Sell at {rec_mandi['market_name']} for net realization ₹{rec_mandi['net_realization_per_quintal']}/qtl. "

        combined_diagnostic = f"{cg_summary} {it_summary} {ms_summary}"

        explanation_req = GeminiExplanationRequest(
            farmer_query=state.get("farmer_query") or "Tomato crop health and selling advisory",
            crop=state.get("crop", "Tomato"),
            diagnostics_summary=combined_diagnostic,
            preferred_language=state.get("preferred_language", "en")
        )

        explanation_res = self.google_ai_provider.explain_advisory_to_farmer(explanation_req)

        return {
            "synthesized_explanation": explanation_res.model_dump(),
            "status": "COMPLETED",
            "execution_trace": trace
        }

    def execute_plan(self, initial_state: KrishivaAgentState) -> KrishivaAgentState:
        """Executes full LangGraph pipeline."""
        logger.info(f"Initiating KRISHIVA LangGraph Orchestrator for {initial_state.get('crop')} in {initial_state.get('district')}")
        result = self.workflow.invoke(initial_state)
        logger.info("KRISHIVA LangGraph workflow completed.")
        return result
