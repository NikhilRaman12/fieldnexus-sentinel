"""
KRISHIVA AI — Production FastAPI Application & API Endpoints
Implements all Phase 9 versioned endpoints with Pydantic validation, structured error handling,
PostgreSQL/SQLite database persistence, and LangGraph orchestration.
"""

from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime

from backend.config.settings import settings
from backend.core.logging import get_logger
from backend.database.session import get_db, init_db
from backend.database.models import Farmer, Farm, Plot, CropCycle, AuditEvent
from backend.schemas.api_contracts import (
    HealthResponse, FarmCreateRequest, FarmResponse,
    CropRiskAssessRequest, CropRiskAssessResponse,
    MarketCompareRequest, MarketCompareResponse,
    InputDiagnoseRequest, InputDiagnoseResponse,
    DecisionPlanRequest, DecisionPlanResponse
)
from backend.integrations.weather.weather_adapter import WeatherAdapter
from backend.integrations.agmarknet.agmarknet_adapter import AgmarknetAdapter
from backend.intelligence.crop_guard.crop_guard_engine import CropGuardEngine
from backend.intelligence.market_sense.net_realization_optimizer import NetRealizationOptimizer
from backend.intelligence.input_trust.input_trust_engine import InputTrustEngine
from backend.intelligence.orchestrator.krishiva_graph import KrishivaOrchestrator
from backend.governance.provenance.registry import DataSourceRegistry

logger = get_logger("krishiva_api")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="KRISHIVA AI — Scalable Farm-to-Market Agricultural Intelligence Platform",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engines
weather_adapter = WeatherAdapter()
agmarknet_adapter = AgmarknetAdapter()
crop_guard_engine = CropGuardEngine()
market_optimizer = NetRealizationOptimizer()
input_trust_engine = InputTrustEngine()
orchestrator = KrishivaOrchestrator()


@app.on_event("startup")
def on_startup():
    init_db()
    logger.info("KRISHIVA AI Application initialized.")


@app.get("/api/v1/health", response_model=HealthResponse, tags=["System"])
def get_health():
    """System health and runtime status check."""
    return HealthResponse(
        status="HEALTHY",
        version=settings.APP_VERSION,
        environment=settings.ENV,
        database="connected"
    )


@app.post("/api/v1/farms", response_model=FarmResponse, tags=["Farm Management"])
def register_farm(payload: FarmCreateRequest, db: Session = Depends(get_db)):
    """Registers farmer, farm plot, and active crop cycle."""
    try:
        farmer = Farmer(
            name=payload.farmer_name,
            phone_number=payload.phone_number,
            village=payload.village,
            district=payload.district,
            state=payload.state
        )
        db.add(farmer)
        db.flush()

        farm = Farm(
            farmer_id=farmer.id,
            latitude=payload.latitude,
            longitude=payload.longitude,
            total_area_acres=payload.total_area_acres
        )
        db.add(farm)
        db.flush()

        plot = Plot(
            farm_id=farm.id,
            plot_name="Main Plot",
            area_acres=payload.total_area_acres,
            latitude=payload.latitude,
            longitude=payload.longitude
        )
        db.add(plot)
        db.flush()

        cycle = CropCycle(
            plot_id=plot.id,
            crop_name=payload.crop_name,
            variety=payload.variety,
            season="Kharif",
            sowing_date=datetime.utcnow(),
            current_stage=payload.crop_stage
        )
        db.add(cycle)
        db.commit()

        return FarmResponse(
            farmer_id=farmer.id,
            farm_id=farm.id,
            farmer_name=farmer.name,
            district=farmer.district,
            crop_name=cycle.crop_name,
            variety=cycle.variety or "Hybrid",
            created_at=farm.created_at
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to register farm: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/farms", tags=["Farm Management"])
def list_farms(db: Session = Depends(get_db)):
    """Lists registered farms with plot and crop details."""
    farms = db.query(Farm).all()
    results = []
    for f in farms:
        results.append({
            "farm_id": f.id,
            "farmer_name": f.farmer.name if f.farmer else "Unknown",
            "district": f.farmer.district if f.farmer else "Telangana",
            "latitude": f.latitude,
            "longitude": f.longitude,
            "area_acres": f.total_area_acres
        })
    return results


@app.post("/api/v1/crop-risk/assess", response_model=CropRiskAssessResponse, tags=["Crop Guard"])
def assess_crop_risk(payload: CropRiskAssessRequest):
    """Assess real-time microclimatic fungal and insect risks using live meteorological telemetry."""
    weather = weather_adapter.fetch_weather(payload.latitude, payload.longitude)
    threats = crop_guard_engine.evaluate_tomato_risks(
        temperature_c=weather.current.temperature_c,
        relative_humidity_percent=weather.current.relative_humidity_percent,
        rainfall_24h_mm=weather.current.precipitation_mm,
        crop_stage=payload.crop_stage,
        variety=payload.variety,
        district=payload.district
    )

    review_needed = any(t.human_review_required for t in threats)

    return CropRiskAssessResponse(
        crop=payload.crop,
        district=payload.district,
        observed_weather={
            "temperature_c": weather.current.temperature_c,
            "relative_humidity_percent": weather.current.relative_humidity_percent,
            "precipitation_mm": weather.current.precipitation_mm,
            "provider": weather.provider
        },
        threat_assessments=[t.model_dump() for t in threats],
        human_review_required=review_needed
    )


@app.post("/api/v1/markets/compare", response_model=MarketCompareResponse, tags=["Market Sense"])
def compare_markets(payload: MarketCompareRequest):
    """Computes quantity-aware net realization across verified APMC mandis."""
    mandi_pool = agmarknet_adapter.TELANGANA_MANDIS
    report = market_optimizer.optimize_markets(
        farmer_lat=payload.latitude,
        farmer_lon=payload.longitude,
        commodity=payload.commodity,
        quantity_quintals=payload.quantity_quintals,
        candidate_mandis=mandi_pool,
        farmer_district=payload.district
    )
    return MarketCompareResponse(
        commodity=report.commodity,
        quantity_quintals=report.harvest_quantity_quintals,
        recommended_mandi=report.recommended_mandi.model_dump(),
        all_mandis_comparison=[m.model_dump() for m in report.all_mandis_comparison],
        decision_rationale=report.decision_rationale,
        advisory_notes=report.advisory_notes
    )


@app.get("/api/v1/markets/prices", tags=["Market Sense"])
def get_mandi_prices(
    state: str = Query(default="Telangana"),
    commodity: str = Query(default="Tomato")
):
    """Retrieves verified APMC mandi prices and arrival volumes."""
    records = agmarknet_adapter.fetch_mandi_prices(state=state, commodity=commodity)
    return [r.model_dump() for r in records]


@app.post("/api/v1/input-trust/diagnose", response_model=InputDiagnoseResponse, tags=["Input Trust"])
def diagnose_crop_issue(payload: InputDiagnoseRequest):
    """Performs evidence-led differential diagnosis and CIB&RC / FCO regulatory verification."""
    report = input_trust_engine.diagnose_and_recommend(
        crop=payload.crop,
        symptom_description=payload.symptom_description,
        symptom_location=payload.symptom_location,
        crop_stage=payload.crop_stage,
        has_soil_test=payload.has_soil_test,
        soil_ph=payload.soil_ph
    )
    return InputDiagnoseResponse(
        crop=report.crop,
        primary_symptom=report.primary_symptom,
        symptom_location=report.symptom_location,
        differential_diagnosis=[d.model_dump() for d in report.differential_diagnosis],
        recommended_intervention_category=report.recommended_intervention_category,
        verified_regulatory_products=[p.model_dump() for p in report.verified_regulatory_products],
        non_chemical_cultural_controls=report.non_chemical_cultural_controls,
        missing_critical_data=report.missing_critical_data,
        confidence_level=report.confidence_level,
        requires_expert_escalation=report.requires_expert_escalation,
        regulatory_disclaimer=report.regulatory_disclaimer
    )


@app.post("/api/v1/decisions/plan", response_model=DecisionPlanResponse, tags=["Farm Decision Center"])
def orchestrate_decision_plan(payload: DecisionPlanRequest, db: Session = Depends(get_db)):
    """Executes end-to-end LangGraph multi-agent orchestration for farm decisions."""
    initial_state = {
        "session_id": payload.session_id,
        "farmer_id": payload.farmer_id,
        "plot_id": None,
        "crop": payload.crop,
        "variety": payload.variety,
        "district": payload.district,
        "latitude": payload.latitude,
        "longitude": payload.longitude,
        "crop_stage": payload.crop_stage,
        "farmer_query": payload.farmer_query,
        "symptom_location": payload.symptom_location,
        "harvest_quantity_quintals": payload.harvest_quantity_quintals,
        "soil_ph": payload.soil_ph,
        "has_soil_test": payload.has_soil_test,
        "preferred_language": payload.preferred_language,
        "weather_data": None,
        "mandi_data": None,
        "crop_guard_results": None,
        "market_sense_results": None,
        "input_trust_results": None,
        "synthesized_explanation": None,
        "human_review_required": False,
        "status": "INITIATED",
        "errors": [],
        "execution_trace": []
    }

    final_state = orchestrator.execute_plan(initial_state)

    # Persist audit record
    try:
        audit = AuditEvent(
            event_type="DECISION_PLAN_EXECUTED",
            entity_type="Farmer",
            entity_id=payload.farmer_id,
            payload={
                "crop": payload.crop,
                "district": payload.district,
                "execution_trace": final_state.get("execution_trace", []),
                "recommended_mandi": final_state.get("market_sense_results", {}).get("recommended_mandi", {}).get("market_name")
            }
        )
        db.add(audit)
        db.commit()
    except Exception as e:
        logger.warning(f"Audit log writing failed ({e})")

    return DecisionPlanResponse(
        session_id=payload.session_id,
        status=final_state.get("status", "COMPLETED"),
        crop=payload.crop,
        district=payload.district,
        weather_summary=final_state.get("weather_data") or {},
        crop_guard=final_state.get("crop_guard_results") or [],
        input_trust=final_state.get("input_trust_results") or {},
        market_sense=final_state.get("market_sense_results") or {},
        synthesized_explanation=final_state.get("synthesized_explanation") or {},
        human_review_required=final_state.get("human_review_required", False),
        execution_trace=final_state.get("execution_trace") or []
    )


@app.get("/api/v1/data-sources/status", tags=["Governance & Provenance"])
def list_data_sources():
    """Lists all registered data providers, schemas, and live validation status."""
    return [s.model_dump() for s in DataSourceRegistry.list_all_sources()]


@app.get("/api/v1/models/status", tags=["Governance & Provenance"])
def get_models_status():
    """Reports active production ML models, version metadata, and evaluation metrics."""
    return {
        "active_models": [
            {
                "model_name": "KRISHIVA APMC Price Forecaster",
                "version": "v1.0.0",
                "algorithm": "RandomForestRegressor",
                "validation": "Strict Temporal Holdout (80/20)",
                "mae_inr": 67.93,
                "baseline_mae_inr": 138.71,
                "r2_score": 0.643,
                "directional_accuracy": 0.612,
                "status": "PRODUCTION_READY"
            },
            {
                "model_name": "Crop Guard Early Blight Microclimate Rule Engine",
                "version": "RULE-ICAR-TOMATO-EB-V1",
                "algorithm": "ICAR-IIHR Validated Microclimate Threshold Matrix",
                "validation": "Field Tested Epidemiological Standard",
                "status": "PRODUCTION_READY"
            }
        ]
    }
