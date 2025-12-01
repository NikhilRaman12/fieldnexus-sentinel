from typing import Optional, Dict, Any
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.base import is_classifier
from .base_model import BaseModel


class RandomForestModel(BaseModel):
    """
    RandomForest wrapper supporting both classification and regression.
    Usage:
        rf = RandomForestModel(task="classification", n_estimators=200)
        rf.fit(X, y)
        preds = rf.predict(X_new)
    """

    def __init__(self, task: str = "classification", n_estimators: int = 200, random_state: int = 42, **kwargs):
        super().__init__()
        if task not in {"classification", "regression"}:
            raise ValueError("task must be 'classification' or 'regression'")
        self.task = task
        self.params = {"n_estimators": n_estimators, "random_state": random_state}
        self.params.update(kwargs)
        self.model = None

    def fit(self, X, y, **fit_kwargs) -> Dict[str, Any]:
        """
        Fit the RandomForest model. Returns training metadata.
        """
        if self.task == "classification":
            self.model = RandomForestClassifier(**self.params)
        else:
            self.model = RandomForestRegressor(**self.params)

        self.model.fit(X, y, **fit_kwargs)
        self.is_fitted = True

        metadata = {
            "n_features": X.shape[1] if hasattr(X, "shape") else None,
            "n_samples": len(y),
        }
        return metadata

    def predict(self, X):
        if not self.is_fitted or self.model is None:
            raise ValueError("Model is not fitted. Call fit() before predict().")
        return self.model.predict(X)

    def predict_proba(self, X):
        if not is_classifier(self.model):
            raise TypeError("predict_proba is only available for classification models.")
        return self.model.predict_proba(X)

    def feature_importances(self):
        if not self.is_fitted:
            return None
        try:
            return self.model.feature_importances_
        except Exception:
            return None

    def save(self, path: str) -> None:
        # Use base implementation (joblib)
        super().save(path)

    def load(self, path: str) -> None:
        super().load(path)
