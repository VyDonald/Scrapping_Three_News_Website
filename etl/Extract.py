# etl/extract.py
from datetime import date
import json
import logging
import warnings
from sources.extract_tech import extract_data_tech
from sources.extract_thev import extract_data_thev
from sources.extract_ar import extract_data_ars
logger = logging.getLogger("scraper")
from config.logger import setup_logger
warnings.simplefilter("ignore")
setup_logger()
logger.info("Logger configured.")

def extract_data():
    try:
        data_tech = extract_data_tech()
        data_thev = extract_data_thev()
        data_ars = extract_data_ars()
        total_data = data_tech + data_thev + data_ars
        logger.info(f"[EXTRACT] Total number of articles extracted: {len(total_data)}")
        with open("data/raw/extracted_data.json", "w") as f:
            json.dump(total_data, f, indent=4)
        logger.info(f"[EXTRACT] Extracted data saved to data/raw/extracted_data.json")    
        return total_data
    except Exception as e:
        logger.error(f"[EXTRACT] Error during data extraction: {e}")
    
# 🔥 TEST LOCAL UNIQUEMENT
if __name__ == "__main__":
    data = extract_data()        
    print(f"Total number of articles extracted: {len(data)}")