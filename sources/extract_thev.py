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

base_url2 = "https://www.theverge.com/archives/{}"

#======================= https://www.theverge.com/archives/2 =================================
#=============================================================================================
def extract_data_thev():
    try:
        frame = []
        for page in range(1, 6):
            url1 = base_url2.format(page)
            logger.info(f"[EXTRACT] Fetching data from: {url1}")
            response = requests.get(url1, headers=headers, timeout=10)
            response.raise_for_status()  # Check for HTTP errors

            soup = BeautifulSoup(response.text, "html.parser")
            logger.info(f"[EXTRACT] Successfully extracted data from The Verge page {page}")

    #===================== title and URL extraction =================================================
            div = soup.find_all("div", class_="_1ufh7nri")
            for content in div:
                a = content.find("a", class_="_1lkmsmo0 _1lkmsmo4")
                if a:
                    logger.info(f"[EXTRACT] Extracted title: {a.text.strip()}")
                    href = a.get("href")
                    logger.info(f"[EXTRACT] Extracted URL: https://www.theverge.com{href}")
    #===================== date extraction =================================================
                dates = content.find("time")  
                if dates:
                    date_text = dates.text.strip()
                    logger.info(f"[EXTRACT] Extracted date: {date_text}")  

    # ======================extraction of reference ==========================================
                source = content.find("span")
                if source:
                    source_text = source.text.strip()
                    logger.info(f"[EXTRACT] Extracted source: {source_text}")  
                frame.append({"title": a.text.strip(), "lien": f"https://www.theverge.com{href}", "date": date_text, "source": source_text})
        return frame      
    except requests.RequestException as e:
        logger.error(f"[EXTRACT] Error fetching The Verge data: {e}")

if __name__ == "__main__":
    data = extract_data_thev()        
    logger.info(f"[EXTRACT] Total number of articles extracted: {data}")