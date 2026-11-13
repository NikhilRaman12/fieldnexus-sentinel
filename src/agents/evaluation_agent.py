import os
import sys
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    mean_squared_error, mean_absolute_error, r2_score
)

# Ensure Python can find root-level utilis.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utilis import get_logger
from .base_agent import BaseAgent


class EvaluationAgent(BaseAgent):
    """
    EvaluationAgent computes comprehensive metrics for trained models:
    - Regression: RMSE, MAE, R2 Score
    - Classification: Accuracy, Precision, Recall, F1 Score
    """

    def __init__(self):
        super().__init__(name="EvaluationAgent")
        self.logger = get_logger("EvaluationAgent")

    def execute(self, trained_models: dict, proc_dir: str = "") -> dict:
        return self.evaluate(trained_models, proc_dir)

    def evaluate(self, trained_models: dict, proc_dir: str = "") -> dict:
        self.logger.info("EvaluationAgent started")
        metrics = {}

        for fname, result in trained_models.items():
            status = result.get("status")
            if status != "trained":
                metrics[fname] = {"status": status or "not_trained"}
                continue

            try:
                task = result["task_type"]
                y_true = np.array(result["y_test"])
                y_pred = np.array(result["predictions"])
                target_name = result.get("target_name", "target")

                if len(y_true) == 0 or len(y_pred) == 0:
                    metrics[fname] = {"status": "empty_test_or_pred"}
                    continue

                if task == "classification":
                    acc = float(accuracy_score(y_true, y_pred))
                    prec = float(precision_score(y_true, y_pred, average="weighted", zero_division=0))
                    rec = float(recall_score(y_true, y_pred, average="weighted", zero_division=0))
                    f1 = float(f1_score(y_true, y_pred, average="weighted", zero_division=0))

                    metrics[fname] = {
                        "task_type": task,
                        "target_name": target_name,
                        "target_note": result.get("target_note"),
                        "metrics": {
                            "accuracy": round(acc, 4),
                            "precision": round(prec, 4),
                            "recall": round(rec, 4),
                            "f1_score": round(f1, 4),
                        },
                        "status": "evaluated",
                    }
                else:
                    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
                    mae = float(mean_absolute_error(y_true, y_pred))
                    r2 = float(r2_score(y_true, y_pred))

                    metrics[fname] = {
                        "task_type": task,
                        "target_name": target_name,
                        "target_note": result.get("target_note"),
                        "metrics": {
                            "rmse": round(rmse, 4),
                            "mae": round(mae, 4),
                            "r2_score": round(r2, 4),
                        },
                        "status": "evaluated",
                    }
            except Exception as e:
                self.logger.error(f"Evaluation error for {fname}: {e}")
                metrics[fname] = {"status": f"evaluation_error: {e}"}

        self.logger.info("EvaluationAgent completed successfully")
        return metrics