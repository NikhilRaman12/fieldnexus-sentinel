import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from .base_agent import BaseAgent


class ModelAgent(BaseAgent):
    """
    ModelAgent handles:
    - Target handling (real or synthetic if missing)
    - Train/validation split
    - Automatic task detection (classification or regression)
    - RandomForest model training
    - Model artifact and predictions return
    """

    def __init__(self):
        super().__init__(name="ModelAgent")
        self.model = None
        self.task_type = None
        self.label_encoder = None

    def _ensure_target(self, df: pd.DataFrame) -> tuple[pd.DataFrame, str]:
        """
        Ensure a 'target' column exists. If missing, create a synthetic target:
        - Choose the first numeric column.
        - target = 1 if value > median else 0 (binary classification).
        Returns the modified df and a note string.
        """
        if "target" in df.columns:
            return df, "real_target"

        num_cols = df.select_dtypes(include=["number"]).columns.tolist()
        if len(num_cols) > 0:
            src_col = num_cols[0]
            median_val = df[src_col].median()
            df = df.copy()
            df["target"] = (df[src_col] > median_val).astype(int)
            return df, f"synthetic_target_from:{src_col}"
        else:
            # No numeric columns: create constant target (still lets pipeline run)
            df = df.copy()
            df["target"] = 0
            return df, "synthetic_target_constant"

    def execute(self, df: pd.DataFrame) -> dict:
        """
        Train a RandomForest model. If target is missing, synthetic target is created.
        Returns:
            {
                "model": fitted_model,
                "task_type": "classification" or "regression",
                "encoder": LabelEncoder or None,
                "X_train": ...,
                "X_test": ...,
                "y_train": ...,
                "y_test": ...,
                "predictions": ...,
                "target_note": "real_target" or "synthetic_*"
            }
        """
        df, target_note = self._ensure_target(df)

        X = df.drop(columns=["target"])
        y = df["target"]

        # Detect task type (synthetic target uses classification)
        if y.dtype == "object" or y.nunique() < 15:
            self.task_type = "classification"
            self.label_encoder = None if y.dtype != "object" else LabelEncoder()
            if self.label_encoder is not None:
                y = self.label_encoder.fit_transform(y)
        else:
            self.task_type = "regression"

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        if self.task_type == "classification":
            self.model = RandomForestClassifier(
                n_estimators=200, random_state=42, n_jobs=-1
            )
        else:
            self.model = RandomForestRegressor(
                n_estimators=200, random_state=42, n_jobs=-1
            )

        self.model.fit(X_train, y_train)
        predictions = self.model.predict(X_test)

        return {
            "model": self.model,
            "task_type": self.task_type,
            "encoder": self.label_encoder,
            "X_train": X_train,
            "X_test": X_test,
            "y_train": y_train,
            "y_test": y_test,
            "predictions": predictions,
            "target_note": target_note,
        }

    def train(self, proc_dir: str) -> dict:
        """
        Loop through all processed CSVs in proc_dir,
        call execute(df) for each, and return a dict of results.
        """
        trained_models = {}
        for fname in os.listdir(proc_dir):
            if not fname.endswith(".csv"):
                continue
            path = os.path.join(proc_dir, fname)
            try:
                df = pd.read_csv(path)
            except Exception as e:
                print(f"[ModelAgent] Skip '{path}' (read error): {e}")
                trained_models[fname] = {"status": f"read_error: {e}"}
                continue

            try:
                result = self.execute(df)
                trained_models[fname] = result
                print(f"[ModelAgent] Trained model for {fname} ({result['target_note']})")
            except Exception as e:
                print(f"[ModelAgent] Failed to train on '{fname}': {e}")
                trained_models[fname] = {"status": f"train_error: {e}"}

        return trained_models