# FieldNexus Sentinel Architecture

## Pipeline Flow
Raw Data >DataCleaningAgent > EDAAgent > ModelAgent > EvaluationAgent > InsightAgent > Reports

## Agents
- DataCleaningAgent: Cleans raw CSVs, handles missing values, standardizes formats.
- EDAAgent: Generates dataset summaries (statistics, distributions).
- ModelAgent: Trains ML models (RandomForest, Neural Network, XGBoost).
- EvaluationAgent: Computes metrics (accuracy, RMSE).
- InsightAgent: Consolidates metrics into recruiter‑ready insights.
- PipelineAgent: Orchestrates the workflow end‑to‑end.
- InferenceAgent: Reserved for future prediction tasks.

## Models
- RandomForest
- Neural Network
- XGBoost