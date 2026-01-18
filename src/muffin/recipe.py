import json
import re
from dataclasses import dataclass
from enum import Enum

from muffin.utils import fraction_to_float, normalize_text


class ServingUnit(str, Enum):
    pieces = "pieces"
    persons = "persons"


@dataclass
class Servings:
    quantity: int
    unit: ServingUnit


@dataclass
class Ingredient:
    name: str
    quantity: float | None
    unit: str | None


@dataclass
class Recipe:
    id: int
    title: str
    prep_time: int  # minutes
    cook_time: int  # minutes
    total_time: int  # minutes
    servings: Servings
    ingredients: list[Ingredient]
    instructions: list[str]

    def get_ingredients_name(self):
        return [ingredient.name for ingredient in self.ingredients]


def clean_servings(line: str) -> Servings:
    """
    Analyse une ligne pour extraire la quantité et l'unité.
    """
    normalized_line = normalize_text(line)

    match_number = re.search(r"^(\d+)", normalized_line.strip())

    quantity = int(match_number.group(1))

    piece_keywords = [
        "muffin",
        "piece",
        "brioche",
        "confiserie",
        "mini",
        "burger",
        "gateau",
        "cupcake",
    ]

    person_keywords = [
        "personne",
        "portion",
    ]

    if any(kw in normalized_line for kw in piece_keywords):
        unit = ServingUnit.pieces

    elif any(kw in normalized_line for kw in person_keywords):
        unit = ServingUnit.persons

    else:
        raise ValueError(f"Aucune unité reconnue dans la ligne : '{line}'")

    return Servings(quantity=quantity, unit=unit)


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

    # Coupe à la première parenthèse ouvrante
    name = re.sub(r"\s*\(.*", "", name)

    # Coupe aux points de suspension (...)
    name = re.sub(r"\s*\.\.\..*", "", name)

    # On cherche " et/ou ", " ou ", " et " ... (avec \b pour les mots entiers) ou le signe "+"
    # Puis on coupe tout ce qui suit (.*)
    name = re.sub(
        r"\s*(?:\bet/ou\b|\bou\b|\bet\b|\bplus\b|\bavec\b|\bpour\b|\bdans\b|\+).*",
        "",
        name,
        flags=re.IGNORECASE,
    )

    # Nettoyage final des prépositions et espaces
    name = re.sub(r"^[dD]['’]\s*", "", name).strip()

    return Ingredient(
        name=name,
        quantity=qty,
        unit=unit,
    )


def clean_time(raw_time: str) -> int:
    """Nettoie une chaîne de durée brute et retourne la durée en minutes."""
    match = re.search(r"PT(\d+)M", raw_time)
    return int(match.group(1))


def raw_json_to_recipe(filepath: str) -> Recipe:
    """Convertit un fichier JSON brut en objet Recipe."""
    with open(filepath, "r", encoding="utf-8") as f:
        raw_recipe = json.load(f)

    servings = clean_servings(raw_recipe.get("recipeYield"))

    ingredients = [clean_ingredient(raw) for raw in raw_recipe.get("recipeIngredient")]

    instructions = [step.get("text") for step in raw_recipe.get("recipeInstructions")]

    return Recipe(
        id=int(re.search(r"recipe_(\d+)", filepath).group(1)),
        title=raw_recipe.get("name"),
        prep_time=clean_time(raw_recipe.get("prepTime")),
        cook_time=clean_time(raw_recipe.get("cookTime")),
        total_time=clean_time(raw_recipe.get("totalTime")),
        servings=servings,
        ingredients=ingredients,
        instructions=instructions,
    )
