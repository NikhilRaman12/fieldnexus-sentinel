import numpy as np
from .base_agent import BaseAgent

class EvaluationAgent(BaseAgent):
    """
    EvaluationAgent computes simple evaluation metrics for trained models.
    """

    def __init__(self):
        super().__init__(name="EvaluationAgent")

    def execute(self, trained_models: dict, proc_dir: str = "") -> dict:
        return self.evaluate(trained_models, proc_dir)

    def evaluate(self, trained_models: dict, proc_dir: str) -> dict:
        metrics = {}
        for fname, result in trained_models.items():
            status = result.get("status")
            if status:
                metrics[fname] = {"status": status}
                continue

            try:
                task = result["task_type"]
                y_test = result["y_test"]
                predictions = result["predictions"]

                if len(y_test) == 0 or len(predictions) == 0:
                    metrics[fname] = {"status": "empty_test_or_pred"}
                    continue

                if task == "classification":
                    preds = np.array(predictions)
                    if np.issubdtype(preds.dtype, np.floating):
                        preds = (preds >= 0.5).astype(int)
                    acc = (np.array(y_test) == preds).mean()
                    metrics[fname] = {
                        "task_type": task,
                        "metric": "accuracy",
                        "value": float(acc),
                        "target_note": result.get("target_note"),
                        "status": "evaluated",
                    }
                else:
                    y_true = np.array(y_test, dtype=float)
                    y_pred = np.array(predictions, dtype=float)
                    rmse = float(np.sqrt(((y_true - y_pred) ** 2).mean()))
                    metrics[fname] = {
                        "task_type": task,
                        "metric": "rmse",
                        "value": rmse,
                        "target_note": result.get("target_note"),
                        "status": "evaluated",
                    }
            except Exception as e:
                metrics[fname] = {"status": f"evaluation_error: {e}"}

        return metrics