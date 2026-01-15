import json
import logging
import os
import random
import re
import time

import httpx
from bs4 import BeautifulSoup

from muffin.recipe import Ingredient

URLS_FILE = "data/muffin_links.txt"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
}
FAILED_LOG = "data/failed_urls.txt"

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def get_marmiton_json(url: str) -> dict | None:
    """
    Récupère les données JSON-LD d'une recette Marmiton à partir de son URL.
    Retourne un dictionnaire avec les données de la recette ou None en cas d'échec
    """
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


def get_recipe_urls(
    query: str = "muffin", nb_pages: int = 1, save_to_file: str | None = None
) -> list[str]:
    """
    Récupère les URLs des recettes Marmiton en fonction d'une requête de recherche.
    Args:
        query (str): Terme de recherche.
        nb_pages (int): Nombre de pages de résultats à parcourir.
        save_to_file (str | None): Chemin du fichier pour sauvegarder les URLs. Si None, ne sauvegarde pas.
    Returns:
        list[str]: Liste des URLs des recettes trouvées.
    """
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


def run_scraper():
    """Lance le scrapper pour récupérer les recettes Marmiton listées dans le fichier URLS_FILE."""
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

        file_path = "data/raw_recipes/" + f"recipe_{recipe_id}.json"

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


def get_all_existing_ingredients(
    filepath: str = "data/raw_recipes", save_to: str = "data/"
) -> set[str]:
    """Parcourt tous les fichiers JSON dans le répertoire spécifié,
    extrait les ingrédients et les sauvegarde dans un fichier texte.
    Args:
        filepath (str): Chemin du répertoire contenant les fichiers JSON.
        save_to (str): Chemin du répertoire où sauvegarder le fichier texte.
    Returns:
        set[str]: Ensemble des ingrédients extraits.
    """
    all_ingredients: set[str] = set()

    for file in os.listdir(filepath):
        if not file.endswith(".json"):
            continue
        with open(os.path.join(filepath, file), "r", encoding="utf-8") as f:
            data = json.load(f)
            ingredients = data.get("recipeIngredient", [])
            all_ingredients |= set(ingredients)

    with open(save_to + "raw_ingredients.txt", "w") as f:
        for ingredient in all_ingredients:
            f.write(ingredient + "\n")

    return all_ingredients


def fraction_to_float(value_str: str) -> float:
    """
    Convertit une chaîne (fraction ou décimal) en float.
    Gère "3/4", "0.75" et "0,75".
    """
    normalized_str = value_str.replace(",", ".")

    if "/" in normalized_str:
        parts = normalized_str.split("/")
        if len(parts) == 2:
            return float(parts[0]) / float(parts[1])

    return float(normalized_str)


def clean_ingredient(
    raw_ingredient: str,
) -> Ingredient:
    """Nettoie une chaîne d'ingrédient brut et retourne un objet Ingredient."""
    units = [
        # --- VOLUMES & CONTENANTS ---
        r"(?:verres?|tasses?|bols?|pots?|bocaux|briques?|briquettes?|boîtes?)",
        r"(?:barquettes?|paquets?|sachets?|tablettes?|portions?)",
        r"(?:cl|ml|dl|l|kg|g)\b",  # Unités métriques avec bordure de mot
        # --- CUILLÈRES (Variantes complexes) ---
        # Capture : cuillères à soupe, bonnes cuillères à café, demi cuillères à café, etc.
        r"(?:[a-zâéè]+ )?cuillères?(?: à (?:soupe|café|thé))?",
        r"à thé",  # Cas isolés
        # --- DÉCOUPE & FORMES ---
        r"(?:tranches?(?: épaisses)?|lamelles?|rondelles?|dés|morceaux?|carrés?)",
        r"(?:gousses?|feuilles?|branches?|brins?|bouquets?|pépites?|traits?)",
        r"(?:pointes?|portions?)",
        # --- MESURES MANUELLES & PRÉCISION ---
        r"(?:(?:grosses |petites )?pincées?)",
        r"(?:(?:grosses |petites )?poignées?)",
        r"(?:gouttes?)",
        # --- UNITÉS GÉNÉRIQUES & FRACTIONS ---
        r"unité\(s\)",
        r"demis?",  # Pour "1 demi de levure"
        r"sachets?",
    ]

    units_pattern = r"|".join(units)

    # Regex principale pour extraire QTY, UNIT et NAME
    regex = rf"^(?P<qty>\d+[\s\./]\d+|\d+(?:[\.,]\d+)?)?\s*(?P<unit>\b(?:{units_pattern})\b)?\s*(?:de\s+|d['’]\s*)?(?P<name>.*)"

    match = re.match(regex, raw_ingredient.strip(), re.IGNORECASE)

    if not match:
        raise ValueError(f"Impossible de parser l'ingrédient : {raw_ingredient}")

    raw_qty = match.group("qty")
    qty = fraction_to_float(raw_qty) if raw_qty else None

    unit = match.group("unit") or None
    name = match.group("name").strip()

    # 1. Coupe à la première parenthèse ouvrante
    name = re.sub(r"\s*\(.*", "", name)

    # 2. Coupe aux points de suspension (...)
    name = re.sub(r"\s*\.\.\..*", "", name)

    # --- NOUVELLE RÈGLE : Conjonctions et symboles ---
    # On cherche " et/ou ", " ou ", " et " ... (avec \b pour les mots entiers) ou le signe "+"
    # Puis on coupe tout ce qui suit (.*)
    name = re.sub(
        r"\s*(?:\bet/ou\b|\bou\b|\bet\b|\bplus\b|\bavec\b|\bpour\b|\bdans\b|\+).*",
        "",
        name,
        flags=re.IGNORECASE,
    )

    # 3. Nettoyage final des prépositions et espaces
    name = re.sub(r"^[dD]['’]\s*", "", name).strip()

    return Ingredient(
        name=name,
        quantity=qty,
        unit=unit,
    )
