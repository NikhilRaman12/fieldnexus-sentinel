# KRISHIVA AI — Farm-to-Market Agricultural Decision Intelligence

> **Buildathon Prototype Edition**  
> **Core Philosophy:** Protect the Crop. Trust the Input. Sell Smarter.  
> **Pilot Region:** Telangana (Tomato Focus)

KRISHIVA AI is an evidence-led agricultural decision intelligence platform designed for Indian farmers, Farmer Producer Organizations (FPOs), and agronomists. It bridges field pathology, statutory regulatory compliance, and market logistics through a LangGraph multi-agent architecture and Google Gemini reasoning.

---

## 🌟 Architecture & Core Systems

```mermaid
graph TD
    A[KRISHIVA Supervisor LangGraph] --> B[🛡️ Crop Guard Subgraph (Tomato)]
    A --> C[🔬 Input Trust Subgraph]
    A --> D[📈 Market Sense Subgraph]
    
    B --> B1[Open-Meteo Weather Telemetry]
    B --> B2[ICAR-IIHR Epidemiological Rules]
    
    C --> C1[Crop-Aware Differential Diagnosis]
    C --> C2[Non-Chemical Cultural Practices & Agronomist Escalation]
    
    D --> D1[AGMARKNET / data.gov.in (Demo / Live Adapter)]
    D --> D2[Net Realization Freight & Perishability Matrix]
    
    B & C & D --> E[Google AI Gemini Multilingual Synthesizer]
    E --> F[Transparent Farmer Action Plan]
```

### 1. Crop Guard (Crop & Disease Intelligence)
- **Scope:** Restricted specifically to Tomato in Telangana. Non-tomato crops (e.g., Chilli, Cotton) are explicitly rejected with validation errors to prevent silent application of invalid pathology rules.
- **Rule-Based Categories:** Reports transparent epidemiological risk categories (`low`, `medium`, `high`, `severe`) derived from ICAR-IIHR protocols. Does not assign fabricated ML probabilities.
- **Weather Telemetry:** Ingests Open-Meteo observations and clearly indicates whether live measured weather or calibrated regional fallback was used.

### 2. Market Sense (Mandi Discovery & Net Realization Optimization)
- **Net Realization Formula:**
  $$\text{Net Realization} = \text{Gross Revenue} - (\text{Freight} + \text{Handling Hamali} + \text{Mandi Fees} + \text{Transit Quality Loss})$$
- **Transparent Cost Disclosures:** Every transport expense, truck count, handling fee, and perishability deduction is explicitly broken down and exposed.
- **Data Provenance:** Clearly distinguishes live API observations from historical simulated reference benchmarks (`DEMO_SIMULATED`). Requires quantity > 0.

### 3. Input Trust (Safety-First Diagnostic Intelligence)
- **Differential Diagnosis First:** Identifies potential competing causes (e.g. Nitrogen translocation deficiency vs Iron chlorosis vs root asphyxiation) rather than diagnosing on leaf yellowing alone.
- **Zero Unverified Chemical Prescriptions:** Unverified chemical pesticides and dosages are strictly disabled. Provides non-chemical sanitary practices (roguing, drip irrigation, airflow spacing) and mandatory agronomist escalation.

---

## ⚖️ Honest ML & System Status

| Component | Architecture / Model | Operational Status | Production Ready Claim | Limitations / Notes |
| :--- | :--- | :--- | :--- | :--- |
| **APMC Price Forecaster** | Random Forest Regressor | `SIMULATION_ONLY` | **NO** | Trained on synthetic seasonal time-series for demo illustration; cannot guarantee market prices. |
| **Tomato Disease Risk** | ICAR Microclimate Threshold Matrix | `RULE_BASED_OPERATIONAL` | **NO (Prototype)** | Evaluates canopy favorability; physical field scout confirmation required. |
| **Crop Disease Computer Vision** | EfficientNet / MobileNet | `NOT_TRAINED` | **NO** | No field-validated weights deployed in this buildathon phase. Zero fabricated weights. |
| **Mandi Price Ingestion** | data.gov.in / AGMARKNET Adapter | `DEMO_SIMULATED` (Fallback) | **NO** | Operates in simulated mode unless official government API key is supplied. |

---

## 🔒 Security & Data Protection
- **No Tracked Credentials:** Active `.env` file removed from source control; `.gitignore` strictly enforced.
- **CORS Restricted:** Restricted to local frontend origins (`http://localhost:3000`, `http://127.0.0.1:3000`).
- **Data Masking:** Public farm listings mask farmer names (`N***`) and omit phone numbers.
- **Explicit Consent:** Farmer registration enforces explicit consent recording.

---

## 🚀 Exact Local Run Instructions

### 1. Requirements
- Python 3.11+
- Node.js 18+ and npm

### 2. Backend Startup (FastAPI + LangGraph)
```powershell
# In project root
cp .env.example .env

# Run database table initialization
python -c "import sys; sys.path.insert(0, '.'); from backend.database.session import init_db; init_db()"

# Execute all 10 automated unit & integration tests
python -m pytest tests/unit/test_krishiva_platform.py -v

# Start FastAPI server
uvicorn backend.api.v1.routes:app --host 0.0.0.0 --port 8000 --reload
```
API docs available at: `http://localhost:8000/docs`

### 3. Frontend Startup (React 18 + TypeScript + Vite)
```powershell
cd frontend
npm install
npm run build
npm run dev
```
Access the application at: `http://localhost:3000`

---

## 🗺️ Buildathon Technical Differentiation & Roadmap

- **Differentiation:** Unlike chatbots that fabricate chemical dosages or uncalibrated probabilities, KRISHIVA AI enforces safety boundaries, differential diagnosis, transparent logistics cost arithmetic, and honest data provenance.
- **Roadmap:**
  - Onboard verified CIB&RC statutory gazette database and FCO standard tables.
  - Implement real-time e-NAM electronic trade integration via authenticated gateway.
  - Pilot mobile field scout app with Google Gemma on-device offline edge intelligence.
