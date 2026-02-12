from datetime import date
import logging
import warnings
from bs4 import BeautifulSoup
import requests
logger = logging.getLogger("scraper")
from config.logger import setup_logger
warnings.simplefilter("ignore")
setup_logger()
logger.info("Logger configured.")
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
base_url = "https://techcrunch.com/latest/page/{}/?offset=10"

def extract_data_tech():
    try:
        
        frame = []
        for page in range(1, 6):  # Extract 10 first pages
#=========================== Extraction of data from TechCrunch ============================
# =============================================================================================   
#         
            url = base_url.format(page)
            logger.info(f"[EXTRACT] Fetching data from: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # Check for HTTP errors

    #===================== HTML content extraction and saving =======================
            soup = BeautifulSoup(response.text, "html.parser")
            logger.info(f"[EXTRACT] Successfully extracted data from page {page}") 

    #===================== title and URL extraction =======================
            div = soup.find_all("div", class_="loop-card__content")
            for content in div:
                a = content.find("a", class_="loop-card__title-link")
                if a:
                    logger.info(f"[EXTRACT] Extracted title: {a.text.strip()}")
                    href = a.get("href")
                    logger.info(f"[EXTRACT] Extracted URL: {href}")

    #===================== date extraction =======================
                dates = content.find("time")  
                if dates:
                    date_text = dates.get("datetime", "").strip()
                    logger.info(f"[EXTRACT] Extracted date: {date_text}")  

    # ======================extraction of reference ======================= 
                source = content.find("a", class_="loop-card__author")
                if source:
                    source_text = source.text.strip()
                    logger.info(f"[EXTRACT] Extracted source: {source_text}")  

                frame.append({"title": a.text.strip(), "lien": href, "date": date_text, "auteur": source_text, "source": "TechCrunch" })
        return frame
    except requests.RequestException as e:
        logger.error(f"[EXTRACT] Error fetching TechCrunch data: {e}")

     
# 🔥 TEST LOCAL UNIQUEMENT
if __name__ == "__main__":
    data = extract_data_tech()
    print(f"Number of extracted items: {data}")
    logger.info(f"[EXTRACT] Total number of articles extracted: {data}")
    