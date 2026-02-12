# main.py
import os
import pandas as pd
from etl.Extract import extract_data
from etl.Transform import load_data as load_raw_data, transform_data
from config.logger import setup_logger

def run_pipeline():
    logger = setup_logger()

    # Step 1: Extract
    extract_data()

    # Step 2: Transform - load raw JSON files then clean
    df_raw = load_raw_data()
    if df_raw is None or df_raw.shape[0] == 0:
        logger.warning("No raw data found after extraction; aborting pipeline")
        return

    df_clean = transform_data(df_raw)

    # Step 3: Load - import inside function to avoid top-level DB deps
    try:
        from etl.Load import  load_to_db

        load_to_db(df_clean)
    except ModuleNotFoundError:
        logger.warning("Database driver not available; saving cleaned files locally instead")
        df_clean.to_csv("data/clean/loaded_data.csv", index=False)
        df_clean.to_json("data/clean/loaded_data.json", orient="records", lines=True)
    except Exception:
        logger.exception("Unexpected error during load step")
        raise
if __name__ == "__main__":
    run_pipeline()
