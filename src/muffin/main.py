import json
import os
import re


def get_all_existing_ingredients(
    filepath: str = "data/raw_recipes", save_to: str = "data/"
) -> set[str]:
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


def parse_and_save(
    input_file: str = "data/raw_ingredients.txt",
    output_file: str = "data/cleaned_ingredients.txt",
):
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

    try:
        with (
            open(input_file, "r", encoding="utf-8") as f_in,
            open(output_file, "w", encoding="utf-8") as f_out,
        ):
            for line in f_in:
                # Suppression des balises de source présentes dans raw_ingredients.txt
                clean_line = re.sub(r"\]*\]", "", line).strip()
                if not clean_line:
                    continue

                match = re.match(regex, clean_line, re.IGNORECASE)
                if match:
                    qty = match.group("qty") or "N/A"
                    unit = match.group("unit") or "unité"
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

                    f_out.write(f"QTY: {qty} | UNIT: {unit} | NAME: {name}\n")

    except FileNotFoundError:
        print(f"Erreur : Le fichier '{input_file}' est introuvable.")

    print(f"Success ! Saved to {output_file}")


if __name__ == "__main__":
    parse_and_save()
