import hashlib
import json
import os
import pandas as pd
from config.logger import setup_logger
from datetime import datetime
logger = setup_logger()

RAW_DIR = "data/raw"

def load_data():
    logger.info("[TRANSFORM] Starting transformation")
    try: 
        file_path = os.path.join(RAW_DIR, "extracted_data.json")
        with open(file_path, "r") as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        logger.info(f"[TRANSFORM] Loaded data with {df.shape[0]} rows and {df.shape[1]} columns")
        return df
    except Exception as e:
        logger.error(f"[TRANSFORM] Error loading data: {e}")
        raise

#def generate_id(row):
    #source = str(row.get("source", "")).strip().lower()
    #lien = str(row.get("lien", "")).strip()
    #unique_string = source + "|" + lien
    #return hashlib.sha256(unique_string.encode("utf-8")).hexdigest()

#df["id"] = df.apply(generate_id, axis=1)


def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    try:
        logger.info("[TRANSFORM] Starting transformation")

        before = df.shape[0]

        df = df.drop_duplicates(subset=["source", "lien"]).copy()
        df["date"] = pd.to_datetime(df["date"], errors="coerce",utc=True)

        df["scraped_at"] = pd.Timestamp.utcnow()

        df["date"] = df["date"].fillna(df["scraped_at"])

        after = df.shape[0]
        logger.info(f"[TRANSFORM] Rows before: {before} → after: {after}")

        
        df["title"] = df["title"].fillna("").str.strip()
        df["auteur"] = df["auteur"].fillna("Unknown").str.strip()

        df["id"] = (
        df["source"].str.lower().str.strip() + "|" +
        df["lien"].str.strip()
            ).apply(lambda x: hashlib.sha256(x.encode()).hexdigest())

        

        df.to_csv("data/clean/clean.csv", index=False)
        logger.info("[TRANSFORM] Cleaned data saved to clean.csv")
        return df

    except Exception as e:
        logger.exception("[TRANSFORM] Error during transformation")
        raise

# 🔥 TEST LOCAL UNIQUEMENT
if __name__ == "__main__":
    df_raw = load_data()
    df_clean = transform_data(df_raw)
    print(df_clean.head())
    print(df_clean.isnull().sum())
    print(df_clean.dtypes)
