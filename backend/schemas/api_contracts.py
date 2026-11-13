"""
KRISHIVA AI — Core Pydantic Schemas for API Requests & Responses
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


# Health & System Status
class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    database: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Farm & Plot Registration
class FarmCreateRequest(BaseModel):
    farmer_name: str
    phone_number: str
    village: str
    district: str
    state: str = "Telangana"
    latitude: float
    longitude: float
    total_area_acres: float
    crop_name: str = "Tomato"
    variety: Optional[str] = "Saaho 3251"
    crop_stage: str = "flowering"


class FarmResponse(BaseModel):
    farmer_id: str
    farm_id: str
    farmer_name: str
    district: str
    crop_name: str
    variety: str
    created_at: datetime


# Crop Guard Risk Assessment
class CropRiskAssessRequest(BaseModel):
    latitude: float
    longitude: float
    crop: str = "Tomato"
    variety: Optional[str] = "Hybrid"
    crop_stage: str = "flowering"
    district: str = "Rangareddy"


class CropRiskAssessResponse(BaseModel):
    crop: str
    district: str
    observed_weather: Dict[str, Any]
    threat_assessments: List[Dict[str, Any]]
    human_review_required: bool
    assessed_at: datetime = Field(default_factory=datetime.utcnow)


# Market Sense & Net Realization
class MarketCompareRequest(BaseModel):
    latitude: float
    longitude: float
    commodity: str = "Tomato"
    quantity_quintals: float = 50.0
    district: str = "Rangareddy"


class MarketCompareResponse(BaseModel):
    commodity: str
    quantity_quintals: float
    recommended_mandi: Dict[str, Any]
    all_mandis_comparison: List[Dict[str, Any]]
    decision_rationale: str
    advisory_notes: str


# Input Trust Diagnosis & Verification
class InputDiagnoseRequest(BaseModel):
    crop: str = "Tomato"
    symptom_description: str
    symptom_location: str = "leaf"
    crop_stage: str = "flowering"
    has_soil_test: bool = False
    soil_ph: Optional[float] = None


class InputDiagnoseResponse(BaseModel):
    crop: str
    primary_symptom: str
    symptom_location: str
    differential_diagnosis: List[Dict[str, Any]]
    recommended_intervention_category: str
    verified_regulatory_products: List[Dict[str, Any]]
    non_chemical_cultural_controls: List[str]
    missing_critical_data: List[str]
    confidence_level: str
    requires_expert_escalation: bool
    regulatory_disclaimer: str


# Full LangGraph Orchestrated Decision Plan
class DecisionPlanRequest(BaseModel):
    session_id: str = "session-001"
    farmer_id: str = "farmer-001"
    crop: str = "Tomato"
    variety: Optional[str] = "Hybrid Saaho"
    district: str = "Rangareddy"
    latitude: float = 17.3850
    longitude: float = 78.4867
    crop_stage: str = "flowering"
    farmer_query: str = "Yellowing lower foliage with concentric brown spots"
    symptom_location: str = "lower_leaf"
    harvest_quantity_quintals: float = 40.0
    soil_ph: Optional[float] = 6.8
    has_soil_test: bool = True
    preferred_language: str = "en"


class DecisionPlanResponse(BaseModel):
    session_id: str
    status: str
    crop: str
    district: str
    weather_summary: Dict[str, Any]
    crop_guard: List[Dict[str, Any]]
    input_trust: Dict[str, Any]
    market_sense: Dict[str, Any]
    synthesized_explanation: Dict[str, Any]
    human_review_required: bool
    execution_trace: List[str]
