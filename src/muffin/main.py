import json
import logging
import random
import time

import httpx
from bs4 import BeautifulSoup

URLS_FILE = "data/muffin_links.txt"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
}
FAILED_LOG = "data/failed_urls.txt"

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def get_marmiton_json(url: str) -> dict | None:
    # Définition des headers pour simuler un navigateur
    headers = HEADERS

    # 1. Récupération de la page
    response = httpx.get(url, headers=headers)
    response.raise_for_status()

    # 2. Analyse du HTML avec BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")

    # 3. Extraction du script JSON-LD
    elements = soup.find_all("script", type="application/ld+json")

    for element in elements:
        if element.string is None:
            continue

        data = json.loads(element.string)

        # Vérification si le @type est "Recipe" on a trouvé le bon JSON
        if isinstance(data, dict) and data.get("@type") == "Recipe":
            return data


## TEST
# url_test = "https://www.marmiton.org/recettes/recette_muffins-a-la-banane_14745.aspx"
# recipe_data = get_marmiton_json(url_test)

# if recipe_data:
#     print(json.dumps(recipe_data, indent=4, ensure_ascii=False))


def get_recipe_urls(
    query: str = "muffin", nb_pages: int = 1, save_to_file: str | None = None
) -> list[str]:
    base_url = "https://www.marmiton.org/recettes/recherche.aspx"
    recipe_links = set()  # Utilisation d'un set pour éviter les doublons

    headers = HEADERS

    for page in range(1, nb_pages + 1):
        logger.info(f"⏳ Collecte de la page {page}...")
        params = {"aqt": query, "page": page}

        try:
            response = httpx.get(base_url, params=params, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Sur Marmiton, les liens de recettes sont dans des balises <a>
            # On cherche les liens qui contiennent "/recettes/recette_"
            for a in soup.find_all("a", href=True):
                href = str(a["href"])
                if "/recettes/recette_" in href:
                    recipe_links.add(
                        href
                        if href.startswith("http")
                        else "https://www.marmiton.org" + href
                    )

            # Pour être plus discret
            time.sleep(1)

        except Exception as e:
            logger.warning(f"Erreur sur la page {page}: {e}")
            break

    if save_to_file:
        with open(save_to_file, "w") as f:
            for link in recipe_links:
                f.write(link + "\n")

    return list(recipe_links)


# all_muffins = get_recipe_urls(
#     query="muffin", nb_pages=100, save_to_file=URLS_FILE
# )
# logger.info(f"✅ Nombre de recettes trouvées : {len(all_muffins)}")


def run_scraper():
    # 1. Lire les URLs
    with open(URLS_FILE, "r") as f:
        urls = [line.strip() for line in f if line.strip()]

    logger.info(f"😱 Total URLs à traiter : {len(urls)}")

    for url in urls:
        # 2. Extraire un ID unique de l'URL pour le nom de fichier
        # Exemple: .../recette_muffins-au-chocolat_165038.aspx -> 165038
        try:
            recipe_id = url.split("_")[-1].split(".")[0]
        except IndexError:
            logger.warning(f"❌ Format d'URL inattendu : {url}")
            recipe_id = str(hash(url))  # Fallback si format URL bizarre

        file_path = "data/recipes/" + f"recipe_{recipe_id}.json"

        logger.info(f"⏳ Téléchargement : {url}")
        data = get_marmiton_json(url)

        if data:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            # Pour la discrétion
            time.sleep(random.uniform(1, 3))
        else:
            with open(FAILED_LOG, "a") as f:
                f.write(f"{url}\n")

    logger.info("✅ Processus terminé !")


if __name__ == "__main__":
    run_scraper()
