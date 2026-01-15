import re
from dataclasses import dataclass

from muffin.utils import fraction_to_float


@dataclass
class Ingredient:
    name: str
    quantity: float | None
    unit: str | None


@dataclass
class Recipe:
    title: str
    prep_time: int  # minutes
    cook_time: int  # minutes
    total_time: int  # minutes
    servings: int
    ingredients: list[Ingredient]
    instructions: list[str]


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
