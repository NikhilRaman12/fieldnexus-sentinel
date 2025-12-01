import os
import abc
from typing import Any
import joblib

class BaseModel(abc.ABC):
    """
    Abstract base class for models in FieldNexus-Sentinel.
    Provides a consistent API for training, prediction and persistence.
    """

    def __init__(self):
        self.is_fitted = False
        self.model = None

    @abc.abstractmethod
    def fit(self, X, y, **fit_kwargs) -> Any:
        """
        Train the model on features X and labels y.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def predict(self, X):
        """
        Return predictions for X.
        """
        raise NotImplementedError

    def save(self, path: str) -> None:
        """
        Save the model to disk. Default uses joblib.
        Subclasses can override if another format is required.
        """
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(self.model, path)

    def load(self, path: str) -> None:
        """
        Load the model from disk. Default uses joblib.
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file not found: {path}")
        self.model = joblib.load(path)
        self.is_fitted = True
