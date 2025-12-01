import os
import pandas as pd

from agents.data_cleaning_agent import DataCleaningAgent
from agents.pipeline_agent import PipelineAgent
from agents.eda_agent import EDAAgent
from utilis import get_logger


def main():
    logger = get_logger("App")

    # Define directories
    raw_dir = os.path.join("data", "raw")
    proc_dir = os.path.join("data", "processed")
    eda_dir = os.path.join("eda", "reports")
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(proc_dir, exist_ok=True)
    os.makedirs(eda_dir, exist_ok=True)

    logger.info("=== Running Data Cleaning Agent ===")

    # Initialize agents
    cleaning_agent = DataCleaningAgent()
    pipeline_agent = PipelineAgent(cleaning_agent=cleaning_agent)

    # Run cleaning on all CSV files in raw_dir
    pipeline_agent.run_cleaning(raw_dir=raw_dir, proc_dir=proc_dir)

    logger.info("=== Running EDA Agent ===")

    eda_agent = EDAAgent()

    # Run EDA on all cleaned CSV files in proc_dir
    # Skip duplicates like "*_clean.csv" to avoid multiple summaries per dataset
    for fname in os.listdir(proc_dir):
        if not fname.lower().endswith(".csv"):
            continue
        if "_clean" in fname:
            logger.info(f"Skipping EDA for duplicate/derived file: {fname}")
            continue

        proc_path = os.path.join(proc_dir, fname)

        try:
            df = pd.read_csv(proc_path)
        except Exception as e:
            logger.error(f"Failed to read processed file {proc_path}: {e}")
            continue

        try:
            eda_summary = eda_agent.execute(df)
            out_path = os.path.join(eda_dir, f"{os.path.splitext(fname)[0]}_eda.csv")
            eda_summary.to_csv(out_path, index=False)
            logger.info(f"EDA summary saved: {out_path}")
        except Exception as e:
            logger.error(f"EDA failed for {proc_path}: {e}")

    logger.info("=== Pipeline + EDA completed successfully ===")


if __name__ == "__main__":
    main()