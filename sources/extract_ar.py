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
base_url3 = "https://arstechnica.com/page/{}/"

#======================= https://arstechnica.com/page/ =================================
#=============================================================================================
def extract_data_ars():
    try:
        frame = []
        for page in range(1, 6):
            url2 = base_url3.format(page)
            logger.info(f"[EXTRACT] Fetching data from: {url2}")
            response = requests.get(url2, headers=headers, timeout=10)
            response.raise_for_status()  # Check for HTTP errors

            soup = BeautifulSoup(response.text, "html.parser")
            logger.info(f"[EXTRACT] Successfully extracted data from Ars Technica page {page}")
#===================== title and URL extraction =================================================
            div = soup.find_all("div", class_="flex flex-1 flex-col justify-between pl-3 sm:pl-5")
            for content in div:
                a = content.find("a")
                if a:
                    logger.info(f"[EXTRACT] Extracted title: {a.text.strip()}")
                    href = a.get("href")
                    logger.info(f"[EXTRACT] Extracted URL: {href}")
#===================== date extraction =================================================
                dates = content.find("time")  
                if dates:
                    date_text = dates.get("datetime", "").strip()
                    logger.info(f"[EXTRACT] Extracted date: {date_text}")  
# ======================extraction of reference ==========================================
                source = content.find("span")
                if source:
                    source_text = source.text.strip()
                    logger.info(f"[EXTRACT] Extracted source: {source_text}")  
                frame.append({"title": a.text.strip(), "lien": href, "date": date_text, "auteur": source_text, "source": "Ars Technica" })
        return frame
    except requests.RequestException as e:
        logger.error(f"[EXTRACT] Error fetching Ars Technica data: {e}")  

if __name__ == "__main__":
    data = extract_data_ars()        
    logger.info(f"[EXTRACT] Total number of articles extracted: {data}")