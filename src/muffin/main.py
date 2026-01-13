import json
import time

import httpx
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}


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


def get_recipe_urls(query="muffin", nb_pages=1):
    base_url = "https://www.marmiton.org/recettes/recherche.aspx"
    recipe_links = set()  # Utilisation d'un set pour éviter les doublons

    headers = HEADERS

    for page in range(1, nb_pages + 1):
        print(f"Collecte de la page {page}...")
        params = {"aqt": query, "page": page}

        try:
            response = httpx.get(base_url, params=params, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Sur Marmiton, les liens de recettes sont souvent dans des balises <a>
            # On cherche les liens qui contiennent "/recettes/recette_"
            for a in soup.find_all("a", href=True):
                href = str(a["href"])
                if "/recettes/recette_" in href:
                    recipe_links.add("https://www.marmiton.org" + href)

            # Politesse : petit délai pour ne pas surcharger le serveur
            time.sleep(1)

        except Exception as e:
            print(f"Erreur sur la page {page}: {e}")
            break

    return list(recipe_links)


# --- TEST ---
all_muffins = get_recipe_urls(query="muffin", nb_pages=2)
print(f"Nombre de recettes trouvées : {len(all_muffins)}")
for url in all_muffins[:5]:  # Affiche les 5 premiers liens
    print(f"- {url}")
