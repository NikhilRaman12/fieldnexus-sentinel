import os
import sys
import json

# Ensure Python can find root-level utilis.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utilis import get_logger, save_json
from .base_agent import BaseAgent


class InsightAgent(BaseAgent):
    """
    InsightAgent consolidates evaluation metrics, model metadata,
    and dataset summaries into structured JSON reports.
    """

    def __init__(self):
        super().__init__(name="InsightAgent")
        self.logger = get_logger("InsightAgent")

    def execute(self, metrics: dict, report_dir: str = "") -> dict:
        return self.generate(metrics, report_dir)

    def generate(self, metrics: dict, report_dir: str) -> dict:
        """
        Save insights as JSON in report_dir.
        """
        self.logger.info("InsightAgent started generating report.")
        if not report_dir:
            report_dir = os.path.join("outputs", "reports")

        os.makedirs(report_dir, exist_ok=True)
        out_path = os.path.join(report_dir, "insights.json")

        summary = {
            "pipeline_status": "completed",
            "total_datasets_evaluated": len(metrics),
            "evaluations": metrics,
        }

        try:
            save_json(summary, out_path)
            self.logger.info(f"Insights report successfully saved to: {out_path}")
            print(f"[InsightAgent] Insights saved: {out_path}")
            return summary
        except Exception as e:
            self.logger.error(f"Failed to save insights report: {e}")
            return {"status": f"error: {e}"}