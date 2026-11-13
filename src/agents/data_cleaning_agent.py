import os
import sys
import pandas as pd
import numpy as np

# Ensure Python can find root-level utilis.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utilis import get_logger
from .base_agent import BaseAgent


class DataCleaningAgent(BaseAgent):
    """
    Cleans raw data by handling missing values, duplicates, and formatting issues.
    Preserves numerical types by applying median imputation to numeric columns
    and categorical filling to text columns.
    """

    def __init__(self):
        super().__init__(name="DataCleaningAgent")
        self.logger = get_logger("DataCleaningAgent")

    def execute(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Run the cleaning process on the provided DataFrame.
        Returns a cleaned DataFrame.
        """
        self.logger.info("DataCleaningAgent started")
        df = df.copy()

        # 1. Strip whitespace from column names
        df.columns = df.columns.astype(str).str.strip()

        # 2. Drop duplicate rows
        df = df.drop_duplicates()

        # 3. Strip whitespace from string cells and handle NaNs cleanly
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                # Fill missing numeric values with median if any exist
                if df[col].isnull().sum() > 0:
                    median_val = df[col].median()
                    df[col] = df[col].fillna(median_val)
            else:
                # String/object column: strip whitespace and fill missing with "Unknown"
                df[col] = df[col].astype(str).str.strip()
                df[col] = df[col].replace(["nan", "NaN", "None", ""], "Unknown")

        self.logger.info("DataCleaningAgent completed successfully")
        return df