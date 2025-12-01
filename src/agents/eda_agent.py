import pandas as pd
from .base_agent import BaseAgent
from utilis import get_logger


class EDAAgent(BaseAgent):
    """
    Performs Exploratory Data Analysis.
    Generates:
    - Basic statistics
    - Missing value summary
    - Numerical distribution summaries
    - Categorical value counts
    - Duplicate row counts
    - Correlation matrix
    - Outlier detection (IQR method)
    """

    def __init__(self):
        super().__init__(name="EDAAgent")
        self.logger = get_logger("EDAAgent")

    def execute(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Executes EDA and returns a structured DataFrame summary.
        """
        self.logger.info("EDAAgent started")

        summary = {}

        # Basic shape information
        summary["rows"] = df.shape[0]
        summary["columns"] = df.shape[1]

        # Data types
        summary["dtypes"] = df.dtypes.astype(str).to_dict()

        # Missing values
        summary["missing_values"] = df.isnull().sum().to_dict()

        # Duplicate rows
        summary["duplicate_rows"] = int(df.duplicated().sum())

        # Numerical description
        numeric_df = df.select_dtypes(include="number")
        if not numeric_df.empty:
            summary["numerical_summary"] = numeric_df.describe().to_dict()

            # Correlation matrix
            summary["correlations"] = numeric_df.corr().to_dict()

            # Outlier detection (IQR method)
            outlier_counts = {}
            for col in numeric_df.columns:
                q1, q3 = numeric_df[col].quantile([0.25, 0.75])
                iqr = q3 - q1
                outlier_counts[col] = int(
                    ((numeric_df[col] < (q1 - 1.5 * iqr)) |
                     (numeric_df[col] > (q3 + 1.5 * iqr))).sum()
                )
            summary["outliers"] = outlier_counts

        # Categorical description
        categorical_df = df.select_dtypes(exclude="number")
        cat_summary = {}
        for col in categorical_df.columns:
            cat_summary[col] = categorical_df[col].value_counts().head(10).to_dict()

        if categorical_df.shape[1] > 0:
            summary["categorical_summary"] = cat_summary

        # Convert dict to a DataFrame for consistency
        output_df = pd.DataFrame.from_dict(
            {k: [v] for k, v in summary.items()}, orient="columns"
        )

        self.logger.info("EDAAgent completed")
        return output_df