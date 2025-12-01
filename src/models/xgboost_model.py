from typing import Any, Dict
import os

try:
    import xgboost as xgb  # type: ignore
    from xgboost import XGBClassifier, XGBRegressor  # type: ignore
except Exception as exc:
    XGBClassifier = None
    XGBRegressor = None
    xgb = None
    _xgboost_import_error = exc

from .base_model import BaseModel


class XGBoostModel(BaseModel):
    """
    XGBoost wrapper supporting classification or regression.
    Ensure xgboost is installed in the environment.
    """

    def __init__(self, task: str = "classification", **params):
        super().__init__()
        if task not in {"classification", "regression"}:
            raise ValueError("task must be 'classification' or 'regression'")
        self.task = task
        self.params = params or {}
        self.model = None

        if xgb is None:
            raise ImportError(
                "xgboost is required for XGBoostModel but it is not installed. "
                f"Original import error: {_xgboost_import_error}"
            )

    def fit(self, X, y, **fit_kwargs) -> Dict[str, Any]:
        if self.task == "classification":
            self.model = XGBClassifier(**self.params)
        else:
            self.model = XGBRegressor(**self.params)

        # Fit the model
        self.model.fit(X, y, **fit_kwargs)
        self.is_fitted = True
        return {"n_samples": len(y), "n_features": X.shape[1] if hasattr(X, "shape") else None}

    def predict(self, X):
        if not self.is_fitted or self.model is None:
            raise ValueError("Model not fitted.")
        return self.model.predict(X)

    def predict_proba(self, X):
        if self.task != "classification":
            raise TypeError("predict_proba available only for classification.")
        return self.model.predict_proba(X)

    def feature_importances(self):
        if not self.is_fitted:
            return None
        try:
            return self.model.feature_importances_
        except Exception:
            return None

    def save(self, path: str) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        # XGBoost models have their own save_model
        if hasattr(self.model, "save_model"):
            self.model.save_model(path)
        else:
            super().save(path)

    def load(self, path: str) -> None:
        if xgb is None:
            raise ImportError("xgboost not available to load model.")
        model = XGBClassifier() if self.task == "classification" else XGBRegressor()
        model.load_model(path)
        self.model = model
        self.is_fitted = True
