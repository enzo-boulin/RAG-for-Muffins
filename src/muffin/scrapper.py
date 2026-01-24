import json
import logging
import random
import time

import httpx
from bs4 import BeautifulSoup

from muffin.constant import LOGGING_LEVEL, RAW_RECIPE_FOLDER

URLS_FILE = "data/muffin_links.txt"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
}
FAILED_LOG = "data/failed_urls.txt"


logger = logging.getLogger(__name__)
logging.basicConfig(level=LOGGING_LEVEL)


def get_recipe_urls(
    query: str = "muffin", nb_pages: int = 1, save_to_file: str | None = None
) -> list[str]:
    """
    Get all the recipe urls returned by marmition for a specific query
    """
    base_url = "https://www.marmiton.org/recettes/recherche.aspx"
    recipe_links = set()  # Avoid duplicates

    headers = HEADERS

    for page in range(1, nb_pages + 1):
        logger.info(f"⏳ Collecting page {page}...")
        params = {"aqt": query, "page": page}

        try:
            response = httpx.get(base_url, params=params, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # recipe links are between <a> blocks
            # recipe links look like "/recettes/recette_"
            for a in soup.find_all("a", href=True):
                href = str(a["href"])
                if "/recettes/recette_" in href:
                    recipe_links.add(
                        href
                        if href.startswith("http")
                        else "https://www.marmiton.org" + href
                    )

            # For discretion
            time.sleep(1)

        except Exception as e:
            logger.warning(f"Error on page {page}: {e}")
            break

    if save_to_file:
        with open(save_to_file, "w") as f:
            for link in recipe_links:
                f.write(link + "\n")

    return list(recipe_links)


def get_marmiton_json(url: str) -> dict | None:
    """
    Get the raw json+ld from a recipe url.
    Returns None if fails
    """
    headers = HEADERS

    response = httpx.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    elements = soup.find_all("script", type="application/ld+json")

    # There are many ld+json blocks, we need to find the good one
    for element in elements:
        if element.string is None:
            continue

        data = json.loads(element.string)

        if isinstance(data, dict) and data.get("@type") == "Recipe":
            return data


def run_scrapper():
    """Script to get all the raw json recipes in a RAW_RECIPE_FOLDER folder"""
    urls = get_recipe_urls(nb_pages=1000)

    logger.info(f"😱 Found {len(urls)} recipes")

    for url in urls:
        try:
            recipe_id = url.split("_")[-1].split(".")[0]
        except IndexError:
            logger.warning(f"❌ Unexpected url format : {url}")
            recipe_id = str(hash(url))  # Fallback

        file_path = RAW_RECIPE_FOLDER + f"recipe_{recipe_id}.json"

        logger.info(f"⏳ Dowloading : {url}")
        data = get_marmiton_json(url)

        if data:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            time.sleep(random.uniform(1, 3))
        else:
            with open(FAILED_LOG, "a") as f:
                f.write(f"{url}\n")

    logger.info("✅ Finished scrapping !")
