import os
import sys

# Ensure Python can find root directory and src directory
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

import pandas as pd
from agents.data_cleaning_agent import DataCleaningAgent
from agents.eda_agent import EDAAgent
from agents.model_agent import ModelAgent
from agents.evaluation_agent import EvaluationAgent
from agents.insight_agent import InsightAgent
from agents.inference_agent import InferenceAgent
from agents.pipeline_agent import PipelineAgent
from utilis import get_logger



def main():
    logger = get_logger("App")

    # Define directories
    raw_dir = os.path.join("data", "raw")
    proc_dir = os.path.join("data", "processed")
    eda_dir = os.path.join("eda", "reports")
    report_dir = os.path.join("outputs", "reports")

    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(proc_dir, exist_ok=True)
    os.makedirs(eda_dir, exist_ok=True)
    os.makedirs(report_dir, exist_ok=True)

    logger.info("==================================================")
    logger.info("   FIELDNEXUS-SENTINEL: MULTI-AGENT PIPELINE    ")
    logger.info("==================================================")

    # Initialize all specialized agents
    cleaning_agent = DataCleaningAgent()
    eda_agent = EDAAgent()
    model_agent = ModelAgent(model_type="rf")
    evaluation_agent = EvaluationAgent()
    insight_agent = InsightAgent()
    inference_agent = InferenceAgent()

    # Instantiate Orchestrator Pipeline Agent
    pipeline = PipelineAgent(
        cleaning_agent=cleaning_agent,
        eda_agent=eda_agent,
        model_agent=model_agent,
        evaluation_agent=evaluation_agent,
        insight_agent=insight_agent,
        inference_agent=inference_agent,
    )

    # Run full end-to-end pipeline execution
    results = pipeline.run_full_pipeline(
        raw_dir=raw_dir,
        proc_dir=proc_dir,
        eda_dir=eda_dir,
        report_dir=report_dir,
    )

    logger.info("=== FIELDNEXUS-SENTINEL PIPELINE EXECUTED SUCCESSFULLY ===")
    logger.info(f"Models Trained: {results['trained_models_count']}")
    logger.info(f"Report Summary: {report_dir}/insights.json")


if __name__ == "__main__":
    main()