# etl/extract.py
from datetime import date
import json
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
base_url2 = "https://www.theverge.com/archives/{}"
base_url3 = "https://arstechnica.com/page/{}/"
def extract_data():
    try:
        
        titles_list = []
        liens_list = []
        dates_list = []
        source_list = []
        frame = []
        for page in range(1, 6):  # Extract 10 first pages
#=========================== Extraction of data from TechCrunch ============================
# =============================================================================================   
            try:         
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

            except requests.RequestException as e:
                logger.error(f"[EXTRACT] Error fetching TechCrunch data: {e}")
#======================= https://www.theverge.com/archives/2 =================================
#=============================================================================================
            try:
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
                        titles_list.append(a.text.strip())
                        href = a.get("href")
                    logger.info(f"[EXTRACT] Extracted URL: https://www.theverge.com{href}")
                    liens_list.append("https://www.theverge.com" + href)

#===================== date extraction =================================================
                    dates = content.find("time")  
                    if dates:
                        date_text = dates.text.strip()
                        logger.info(f"[EXTRACT] Extracted date: {date_text}")  
                        dates_list.append(date_text) 

# ======================extraction of reference ==========================================
                    source = content.find("span")
                    if source:
                        source_text = source.text.strip()
                        logger.info(f"[EXTRACT] Extracted source: {source_text}")  
                        source_list.append(source_text)

            except requests.RequestException as e:
                logger.error(f"[EXTRACT] Error fetching The Verge data: {e}")

#======================= https://arstechnica.com/page/ =================================
#=============================================================================================
            try:
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
                        titles_list.append(a.text.strip())
                        href = a.get("href")
                    logger.info(f"[EXTRACT] Extracted URL: {href}")
                    liens_list.append(href)
#===================== date extraction =================================================
                    dates = content.find("time")  
                    if dates:
                        date_text = dates.text.strip()
                        logger.info(f"[EXTRACT] Extracted date: {date_text}")  
                        dates_list.append(date_text)
# ======================extraction of reference ==========================================
                    source = content.find("span")
                    if source:
                        source_text = source.text.strip()
                        logger.info(f"[EXTRACT] Extracted source: {source_text}")  
                        source_list.append(source_text)
            except requests.RequestException as e:
                logger.error(f"[EXTRACT] Error fetching Ars Technica data: {e}")  

#===================== Saving extracted data to JSON file ====================================
#=============================================================================================
        for title, lien, date, source in zip(titles_list, liens_list, dates_list, source_list):
            frame.append({"title": title, "lien": lien, "date": date, "source": source})
            with open("data/raw/extracted_data.json", "w") as f:
                json.dump(frame, f, indent=4)
        logger.info(f"[EXTRACT] Successfully saved extracted data to data/raw/extracted_data.json")        

        return len(titles_list), len(liens_list), len(dates_list), len(source_list)                  
    except requests.RequestException as e:
        logger.error(f"[EXTRACT] Error fetching Ars Technica data: {e}")
        
# 🔥 TEST LOCAL UNIQUEMENT
if __name__ == "__main__":
    titles_count, liens_count, dates_count, source_count = extract_data()
    print(f"Extracted {titles_count} titles, {liens_count} URLs, {dates_count} dates, and {source_count} sources.")