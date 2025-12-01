import os
import pandas as pd
from .base_agent import BaseAgent
from utilis import get_logger   # root-level import

class PipelineAgent(BaseAgent):
    """
    Orchestrates the pipeline by coordinating different agents.
    Currently supports: DataCleaningAgent, but can be extended.
    """

    def __init__(self, cleaning_agent=None):
        super().__init__(name="PipelineAgent")
        self.cleaning_agent = cleaning_agent
        self.logger = get_logger("PipelineAgent")

    def execute(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Required abstract method from BaseAgent.
        For PipelineAgent, this can just return the DataFrame unchanged
        or apply cleaning if provided.
        """
        if self.cleaning_agent:
            self.logger.info("Executing cleaning agent on DataFrame")
            return self.cleaning_agent.run(df)
        self.logger.info("No cleaning agent provided, returning DataFrame unchanged")
        return df

    def run_cleaning(self, raw_dir: str, proc_dir: str):
        """
        Run the cleaning agent on all CSV files in raw_dir
        and save cleaned versions into proc_dir.
        """
        if not self.cleaning_agent:
            raise ValueError("PipelineAgent requires a cleaning_agent to run cleaning.")

        self.logger.info("Pipeline cleaning started")
        for fname in os.listdir(raw_dir):
            if fname.lower().endswith(".csv"):
                raw_path = os.path.join(raw_dir, fname)
                df = pd.read_csv(raw_path)

                # Apply cleaning
                cleaned_df = self.cleaning_agent.run(df)

                # Save cleaned file
                # Strip whitespace from filename before saving
                out_path = os.path.join(proc_dir, fname.strip())
                cleaned_df.to_csv(out_path, index=False)
                self.logger.info(f"Cleaned file saved: {out_path}")

        self.logger.info("Pipeline cleaning completed successfully")