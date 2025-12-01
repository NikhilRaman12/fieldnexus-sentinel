import os
import json
from .base_agent import BaseAgent

class InsightAgent(BaseAgent):
    """
    InsightAgent generates final insights/reports from evaluation metrics.
    """

    def __init__(self):
        super().__init__(name="InsightAgent")

    def execute(self, metrics: dict, report_dir: str = "") -> None:
        """
        Adapter to satisfy BaseAgent's abstract 'execute' contract.
        Delegates to generate().
        """
        return self.generate(metrics, report_dir)

    def generate(self, metrics: dict, report_dir: str) -> None:
        """
        Save insights as JSON in report_dir.
        """
        os.makedirs(report_dir, exist_ok=True)
        out_path = os.path.join(report_dir, "insights.json")
        try:
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(metrics, f, indent=4, ensure_ascii=False)
            print(f"[InsightAgent] Insights saved: {out_path}")
        except Exception as e:
            print(f"[InsightAgent] Failed to save insights: {e}")