from .base_agent import BaseAgent
import pandas as pd


class InferenceAgent(BaseAgent):
    def predict(self, model, input_data: dict):
        try:
            self.log("Running inference on input data.")

            df = pd.DataFrame([input_data])
            prediction = model.predict(df)[0]

            self.log("Inference completed.")
            return prediction

        except Exception as e:
            self.log(f"Inference failed: {str(e)}")
            return None
