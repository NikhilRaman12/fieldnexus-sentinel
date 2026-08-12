# Devpost Hackathon Submission Package - ML Empowerment Build Challenge

## Project Title
**FieldNexus-Sentinel AI: Autonomous Multi-Agent Agricultural & Soil Intelligence Platform**

---

## Project Tagline / Elevator Pitch
An autonomous multi-agent machine learning platform that orchestrates dataset cleaning, exploratory data analysis, zero-leakage model training, evaluation, and interactive crop recommendation simulation for sustainable agriculture.

---

## Project Description

### 1. Problem Statement
Agricultural, soil, and climate datasets worldwide are severely fragmented, noisy, unstandardized, and underutilized. Farmers, agronomists, and environmental researchers struggle with scattered data across soil pH, Nitrogen-Phosphorus-Potassium ($N, P, K$) nutrient levels, annual rainfall, temperature fluctuations, and supply chain market prices. Traditional machine learning scripts often suffer from severe target leakage, hard-coded risk scores, categorical encoding errors, and lack of reproducible execution.

### 2. Solution Overview
FieldNexus-Sentinel solves this by deploying a team of specialized AI agents:
- **DataCleaningAgent**: Standardizes schemas, imputes missing numerical values via median strategy, and cleans categorical strings.
- **EDAAgent**: Performs feature distribution analysis, IQR outlier detection, missing value auditing, and correlation matrix generation.
- **ModelAgent**: Dynamically resolves legitimate domain target variables, enforces **zero target leakage**, applies One-Hot Encoding, drops high-cardinality identifier columns, and trains Random Forest / Neural Network classifiers & regressors.
- **EvaluationAgent**: Computes genuine evaluation metrics ($R^2$, RMSE, MAE for regression; Accuracy, Weighted Precision, Recall, and F1-Score for classification).
- **InsightAgent**: Synthesizes pipeline metrics into structured audit-ready JSON reports.
- **InferenceAgent**: Aligns feature schemas and performs live single-sample predictive inference.
- **PipelineAgent**: Orchestrates all agents end-to-end with full error handling and logging.

The system features an **Interactive Streamlit Web UI Dashboard** allowing users to run the pipeline, explore dataset analytics, and simulate live soil & climate crop recommendations.

### 3. Key Features
1. **Autonomous Multi-Agent Orchestration**: Executes a seamless 6-phase pipeline from raw CSV ingestion to structured insight export.
2. **Zero Target Leakage Engine**: Eliminates feature-target contamination by isolating target vectors prior to feature preprocessing and train-test splitting.
3. **Multi-Task Machine Learning**: Processes both regression (Crop Yield MT/ha, Market Price, Soil pH) and multi-class classification (22-class Kaggle Crop Recommendation).
4. **Interactive Crop Recommendation Simulator**: Sliders for Nitrogen ($N$), Phosphorus ($P$), Potassium ($K$), Temperature, Humidity, Soil pH, and Rainfall to output real-time AI crop recommendations (e.g., `RICE`, `MAIZE`, `COTTON`, `COFFEE`).
5. **Audit-Ready Insights Export**: Automatically exports structured JSON audit logs (`outputs/reports/insights.json`) documenting model metrics, target notes, and pipeline health.

### 4. Technologies Used
- **Programming & ML**: Python 3.11, Scikit-learn, Pandas, NumPy, XGBoost, PyTorch / Keras
- **Agentic Framework**: Modular Object-Oriented Python Agentic Hierarchy (`BaseAgent` base class)
- **Web UI & Visualization**: Streamlit, Matplotlib, Seaborn
- **Version Control & Repository**: Git, GitHub

### 5. Target Users
- **Smallholder Farmers & Agricultural Advisors**: Receive instant data-driven crop recommendations tailored to localized soil chemistry.
- **Agronomists & Data Scientists**: Automate exploratory data analysis and baseline model training across disparate agricultural datasets.
- **Environmental Researchers & Policy Makers**: Access reproducible, audit-ready ML metrics on crop yield sustainability and soil health.

---

## Project Repository & Demo Links

- **GitHub Repository**: [https://github.com/NikhilRaman12/fieldnexus-sentinel.git](https://github.com/NikhilRaman12/fieldnexus-sentinel.git)
- **Live Local UI URL**: `http://localhost:8501`

---

## Included Demonstration Files & Screenshots

- `prediction_result_1786562543684.png`: Visual demonstration of the Live Crop Recommendation Simulator predicting optimal crop selection (`RICE`) from soil $N-P-K$ and climate parameters.
- `outputs/reports/insights.json`: Pipeline evaluation metrics export across all trained models.
- `logs/pipeline.log`: Complete execution log trace of the multi-agent pipeline.
