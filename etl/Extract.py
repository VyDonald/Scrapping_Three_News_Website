# etl/extract.py
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


def extract_data():
    try:
        titles_list = []
        liens_list = []
        dates_list = []
        source_list = []
        for page in range(1, 11):  # Extract 10 first pages
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
                    titles_list.append(a.text.strip())
                    href = a.get("href")
                logger.info(f"[EXTRACT] Extracted URL: {href}")
                liens_list.append(href)

#===================== date extraction =======================
                dates = content.find("time")  
                if dates:
                    date_text = dates.text.strip()
                    logger.info(f"[EXTRACT] Extracted date: {date_text}")  
                    dates_list.append(date_text) 

# ======================extraction of reference ======================= 
                source = content.find("a", class_="loop-card__author")
                if source:
                    source_text = source.text.strip()
                    logger.info(f"[EXTRACT] Extracted source: {source_text}")  
                    source_list.append(source_text)                 
        logger.info(f"[EXTRACT] Extraction completed. Total titles: {len(titles_list)}, Total links: {len(liens_list)}, Total dates: {len(dates_list)}, Total sources: {len(source_list)}")         
        return len(titles_list), len(liens_list), len(dates_list), len(source_list)
            
    except requests.RequestException as e:
        logger.error(f"[EXTRACT] Error during extraction: {e}")
        return None

# 🔥 TEST LOCAL UNIQUEMENT
if __name__ == "__main__":
    data = extract_data()
    if data:
        print("Data extracted successfully!")
        print(f"Titles: {data[0]}, Links: {data[1]}, Dates: {data[2]}, Sources: {data[3]}")
    else:
        print("Failed to extract data.")