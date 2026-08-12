import os
import sys
import pandas as pd

# Ensure Python can find root-level utilis.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utilis import get_logger, save_json
from .base_agent import BaseAgent


class PipelineAgent(BaseAgent):
    """
    Orchestrates the FieldNexus-Sentinel pipeline by coordinating all specialized agents:
    - DataCleaningAgent
    - EDAAgent
    - ModelAgent
    - EvaluationAgent
    - InsightAgent
    - InferenceAgent
    """

    def __init__(
        self,
        cleaning_agent=None,
        eda_agent=None,
        model_agent=None,
        evaluation_agent=None,
        insight_agent=None,
        inference_agent=None,
    ):
        super().__init__(name="PipelineAgent")
        self.cleaning_agent = cleaning_agent
        self.eda_agent = eda_agent
        self.model_agent = model_agent
        self.evaluation_agent = evaluation_agent
        self.insight_agent = insight_agent
        self.inference_agent = inference_agent
        self.logger = get_logger("PipelineAgent")

    def execute(self, *args, **kwargs):
        """
        Default execute entrypoint.
        """
        self.logger.info("Executing PipelineAgent.")
        return {"status": "PipelineAgent ready"}

    def run_cleaning(self, raw_dir: str, proc_dir: str):
        """
        Run DataCleaningAgent on all CSV files in raw_dir and save to proc_dir.
        """
        if not self.cleaning_agent:
            raise ValueError("PipelineAgent requires cleaning_agent to run cleaning.")

        self.logger.info("Pipeline cleaning phase started.")
        os.makedirs(proc_dir, exist_ok=True)

        for fname in os.listdir(raw_dir):
            if fname.lower().endswith(".csv"):
                raw_path = os.path.join(raw_dir, fname)
                df = pd.read_csv(raw_path)

                cleaned_df = self.cleaning_agent.run(df)
                out_path = os.path.join(proc_dir, fname.strip())
                cleaned_df.to_csv(out_path, index=False)
                self.logger.info(f"Cleaned file saved: {out_path}")

        self.logger.info("Pipeline cleaning phase completed successfully.")

    def run_full_pipeline(self, raw_dir: str, proc_dir: str, eda_dir: str, report_dir: str) -> dict:
        """
        Run the complete end-to-end pipeline across all agents.
        """
        self.logger.info("=== STARTING FULL END-TO-END PIPELINE ===")

        # 1. Data Cleaning
        self.run_cleaning(raw_dir, proc_dir)

        # 2. EDA Generation
        if self.eda_agent:
            self.logger.info("--- Phase 2: EDA Generation ---")
            os.makedirs(eda_dir, exist_ok=True)
            for fname in os.listdir(proc_dir):
                if fname.lower().endswith(".csv") and "_clean" not in fname:
                    df = pd.read_csv(os.path.join(proc_dir, fname))
                    summary = self.eda_agent.run(df)
                    summary.to_csv(os.path.join(eda_dir, f"{os.path.splitext(fname)[0]}_eda.csv"), index=False)

        # 3. Model Training
        trained_models = {}
        if self.model_agent:
            self.logger.info("--- Phase 3: Model Training ---")
            trained_models = self.model_agent.train(proc_dir)

        # 4. Evaluation
        evaluation_results = {}
        if self.evaluation_agent:
            self.logger.info("--- Phase 4: Model Evaluation ---")
            evaluation_results = self.evaluation_agent.run(trained_models, proc_dir)

        # 5. Insights & Report Export
        report_summary = {}
        if self.insight_agent:
            self.logger.info("--- Phase 5: Insight Export ---")
            report_summary = self.insight_agent.run(evaluation_results, report_dir)

        # 6. Sample Inference Verification
        inference_samples = {}
        if self.inference_agent and trained_models:
            self.logger.info("--- Phase 6: Sample Inference Verification ---")
            for dataset_name, model_info in trained_models.items():
                if model_info.get("status") == "trained" and "X_test" in model_info:
                    test_sample = model_info["X_test"].iloc[0].to_dict()
                    pred = self.inference_agent.run(model_info, test_sample)
                    inference_samples[dataset_name] = pred

        self.logger.info("=== FULL END-TO-END PIPELINE COMPLETED SUCCESSFULLY ===")
        return {
            "trained_models_count": len(trained_models),
            "evaluations": evaluation_results,
            "insights": report_summary,
            "inference_samples": inference_samples,
        }