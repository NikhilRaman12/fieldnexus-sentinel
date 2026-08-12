import os
import sys
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# Ensure Python can find root-level utilis.py and models
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utilis import get_logger
from .base_agent import BaseAgent
try:
    from models.rf_model import RandomForestModel
except ImportError:
    from src.models.rf_model import RandomForestModel


# Domain target mapping for raw datasets
DEFAULT_TARGET_MAP = {
    "agriculture": "Yield(tons)",
    "climate": "Crop_Yield_MT_per_HA",
    "pesticides": "Value",
    "rainfall": "average_rain_fall_mm_per_year",
    "soil": "pH",
    "supply_chain": "Market_Price_per_ton",
    "sustainability": "Sustainability_Score",
    "temp": "avg_temp",
    "yield-a": "Value",
    "yield-b": "hg/ha_yield",
    "kaggle_crop_recommendation": "label",
}


# High-cardinality identifier columns to drop from feature set X
ID_COLUMNS = [
    "farm_id", "market_id", "area code", "item code", "element code",
    "domain code", "year code", "unnamed: 0", "index", "id"
]


class ModelAgent(BaseAgent):
    """
    ModelAgent handles:
    - Target resolution (legitimate domain targets)
    - Zero target leakage (target column removed from feature set X)
    - Automated feature encoding and preprocessing (categorical OHE, numeric imputation)
    - Task type determination (classification vs. regression)
    - Model training using modular BaseModel wrappers (RandomForestModel, etc.)
    """

    def __init__(self, model_type: str = "rf"):
        super().__init__(name="ModelAgent")
        self.logger = get_logger("ModelAgent")
        self.model_type = model_type

    def _resolve_target(self, df: pd.DataFrame, dataset_name: str = "") -> tuple[pd.DataFrame, str, str]:
        """
        Identify legitimate domain target column from df or DEFAULT_TARGET_MAP.
        Returns (df, target_col, target_note).
        """
        df = df.copy()

        # Check explicit target map by dataset name lookup
        clean_name = os.path.basename(dataset_name).lower().replace(".csv", "").replace("_clean", "")
        mapped_target = DEFAULT_TARGET_MAP.get(clean_name)

        if mapped_target and mapped_target in df.columns:
            return df, mapped_target, f"legitimate_target:{mapped_target}"

        # Search for known target keywords in columns
        target_keywords = ["yield", "score", "price", "value", "target", "ph", "rain", "temp"]
        for col in df.columns:
            if any(kw in col.lower() for kw in target_keywords):
                return df, col, f"detected_target:{col}"

        # Fallback: choose the last numeric column as target
        num_cols = df.select_dtypes(include=["number"]).columns.tolist()
        if num_cols:
            target_col = num_cols[-1]
            return df, target_col, f"fallback_target:{target_col}"

        raise ValueError("No valid numerical or categorical target column could be identified.")

    def preprocess_features(self, df: pd.DataFrame, target_col: str) -> tuple[pd.DataFrame, pd.Series, list]:
        """
        Preprocess feature matrix X and target y:
        1. Separate target y from features X (CRITICAL: eliminates target leakage).
        2. Drop identifier/high-cardinality columns.
        3. One-Hot Encode categorical text columns.
        4. Impute missing numerical values with median.
        """
        y = df[target_col]
        X = df.drop(columns=[target_col]).copy()

        # Drop ID / key columns that cause overfitting/leakage
        cols_to_drop = [c for c in X.columns if c.lower().strip() in ID_COLUMNS or c.lower().startswith("unnamed")]
        if cols_to_drop:
            X = X.drop(columns=cols_to_drop)

        # Identify numeric vs categorical
        num_cols = X.select_dtypes(include=["number"]).columns.tolist()
        cat_cols = X.select_dtypes(exclude=["number"]).columns.tolist()

        # Numeric median imputation
        for c in num_cols:
            if X[c].isnull().sum() > 0:
                X[c] = X[c].fillna(X[c].median())

        # One-Hot Encode categorical columns safely
        if cat_cols:
            X = pd.get_dummies(X, columns=cat_cols, drop_first=True, dtype=float)

        # Final cleanup of any remaining non-numeric columns
        X = X.select_dtypes(include=["number"]).fillna(0.0)

        feature_names = X.columns.tolist()
        return X, y, feature_names

    def execute(self, df: pd.DataFrame, dataset_name: str = "") -> dict:
        """
        Execute feature preprocessing, target extraction, train/test split, and model training.
        """
        self.logger.info(f"ModelAgent started for dataset '{dataset_name}'")

        # 1. Resolve Target
        df, target_col, target_note = self._resolve_target(df, dataset_name)
        self.logger.info(f"Target variable resolved: '{target_col}' ({target_note})")

        # Subsample large datasets for ultra-fast pipeline execution
        if len(df) > 3000:
            df = df.sample(n=3000, random_state=42)

        # 2. Preprocess Features & Remove Target Leakage
        X, y, feature_names = self.preprocess_features(df, target_col)


        if X.empty or len(X) < 10:
            raise ValueError(f"Insufficient samples or features for training on dataset '{dataset_name}'.")

        # 3. Determine Task Type
        label_encoder = None
        if y.dtype == "object" or (pd.api.types.is_integer_dtype(y) and y.nunique() <= 5):
            task_type = "classification"
            if y.dtype == "object":
                label_encoder = LabelEncoder()
                y = pd.Series(label_encoder.fit_transform(y.astype(str)), index=y.index)
        else:
            task_type = "regression"

        # 4. Train / Test Split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # 5. Initialize Model Wrapper
        model_wrapper = RandomForestModel(task=task_type, n_estimators=30, random_state=42)
        model_wrapper.fit(X_train, y_train)


        predictions = model_wrapper.predict(X_test)

        self.logger.info(f"ModelAgent training complete for '{dataset_name}' (task: {task_type})")

        return {
            "model": model_wrapper,
            "task_type": task_type,
            "encoder": label_encoder,
            "target_name": target_col,
            "feature_names": feature_names,
            "X_train": X_train,
            "X_test": X_test,
            "y_train": y_train,
            "y_test": y_test,
            "predictions": predictions,
            "target_note": target_note,
            "status": "trained",
        }

    def train(self, proc_dir: str) -> dict:
        """
        Train models on all CSV datasets inside proc_dir.
        """
        trained_models = {}
        for fname in os.listdir(proc_dir):
            if not fname.endswith(".csv") or "_clean" in fname:
                continue
            path = os.path.join(proc_dir, fname)
            try:
                df = pd.read_csv(path)
                result = self.execute(df, dataset_name=fname)
                trained_models[fname] = result
                print(f"[ModelAgent] Successfully trained model for '{fname}' ({result['target_note']})")
            except Exception as e:
                self.logger.error(f"Failed to train model for '{fname}': {e}")
                trained_models[fname] = {"status": f"train_error: {e}"}

        return trained_models