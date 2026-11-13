feature/kaggriculture-agent
# KRISHIVA AI — Farm-to-Market Agricultural Intelligence Platform

> **Core Philosophy:** Protect the Crop. Trust the Input. Sell Smarter.

**KRISHIVA AI** is an evidence-led agricultural decision intelligence platform designed for Indian farmers, Farmer Producer Organizations (FPOs), agronomists, and agricultural enterprises. It bridges the gap between field pathology, regulatory compliance, and market economics through a LangGraph multi-agent architecture and Google Gemini reasoning.

---

## 🌟 The Three Core Intelligence Systems

```mermaid
graph TD
    A[KRISHIVA Supervisor LangGraph] --> B[🛡️ Crop Guard Subgraph]
    A --> C[🔬 Input Trust Subgraph]
    A --> D[📈 Market Sense Subgraph]
    
    B --> B1[Live Open-Meteo & IMD Telemetry]
    B --> B2[ICAR / Epidemiological Infection Thresholds]
    
    C --> C1[Differential Diagnostic Engine]
    C --> C2[Statutory CIB&RC & FCO Registry Check]
    
    D --> D1[AGMARKNET / data.gov.in Live APMC Arrivals]
    D --> D2[Net Realization Freight & Perishability Matrix]
    
    B & C & D --> E[Google AI Gemini Multilingual Synthesizer]
    E --> F[Farmer & FPO Action Plan]
```

### 1. Crop Guard (Crop & Disease Intelligence)
- Real-time microclimatic disease favorability indices (temperature, relative humidity, leaf wetness, rainfall).
- Epidemiological risk assessment for Early Blight (*Alternaria solani*), Late Blight (*Phytophthora infestans*), and Whitefly vectors.
- Transparent rule & calibrated probabilistic outputs with clear uncertainty markers.

### 2. Market Sense (Market Discovery & Net Realization Optimization)
- Ingests official AGMARKNET and e-NAM mandi modal prices and arrivals.
- Computes quantity-aware net realization using the formula:
  $$\text{Net Realization} = \text{Gross Revenue} - (\text{Freight} + \text{Handling} + \text{Mandi Fees} + \text{Transit Quality Loss})$$
- Prevents misleading recommendations based solely on distant high modal prices.

### 3. Input Trust (Statutory Regulatory Input Verification)
- **Differential Diagnosis First:** Prevents false single-cause diagnoses (e.g. distinguishing nitrogen deficiency from iron chlorosis or waterlogging).
- **Statutory CIB&RC & FCO Compliance:** Only recommends pesticides with verified registration numbers, approved crop-target usages, exact label dosages, and Pre-Harvest Intervals (PHI).

---

## 🏗️ Repository Architecture

```
fieldnexus-sentinel/
├── backend/
│   ├── api/v1/routes.py            # FastAPI endpoints
│   ├── config/settings.py          # Pydantic Settings
│   ├── database/models.py          # SQLAlchemy PostgreSQL/SQLite models
│   ├── governance/                 # Data provenance & audit registry
│   ├── integrations/               # Open-Meteo, AGMARKNET, Google AI
│   ├── intelligence/               # Crop Guard, Market Sense, Input Trust
│   │   └── orchestrator/           # LangGraph supervisor workflow
│   ├── knowledge/                  # CIB&RC and FCO regulatory standards
│   ├── ml/training/                # Scikit-learn temporal training & model cards
│   └── schemas/api_contracts.py    # Typed Pydantic request/response schemas
├── frontend/                       # React 18 + TypeScript + Vite UI
├── data/                           # Verified raw, reference & interim datasets
├── models/                         # Trained model artifacts & evaluation cards
├── tests/unit/                     # Automated Pytest suite (10/10 verified)
└── docs/                           # Architecture, audit, and system documentation
```

---

## 🚀 Quickstart & Local Setup

### 1. Prerequisites
- Python 3.11+
- Node.js 18+ and npm

### 2. Backend Setup
```bash
# Clone the repository
git clone https://github.com/NikhilRaman12/fieldnexus-sentinel.git
cd fieldnexus-sentinel

# Configure environment
cp .env.example .env

# Run database migrations / init
python -c "from backend.database.session import init_db; init_db()"

# Run all automated tests (10/10 passing)
pytest tests/unit/test_krishiva_platform.py -v

# Start FastAPI Server
uvicorn backend.api.v1.routes:app --host 0.0.0.0 --port 8000 --reload
```
API Documentation will be live at `http://localhost:8000/docs`.

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run build
npm run dev
```
The KRISHIVA UI will be accessible at `http://localhost:3000`.

---

## 🔒 Security & Data Provenance
- Tracked secrets removed from Git index; active `.gitignore` enforcement.
- Strict data provenance identifiers (`PROV-AGMARKNET-001`, `PROV-WEATHER-003`, `PROV-CIBRC-004`).
- All recommendations carry clear regulatory citations and expert human escalation boundaries.
=======
# FieldNexus-Sentinel

A project that does not just run — it **orchestrates**.  
A pipeline that does not just process — it **transforms**.  
An agent system that does not just analyze — it **reveals unseen connections** across climate, soil, rainfall, pesticides, supply chains, sustainability, and yield.

---

## Overview
FieldNexus Sentinel was built for the **Google 5‑Day AI Agents Intensive (Nov 10–14, 2025)** under the **Agents for Good** track.  
It is not another notebook. It is a **mission‑driven architecture** that turns fragmented datasets into **actionable intelligence**.  
Every agent is a specialist. Together, they form a team that delivers insights with speed, reproducibility, and clarity.

---

## Problem
Agricultural and sustainability datasets are scattered, noisy, inconsistent, and underutilized.  
Researchers spend hours cleaning, policymakers struggle to interpret, and farmers rarely see the benefit.  
The gap between raw data and meaningful action is wide — and urgent.

---

## Solution
FieldNexus Sentinel closes that gap with a **multi‑agent pipeline**:

- **DataCleaningAgent**: transforms raw CSVs into clean, usable data  
- **EDAAgent**: generates summaries that highlight the story inside the numbers  
- **ModelAgent**: trains models (RandomForest, Neural Network, XGBoost) with reproducibility  
- **Evaluation Agent**: computes metrics that matter  
- **InsightAgent**: consolidates results into recruiter‑ready insights  
- **PipelineAgent**: orchestrates the workflow end‑to‑end  
- **InferenceAgent**: reserved for future predictive tasks  

---

## Features
- Modularity: each agent is independent yet collaborative  
- Reproducibility: outputs are consistent, stored in `outputs/reports/insights.json`  
- Professional polish: documentation, configuration, and logging are complete  


---

## QuickStart

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the full agentic pipeline via CLI:
```bash
python src/app.py
```

3. Launch the interactive Web UI Dashboard:
```bash
streamlit run src/ui.py
```

