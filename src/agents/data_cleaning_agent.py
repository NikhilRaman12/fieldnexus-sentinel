import os
import sys
import pandas as pd

# Ensure Python can find root-level utilis.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utilis import get_logger

class DataCleaningAgent:
    """
    Cleans raw data by handling missing values, duplicates, and formatting issues.
    Uses logging to track execution steps.
    """

    def __init__(self):
        # Initialize logger specific to this agent
        self.logger = get_logger("DataCleaningAgent")

    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Run the cleaning process on the provided DataFrame.
        Returns a cleaned DataFrame.
        """
        self.logger.info("DataCleaningAgent started")

        # Example cleaning steps (customize as needed)
        # 1. Drop duplicates
        df = df.drop_duplicates()

        # 2. Handle missing values (simple fill with empty string for demo)
        df = df.fillna("")

        # 3. Strip whitespace from column names
        df.columns = df.columns.str.strip()

        self.logger.info("DataCleaningAgent completed")
        return df