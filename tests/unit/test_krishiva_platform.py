import pytest
from fastapi.testclient import TestClient
from backend.api.v1.routes import app
from backend.intelligence.crop_guard.crop_guard_engine import CropGuardEngine
from backend.intelligence.market_sense.net_realization_optimizer import NetRealizationOptimizer
from backend.intelligence.input_trust.input_trust_engine import InputTrustEngine
from backend.governance.provenance.registry import DataSourceRegistry
from backend.integrations.google_ai.gemma_adapter import GoogleGemmaAdapter, GemmaInferenceRequest
from backend.integrations.google_ai.vertex_ai_service import GoogleVertexAIService, VertexPredictionRequest
from backend.integrations.earth_engine.sentinel_adapter import GoogleEarthEngineAdapter, EarthEngineVegetationRequest
from backend.intelligence.orchestrator.a2a_negotiation import AgentToAgentNegotiator

client = TestClient(app)

def test_health_endpoint():
    res = client.get('/api/v1/health')
    assert res.status_code == 200
    assert res.json()['status'] == 'HEALTHY'

def test_crop_risk_assessment_engine():
    engine = CropGuardEngine()
    results = engine.evaluate_tomato_risks(
        temperature_c=26.0,
        relative_humidity_percent=82.0,
        rainfall_24h_mm=3.0,
        crop_stage='flowering',
        variety='Saaho 3251'
    )
    assert len(results) >= 2
    threat_names = [r.threat for r in results]
    assert any('Early Blight' in t for t in threat_names)
    assert results[0].risk_category in ['medium', 'high', 'severe']

def test_market_sense_net_realization():
    optimizer = NetRealizationOptimizer()
    candidate_mandis = [
        {'market': 'Mandi Near', 'district': 'Rangareddy', 'latitude': 17.40, 'longitude': 78.50, 'modal_price': 2200.0, 'apmc_charge_percent': 1.0},
        {'market': 'Mandi Distant High Price', 'district': 'Hyderabad', 'latitude': 17.50, 'longitude': 78.60, 'modal_price': 2600.0, 'apmc_charge_percent': 1.0}
    ]
    report = optimizer.optimize_markets(
        farmer_lat=17.38,
        farmer_lon=78.48,
        commodity='Tomato',
        quantity_quintals=50.0,
        candidate_mandis=candidate_mandis
    )
    assert report.harvest_quantity_quintals == 50.0
    assert report.recommended_mandi.expected_net_realization > 0
    assert len(report.all_mandis_comparison) == 2

def test_input_trust_differential_diagnosis():
    engine = InputTrustEngine()
    report = engine.diagnose_and_recommend(
        crop='Tomato',
        symptom_description='Yellowing leaves on lower branches with small brown spots',
        symptom_location='lower_leaf'
    )
    assert len(report.differential_diagnosis) >= 2
    assert len(report.verified_regulatory_products) >= 1
    assert report.verified_regulatory_products[0].registration_number is not None

def test_data_source_registry_provenance():
    sources = DataSourceRegistry.list_all_sources()
    assert len(sources) >= 4
    names = [s.source_name for s in sources]
    assert any('Agmarknet' in n for n in names)
    assert any('Open-Meteo' in n for n in names)

def test_api_crop_risk():
    res = client.post('/api/v1/crop-risk/assess', json={
        'latitude': 17.3850,
        'longitude': 78.4867,
        'crop': 'Tomato',
        'variety': 'Saaho 3251',
        'crop_stage': 'flowering',
        'district': 'Rangareddy'
    })
    assert res.status_code == 200
    data = res.json()
    assert 'threat_assessments' in data
    assert len(data['threat_assessments']) > 0

def test_google_gemma_edge_inference():
    gemma = GoogleGemmaAdapter()
    resp = gemma.run_edge_inference(GemmaInferenceRequest(
        crop='Tomato',
        symptom_notes='Target-board concentric rings on foliage',
        temperature_c=25.0,
        humidity_percent=80.0
    ))
    assert resp.offline_edge_ready is True
    assert 'Alternaria solani' in resp.diagnostic_hypothesis
    assert resp.confidence_score > 0.75

def test_google_earth_engine_sentinel():
    gee = GoogleEarthEngineAdapter()
    resp = gee.analyze_crop_vigor(EarthEngineVegetationRequest(
        latitude=17.3850,
        longitude=78.4867
    ))
    assert resp.ndvi_mean > 0.5
    assert 'COPERNICUS/S2_SR_HARMONIZED' in resp.satellite_sensor
    assert resp.provenance_id == 'PROV-GEE-SENTINEL2-006'

def test_agent_to_agent_autonomous_negotiation():
    neg = AgentToAgentNegotiator()
    session = neg.negotiate_harvest_and_treatment(
        crop='Tomato',
        detected_threat='Early Blight',
        threat_level='high',
        selected_chemical_phi_days=7,
        current_mandi_modal_price=2500.0,
        planned_harvest_days_away=2
    )
    assert session.consensus_status == 'REACHED'
    assert len(session.messages) == 3
    assert session.active_consensus['action'] == 'SUBSTITUTE_LOW_PHI_INPUT_OR_DELAY_HARVEST'

def test_end_to_end_decision_plan():
    res = client.post('/api/v1/decisions/plan', json={
        'session_id': 'test-session',
        'farmer_id': 'test-farmer',
        'crop': 'Tomato',
        'district': 'Rangareddy',
        'latitude': 17.3850,
        'longitude': 78.4867,
        'crop_stage': 'flowering',
        'farmer_query': 'Foliage spots and market selling plan',
        'harvest_quantity_quintals': 30.0,
        'has_soil_test': True,
        'preferred_language': 'en'
    })
    assert res.status_code == 200
    data = res.json()
    assert data['status'] == 'COMPLETED'
    assert len(data['crop_guard']) > 0
    assert 'recommended_mandi' in data['market_sense']
    assert len(data['execution_trace']) >= 4
