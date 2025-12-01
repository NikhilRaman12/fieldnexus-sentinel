from typing import Any, Dict, Optional
import os
import numpy as np

try:
    import tensorflow as tf  # type: ignore
    from tensorflow import keras  # type: ignore
except Exception as exc:
    tf = None
    keras = None
    _tf_import_error = exc

from .base_model import BaseModel


class NeuralNetworkModel(BaseModel):
    """
    Simple feed-forward neural network for tabular data.
    Requires TensorFlow/Keras installed.

    Usage:
        nn = NeuralNetworkModel(hidden_units=[128,64], epochs=50, batch_size=32, task='classification')
        nn.fit(X_train, y_train)
        preds = nn.predict(X_test)
    """

    def __init__(
        self,
        hidden_units: Optional[list] = None,
        activation: str = "relu",
        optimizer: str = "adam",
        epochs: int = 50,
        batch_size: int = 32,
        task: str = "classification",
        loss: Optional[str] = None,
        metrics: Optional[list] = None,
        random_seed: int = 42,
    ):
        super().__init__()
        if tf is None or keras is None:
            raise ImportError(f"TensorFlow is required for NeuralNetworkModel. Import error: {_tf_import_error}")

        self.hidden_units = hidden_units or [128, 64]
        self.activation = activation
        self.optimizer = optimizer
        self.epochs = epochs
        self.batch_size = batch_size
        self.task = task
        self.loss = loss
        self.metrics = metrics or (["accuracy"] if task == "classification" else ["mse"])
        self.random_seed = random_seed
        tf.random.set_seed(self.random_seed)
        self.model = None

    def _build_model(self, input_shape: int, n_classes: Optional[int] = None):
        inputs = keras.layers.Input(shape=(input_shape,))
        x = inputs
        for units in self.hidden_units:
            x = keras.layers.Dense(units, activation=self.activation)(x)
        if self.task == "classification":
            if n_classes is None or n_classes <= 2:
                outputs = keras.layers.Dense(1, activation="sigmoid")(x)
                loss = self.loss or "binary_crossentropy"
            else:
                outputs = keras.layers.Dense(n_classes, activation="softmax")(x)
                loss = self.loss or "sparse_categorical_crossentropy"
        else:
            outputs = keras.layers.Dense(1, activation="linear")(x)
            loss = self.loss or "mse"

        model = keras.Model(inputs=inputs, outputs=outputs)
        model.compile(optimizer=self.optimizer, loss=loss, metrics=self.metrics)
        return model

    def fit(self, X, y, validation_data: Optional[tuple] = None, **fit_kwargs) -> Dict[str, Any]:
        """
        Fit the Keras model. X must be a 2D numpy array or pandas DataFrame.
        y must be 1D labels.
        """
        X_arr = np.asarray(X)
        y_arr = np.asarray(y)

        # Determine number of classes if classification
        n_classes = None
        if self.task == "classification":
            unique = np.unique(y_arr)
            if len(unique) > 2:
                # multiclass
                n_classes = len(unique)

        self.model = self._build_model(input_shape=X_arr.shape[1], n_classes=n_classes)
        history = self.model.fit(
            X_arr,
            y_arr,
            epochs=self.epochs,
            batch_size=self.batch_size,
            validation_data=validation_data,
            verbose=0,
            **fit_kwargs,
        )
        self.is_fitted = True
        return {"history": history.history}

    def predict(self, X):
        if not self.is_fitted or self.model is None:
            raise ValueError("Neural network model is not fitted.")
        X_arr = np.asarray(X)
        preds = self.model.predict(X_arr, batch_size=self.batch_size, verbose=0)
        if self.task == "classification":
            # binary or multiclass
            if preds.shape[-1] == 1:
                return (preds.ravel() > 0.5).astype(int)
            else:
                return preds.argmax(axis=1)
        else:
            return preds.ravel()

    def save(self, path: str) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        # save as TF SavedModel directory
        self.model.save(path, save_format="tf")

    def load(self, path: str) -> None:
        if tf is None or keras is None:
            raise ImportError("TensorFlow not available to load neural network model.")
        self.model = keras.models.load_model(path)
        self.is_fitted = True
