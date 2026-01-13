import json

import httpx
from bs4 import BeautifulSoup


def get_marmiton_json(url):
    # Définition des headers pour simuler un navigateur
    headers = {"User-Agent": "Mozilla/5.0"}

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

        # elif isinstance(data, list):
        #     for item in data:
        #         if item.get("@type") == "Recipe":
        #             return item


# --- TEST ---
url_test = "https://www.marmiton.org/recettes/recette_muffins-a-la-banane_14745.aspx"
recipe_data = get_marmiton_json(url_test)

if recipe_data:
    # On affiche le JSON de manière lisible
    print(json.dumps(recipe_data, indent=4, ensure_ascii=False))
