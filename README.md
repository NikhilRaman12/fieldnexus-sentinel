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