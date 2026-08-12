import os
import sys
import pandas as pd
import numpy as np

# Ensure Python can find root-level utilis.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utilis import get_logger
from .base_agent import BaseAgent


class InferenceAgent(BaseAgent):
    """
    InferenceAgent handles real-time single-sample or batch inference.
    Aligns raw input feature names with the trained model's feature schema.
    """

    def __init__(self):
        super().__init__(name="InferenceAgent")
        self.logger = get_logger("InferenceAgent")

    def execute(self, model_info: dict, input_data: dict) -> dict:
        return self.predict(model_info, input_data)

    def predict(self, model_info: dict, input_data: dict) -> dict:
        """
        Run inference on input data dictionary using a trained model_info object.
        """
        try:
            self.logger.info("Running inference on input sample.")
            model = model_info.get("model")
            feature_names = model_info.get("feature_names", [])
            encoder = model_info.get("encoder")
            task_type = model_info.get("task_type", "regression")

            if model is None:
                raise ValueError("Model is None in model_info dictionary.")

            # Create input DataFrame
            input_df = pd.DataFrame([input_data])

            # Apply dummy encoding if categorical text features exist in input
            input_df = pd.get_dummies(input_df, drop_first=True, dtype=float)

            # Re-index to align exactly with model training feature set
            if feature_names:
                aligned_df = pd.DataFrame(0.0, index=[0], columns=feature_names)
                for col in feature_names:
                    if col in input_df.columns:
                        aligned_df[col] = input_df[col].values[0]
            else:
                aligned_df = input_df.select_dtypes(include=["number"])

            # Make prediction
            raw_pred = model.predict(aligned_df)[0]

            # Decode prediction if label encoder exists
            decoded_pred = raw_pred
            if encoder is not None:
                try:
                    decoded_pred = encoder.inverse_transform([int(raw_pred)])[0]
                except Exception:
                    pass

            self.logger.info(f"Inference completed successfully. Prediction: {decoded_pred}")
            return {
                "prediction": decoded_pred,
                "raw_prediction": float(raw_pred) if np.issubdtype(type(raw_pred), np.number) else raw_pred,
                "task_type": task_type,
                "status": "success",
            }

        except Exception as e:
            self.logger.error(f"Inference failed: {e}")
            return {"prediction": None, "status": f"inference_error: {e}"}

