import json
import logging
import time

import httpx
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
}

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


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
#     query="muffin", nb_pages=100, save_to_file="data/muffin_links.txt"
# )
# logger.info(f"✅ Nombre de recettes trouvées : {len(all_muffins)}")
