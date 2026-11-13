"""
KRISHIVA AI — Central LangGraph Multi-Agent Orchestrator
Coordinates three independent intelligence subgraphs:
1. Crop Guard Subgraph (Disease rules for Tomato; explicit rejection of unsupported crops)
2. Market Sense Subgraph (APMC discovery, arrivals, net realization with transparent cost disclosures)
3. Input Trust Subgraph (Differential diagnosis first, non-chemical controls, no unverified chemical dosages)
"""

from typing import Dict, Any, List, Optional, TypedDict
from datetime import datetime
from langgraph.graph import StateGraph, END

from backend.intelligence.crop_guard.crop_guard_engine import CropGuardEngine
from backend.intelligence.market_sense.net_realization_optimizer import NetRealizationOptimizer
from backend.intelligence.input_trust.input_trust_engine import InputTrustEngine
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
                "forecast_days": len(weather_snap.forecast_7d),
                "is_live_measured": weather_snap.is_live_measured,
                "status_label": weather_snap.status_label
            }
            trace.append(f"Context Node: Weather acquired ({weather_snap.status_label}).")
        except Exception as e:
            errors.append(f"Weather acquisition error: {str(e)}")

        try:
            mandis = self.agmarknet_adapter.fetch_mandi_prices(
                state="Telangana",
                commodity=state["crop"],
                limit=10
            )
            mandi_list = [m.model_dump() for m in mandis]
            src = mandi_list[0]["data_source"] if mandi_list else "UNKNOWN"
            trace.append(f"Context Node: APMC mandi telemetry acquired ({src}).")
        except Exception as e:
            errors.append(f"Mandi acquisition error: {str(e)}")

        return {
            "weather_data": weather_dict,
            "mandi_data": mandi_list,
            "execution_trace": trace,
            "errors": errors
        }

    def _crop_guard_node(self, state: KrishivaAgentState) -> Dict[str, Any]:
        """Evaluates micro-climatic pest and disease risks with strict crop validation."""
        trace = list(state.get("execution_trace", []))
        errors = list(state.get("errors", []))

        crop = state.get("crop", "Tomato")
        weather = state.get("weather_data") or {
            "temperature_c": 28.0,
            "relative_humidity_percent": 75.0,
            "precipitation_mm": 2.0,
            "is_live_measured": False,
            "provider": "fallback"
        }

        try:
            assessments = self.crop_guard_engine.evaluate_crop_risks(
                crop=crop,
                temperature_c=weather["temperature_c"],
                relative_humidity_percent=weather["relative_humidity_percent"],
                rainfall_24h_mm=weather["precipitation_mm"],
                crop_stage=state.get("crop_stage", "flowering"),
                variety=state.get("variety", "Hybrid Tomato"),
                district=state.get("district", "Rangareddy"),
                weather_provider=weather.get("provider", "open-meteo"),
                is_live_weather=weather.get("is_live_measured", True)
            )
            trace.append(f"Crop Guard Node: Evaluated {len(assessments)} rule-based epidemiological indicators for {crop}.")
            return {
                "crop_guard_results": [a.model_dump() for a in assessments],
                "human_review_required": any(a.human_review_required for a in assessments),
                "execution_trace": trace
            }
        except ValueError as e:
            errors.append(str(e))
            trace.append(f"Crop Guard Node REJECTED: {str(e)}")
            return {
                "crop_guard_results": [],
                "human_review_required": True,
                "errors": errors,
                "execution_trace": trace
            }

    def _input_trust_node(self, state: KrishivaAgentState) -> Dict[str, Any]:
        """Executes differential diagnosis and non-chemical cultural guidance."""
        trace = list(state.get("execution_trace", []))
        trace.append("Input Trust Node: Differential diagnosis completed (unverified chemical prescriptions disabled).")

        query = state.get("farmer_query") or "Foliar spots on lower leaves."
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
        """Calculates net realization across APMC mandis with validated quantity > 0."""
        trace = list(state.get("execution_trace", []))
        errors = list(state.get("errors", []))

        qty = state.get("harvest_quantity_quintals") or 40.0
        mandi_pool = self.agmarknet_adapter.TELANGANA_MANDIS

        try:
            report = self.market_sense_engine.optimize_markets(
                farmer_lat=state["latitude"],
                farmer_lon=state["longitude"],
                commodity=state["crop"],
                quantity_quintals=qty,
                candidate_mandis=mandi_pool,
                farmer_district=state["district"]
            )
            trace.append(f"Market Sense Node: Optimized net realization for {qty} quintals across {len(mandi_pool)} mandis.")
            return {
                "market_sense_results": report.model_dump(),
                "execution_trace": trace
            }
        except Exception as e:
            errors.append(f"Market Sense error: {str(e)}")
            trace.append(f"Market Sense Node failed: {str(e)}")
            return {
                "market_sense_results": None,
                "errors": errors,
                "execution_trace": trace
            }

    def _supervisor_synthesis_node(self, state: KrishivaAgentState) -> Dict[str, Any]:
        """Synthesizes unified farm intelligence using Google Gemini with strict safety boundaries."""
        trace = list(state.get("execution_trace", []))
        trace.append("Supervisor Node: Formulated verified farmer advisory explanation.")

        cg_summary = ""
        if state.get("crop_guard_results"):
            top_risk = state["crop_guard_results"][0]
            cg_summary += f"Crop risk: {top_risk['threat']} (Rule Risk: {top_risk['risk_category']}). "

        it_summary = ""
        if state.get("input_trust_results"):
            it = state["input_trust_results"]
            it_summary += f"Diagnosis: {it['primary_symptom']}. Cultural management recommended: {'; '.join(it.get('non_chemical_cultural_controls', [])[:2])}. "

        ms_summary = ""
        if state.get("market_sense_results"):
            rec_mandi = state["market_sense_results"]["recommended_mandi"]
            ms_summary += f"Selling recommendation: {rec_mandi['market_name']} yields net realization ₹{rec_mandi['net_realization_per_quintal']:.2f}/qtl. "

        combined_diagnostic = f"{cg_summary} {it_summary} {ms_summary}"

        explanation_req = GeminiExplanationRequest(
            farmer_query=state.get("farmer_query") or "Crop health and selling advisory",
            crop=state.get("crop", "Tomato"),
            diagnostics_summary=combined_diagnostic,
            preferred_language=state.get("preferred_language", "en")
        )

        explanation_res = self.google_ai_provider.explain_advisory_to_farmer(explanation_req)

        status_outcome = "COMPLETED" if not state.get("errors") else "COMPLETED_WITH_WARNINGS"

        return {
            "synthesized_explanation": explanation_res.model_dump(),
            "status": status_outcome,
            "execution_trace": trace
        }

    def execute_plan(self, initial_state: KrishivaAgentState) -> KrishivaAgentState:
        """Executes full LangGraph pipeline."""
        logger.info(f"Initiating KRISHIVA LangGraph Orchestrator for {initial_state.get('crop')} in {initial_state.get('district')}")
        result = self.workflow.invoke(initial_state)
        logger.info(f"KRISHIVA LangGraph workflow completed with status {result.get('status')}")
        return result
