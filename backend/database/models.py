"""
KRISHIVA AI — Core Database Models
Covers all 26 core architectural entities:
User, Farmer, FPO, Farm, Plot, CropCycle, SoilTest, WeatherObservation,
WeatherForecast, FieldObservation, ImageAssessment, RiskAssessment,
Market, Commodity, MarketPrice, MarketArrival, PriceForecast, HarvestEstimate,
InputProduct, ProductRegistration, AgronomicEvidence, InterventionRecommendation,
SellingRecommendation, DecisionFeedback, ModelVersion, DatasetVersion,
AgentExecution, AuditEvent.
"""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Float, Integer, DateTime, Boolean, ForeignKey, Text, JSON
)
from sqlalchemy.orm import relationship
from backend.database.session import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class TimestampMixin:
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


# 1. User & Authentication
class User(Base, TimestampMixin):
    __tablename__ = "users"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    phone_number = Column(String(20), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(30), default="farmer", nullable=False)  # farmer, fpo_manager, agronomist, admin
    language_preference = Column(String(10), default="te")  # te=Telugu, hi=Hindi, en=English
    is_active = Column(Boolean, default=True)


# 2. FPO
class FPO(Base, TimestampMixin):
    __tablename__ = "fpos"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(150), nullable=False)
    registration_number = Column(String(50), unique=True, nullable=True)
    state = Column(String(50), nullable=False)
    district = Column(String(50), nullable=False)
    mandal_or_block = Column(String(50), nullable=True)
    contact_phone = Column(String(20), nullable=True)


# 3. Farmer
class Farmer(Base, TimestampMixin):
    __tablename__ = "farmers"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    fpo_id = Column(String(36), ForeignKey("fpos.id"), nullable=True)
    name = Column(String(100), nullable=False)
    village = Column(String(100), nullable=False)
    district = Column(String(50), nullable=False)
    state = Column(String(50), nullable=False)
    phone_number = Column(String(20), nullable=False)
    consent_recorded = Column(Boolean, default=True)

    farms = relationship("Farm", back_populates="farmer")


# 4. Farm
class Farm(Base, TimestampMixin):
    __tablename__ = "farms"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    farmer_id = Column(String(36), ForeignKey("farmers.id"), nullable=False)
    name = Column(String(100), default="Primary Farm")
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    total_area_acres = Column(Float, nullable=False)
    soil_type = Column(String(50), nullable=True)
    irrigation_source = Column(String(50), nullable=True)  # Borewell, Canal, Rainfed, Drip

    farmer = relationship("Farmer", back_populates="farms")
    plots = relationship("Plot", back_populates="farm")


# 5. Plot
class Plot(Base, TimestampMixin):
    __tablename__ = "plots"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    farm_id = Column(String(36), ForeignKey("farms.id"), nullable=False)
    plot_name = Column(String(50), default="Plot 1")
    area_acres = Column(Float, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    boundary_geojson = Column(JSON, nullable=True)

    farm = relationship("Farm", back_populates="plots")
    crop_cycles = relationship("CropCycle", back_populates="plot")


# 6. CropCycle
class CropCycle(Base, TimestampMixin):
    __tablename__ = "crop_cycles"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    plot_id = Column(String(36), ForeignKey("plots.id"), nullable=False)
    crop_name = Column(String(50), nullable=False)  # e.g. Tomato
    variety = Column(String(50), nullable=True)     # e.g. Saaho 3251
    season = Column(String(20), nullable=False)     # Kharif, Rabi, Zaid
    sowing_date = Column(DateTime, nullable=False)
    current_stage = Column(String(50), default="vegetative") # vegetative, flowering, fruiting, harvesting
    expected_harvest_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

    plot = relationship("Plot", back_populates="crop_cycles")


# 7. SoilTest
class SoilTest(Base, TimestampMixin):
    __tablename__ = "soil_tests"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    plot_id = Column(String(36), ForeignKey("plots.id"), nullable=False)
    sample_date = Column(DateTime, nullable=False)
    laboratory = Column(String(100), nullable=True)
    ph = Column(Float, nullable=False)
    ec_ds_m = Column(Float, nullable=True)
    organic_carbon_percent = Column(Float, nullable=True)
    nitrogen_kg_ha = Column(Float, nullable=True)
    phosphorus_kg_ha = Column(Float, nullable=True)
    potassium_kg_ha = Column(Float, nullable=True)
    zinc_ppm = Column(Float, nullable=True)
    iron_ppm = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)


# 8. WeatherObservation
class WeatherObservation(Base, TimestampMixin):
    __tablename__ = "weather_observations"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    observation_time = Column(DateTime, nullable=False, index=True)
    temperature_c = Column(Float, nullable=False)
    relative_humidity_percent = Column(Float, nullable=False)
    precipitation_mm = Column(Float, default=0.0)
    wind_speed_kmh = Column(Float, nullable=True)
    solar_radiation_w_m2 = Column(Float, nullable=True)
    provider = Column(String(50), default="open-meteo")


# 9. WeatherForecast
class WeatherForecast(Base, TimestampMixin):
    __tablename__ = "weather_forecasts"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    forecast_generated_time = Column(DateTime, nullable=False)
    forecast_target_time = Column(DateTime, nullable=False, index=True)
    temp_min_c = Column(Float, nullable=False)
    temp_max_c = Column(Float, nullable=False)
    avg_humidity_percent = Column(Float, nullable=False)
    precipitation_prob_percent = Column(Float, nullable=True)
    expected_rainfall_mm = Column(Float, default=0.0)
    provider = Column(String(50), default="open-meteo")


# 10. FieldObservation
class FieldObservation(Base, TimestampMixin):
    __tablename__ = "field_observations"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    crop_cycle_id = Column(String(36), ForeignKey("crop_cycles.id"), nullable=False)
    observation_date = Column(DateTime, default=datetime.utcnow)
    observed_symptoms = Column(Text, nullable=False)
    symptom_location = Column(String(50), nullable=True)  # leaf, stem, fruit, root
    severity = Column(String(20), default="moderate")     # mild, moderate, severe
    farmer_notes = Column(Text, nullable=True)


# 11. ImageAssessment
class ImageAssessment(Base, TimestampMixin):
    __tablename__ = "image_assessments"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    field_observation_id = Column(String(36), ForeignKey("field_observations.id"), nullable=True)
    image_uri = Column(String(255), nullable=False)
    assessed_by = Column(String(50), default="gemini-vision")
    visual_features_detected = Column(JSON, nullable=True)
    candidate_conditions = Column(JSON, nullable=True)
    quality_score = Column(Float, default=1.0)
    is_field_condition = Column(Boolean, default=True)


# 12. RiskAssessment (Crop Guard Core Output)
class RiskAssessment(Base, TimestampMixin):
    __tablename__ = "risk_assessments"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    crop_cycle_id = Column(String(36), ForeignKey("crop_cycles.id"), nullable=True)
    threat_name = Column(String(100), nullable=False)  # Early Blight, Late Blight, Whitefly
    threat_type = Column(String(30), nullable=False)  # fungal, bacterial, viral, pest, physiological
    risk_category = Column(String(20), nullable=False) # low, medium, high, severe
    calibrated_probability = Column(Float, nullable=True)
    model_or_rule_identifier = Column(String(100), nullable=False)
    evidence_payload = Column(JSON, nullable=False)
    data_timestamps = Column(JSON, nullable=False)
    uncertainty_score = Column(Float, nullable=True)
    recommended_monitoring = Column(Text, nullable=False)
    limitations = Column(Text, nullable=False)
    human_review_required = Column(Boolean, default=False)


# 13. Market (APMC Mandis)
class Market(Base, TimestampMixin):
    __tablename__ = "markets"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    market_name = Column(String(100), nullable=False, index=True)
    district = Column(String(50), nullable=False, index=True)
    state = Column(String(50), nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    is_enam_enabled = Column(Boolean, default=False)
    apmc_charge_percent = Column(Float, default=1.5)  # APMC mandi fee


# 14. Commodity
class Commodity(Base, TimestampMixin):
    __tablename__ = "commodities"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(50), unique=True, nullable=False)
    category = Column(String(30), default="vegetable")
    standard_unit = Column(String(20), default="quintal") # 100 kg


# 15. MarketPrice
class MarketPrice(Base, TimestampMixin):
    __tablename__ = "market_prices"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    market_id = Column(String(36), ForeignKey("markets.id"), nullable=False)
    commodity_id = Column(String(36), ForeignKey("commodities.id"), nullable=False)
    variety = Column(String(50), default="Standard")
    arrival_date = Column(DateTime, nullable=False, index=True)
    min_price_inr_qtl = Column(Float, nullable=False)
    max_price_inr_qtl = Column(Float, nullable=False)
    modal_price_inr_qtl = Column(Float, nullable=False)
    data_source = Column(String(50), default="agmarknet")
    retrieval_timestamp = Column(DateTime, default=datetime.utcnow)


# 16. MarketArrival
class MarketArrival(Base, TimestampMixin):
    __tablename__ = "market_arrivals"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    market_id = Column(String(36), ForeignKey("markets.id"), nullable=False)
    commodity_id = Column(String(36), ForeignKey("commodities.id"), nullable=False)
    arrival_date = Column(DateTime, nullable=False, index=True)
    arrivals_tonnes = Column(Float, nullable=False)
    traded_tonnes = Column(Float, nullable=True)
    source = Column(String(50), default="agmarknet")


# 17. PriceForecast
class PriceForecast(Base, TimestampMixin):
    __tablename__ = "price_forecasts"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    market_id = Column(String(36), ForeignKey("markets.id"), nullable=False)
    commodity_id = Column(String(36), ForeignKey("commodities.id"), nullable=False)
    forecast_date = Column(DateTime, nullable=False, index=True)
    predicted_modal_price = Column(Float, nullable=False)
    lower_bound_price = Column(Float, nullable=False)
    upper_bound_price = Column(Float, nullable=False)
    model_version = Column(String(50), nullable=False)
    evaluation_metrics = Column(JSON, nullable=True)


# 18. HarvestEstimate
class HarvestEstimate(Base, TimestampMixin):
    __tablename__ = "harvest_estimates"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    crop_cycle_id = Column(String(36), ForeignKey("crop_cycles.id"), nullable=False)
    estimated_harvest_date = Column(DateTime, nullable=False)
    estimated_quantity_quintals = Column(Float, nullable=False)
    quality_grade = Column(String(10), default="Grade A")
    confidence_interval = Column(JSON, nullable=True)


# 19. InputProduct
class InputProduct(Base, TimestampMixin):
    __tablename__ = "input_products"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    brand_name = Column(String(100), nullable=False)
    manufacturer = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)  # fungicide, insecticide, biofertilizer, chemical_fertilizer
    active_ingredient = Column(String(150), nullable=False)
    formulation = Column(String(50), nullable=False) # e.g. 75% WP, 250 EC
    nutrient_composition = Column(JSON, nullable=True) # e.g. {"N": 19, "P": 19, "K": 19}
    standard_pack_size = Column(String(50), nullable=True)
    mrp_inr = Column(Float, nullable=True)


# 20. ProductRegistration (CIB&RC / FCO Compliance)
class ProductRegistration(Base, TimestampMixin):
    __tablename__ = "product_registrations"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    product_id = Column(String(36), ForeignKey("input_products.id"), nullable=False)
    registration_authority = Column(String(50), default="CIB&RC") # CIB&RC or FCO
    registration_number = Column(String(100), nullable=False)
    approved_crop = Column(String(50), nullable=False) # e.g. Tomato
    approved_target_pest = Column(String(100), nullable=False) # e.g. Early Blight
    label_dosage_per_acre = Column(String(50), nullable=False) # e.g. 600-800 gm in 200L water
    waiting_period_days = Column(Integer, nullable=False) # Pre-harvest interval (PHI)
    safety_restrictions = Column(Text, nullable=True)
    source_document = Column(String(200), nullable=False)
    verified_date = Column(DateTime, nullable=False)


# 21. AgronomicEvidence
class AgronomicEvidence(Base, TimestampMixin):
    __tablename__ = "agronomic_evidence"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    crop = Column(String(50), nullable=False)
    condition_or_threat = Column(String(100), nullable=False)
    evidence_source = Column(String(150), nullable=False) # e.g. ICAR-IIHR, PJTSAU
    scientific_rationale = Column(Text, nullable=False)
    recommended_cultural_practices = Column(Text, nullable=True)
    biological_controls = Column(Text, nullable=True)


# 22. InterventionRecommendation
class InterventionRecommendation(Base, TimestampMixin):
    __tablename__ = "intervention_recommendations"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    risk_assessment_id = Column(String(36), ForeignKey("risk_assessments.id"), nullable=True)
    farmer_query_summary = Column(Text, nullable=False)
    differential_diagnosis = Column(JSON, nullable=False)
    recommended_category = Column(String(50), nullable=False) # bio-control, cultural, chemical, nutrition
    verified_product_options = Column(JSON, nullable=False)
    application_instructions = Column(Text, nullable=False)
    pre_harvest_interval_days = Column(Integer, nullable=False)
    safety_cautions = Column(Text, nullable=False)
    requires_expert_escalation = Column(Boolean, default=False)


# 23. SellingRecommendation (Market Sense Core Output)
class SellingRecommendation(Base, TimestampMixin):
    __tablename__ = "selling_recommendations"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    crop_cycle_id = Column(String(36), ForeignKey("crop_cycles.id"), nullable=True)
    market_id = Column(String(36), ForeignKey("markets.id"), nullable=False)
    quantity_quintals = Column(Float, nullable=False)
    expected_modal_price = Column(Float, nullable=False)
    expected_gross_revenue = Column(Float, nullable=False)
    transport_cost = Column(Float, nullable=False)
    handling_cost = Column(Float, nullable=False)
    mandi_fees = Column(Float, nullable=False)
    estimated_transit_loss = Column(Float, nullable=False)
    expected_net_realization = Column(Float, nullable=False)
    net_realization_per_quintal = Column(Float, nullable=False)
    distance_km = Column(Float, nullable=False)
    confidence_level = Column(String(20), default="high")
    recommendation_reason = Column(Text, nullable=False)


# 24. DecisionFeedback
class DecisionFeedback(Base, TimestampMixin):
    __tablename__ = "decision_feedback"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    decision_type = Column(String(50), nullable=False) # crop_guard, market_sense, input_trust
    recommendation_id = Column(String(36), nullable=False)
    action_taken = Column(String(100), nullable=False) # followed, modified, rejected
    farmer_reported_outcome = Column(Text, nullable=True)
    actual_realized_price = Column(Float, nullable=True)
    actual_pest_control_rating = Column(Integer, nullable=True) # 1 to 5


# 25. ModelVersion & DatasetVersion
class ModelVersion(Base, TimestampMixin):
    __tablename__ = "model_versions"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    model_name = Column(String(100), nullable=False)
    version = Column(String(30), nullable=False)
    task_type = Column(String(50), nullable=False) # price_forecast, disease_risk_rule
    metrics = Column(JSON, nullable=False)
    training_data_provenance = Column(String(200), nullable=False)
    model_artifact_path = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)


class DatasetVersion(Base, TimestampMixin):
    __tablename__ = "dataset_versions"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    dataset_name = Column(String(100), nullable=False)
    provider = Column(String(100), nullable=False)
    records_count = Column(Integer, nullable=False)
    geographic_coverage = Column(String(100), nullable=False)
    collection_timestamp = Column(DateTime, default=datetime.utcnow)
    data_hash = Column(String(64), nullable=False)


# 26. AgentExecution & AuditEvent
class AgentExecution(Base, TimestampMixin):
    __tablename__ = "agent_executions"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    subgraph_name = Column(String(50), nullable=False) # crop_guard, market_sense, input_trust, supervisor
    agent_name = Column(String(50), nullable=False)
    input_payload = Column(JSON, nullable=False)
    output_payload = Column(JSON, nullable=True)
    status = Column(String(20), default="success") # success, failed, degraded
    latency_ms = Column(Float, nullable=True)
    error_message = Column(Text, nullable=True)


class AuditEvent(Base, TimestampMixin):
    __tablename__ = "audit_events"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    event_type = Column(String(50), nullable=False) # RECOMMENDATION_GENERATED, DATA_INGESTION, SENSITIVE_QUERY
    entity_type = Column(String(50), nullable=True)
    entity_id = Column(String(36), nullable=True)
    payload = Column(JSON, nullable=False)
    operator = Column(String(100), default="system")
