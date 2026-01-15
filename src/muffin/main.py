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
    # 1. Liste des unités avec gestion des priorités (les plus longues d'abord)
    # On ajoute \b pour éviter de tronquer les mots commençant par ces lettres
    units = [
        r"cuillères? à soupe",
        r"cuillères? à café",
        r"cuillères?",
        r"gousses?",
        r"sachets?",
        r"pincées?",
        r"tasses?",
        r"tablettes?",
        r"tranches?",
        r"boîtes?",
        r"pots?",
        r"briques?",
        r"bouquets?",
        r"cl",
        r"ml",
        r"kg",
        r"dl",
        r"\bg\b",
        r"\bl\b",  # \b protège le 'g' et le 'l' isolés
    ]

    # Utilisation de \b autour de l'unité pour ne pas mordre sur le nom
    units_pattern = r"|".join(units)

    # Regex améliorée
    regex = rf"^(?P<qty>\d+[\s\./]\d+|\d+(?:[\.,]\d+)?)?\s*(?P<unit>\b(?:{units_pattern})\b)?\s*(?:de\s+|d['’]\s*)?(?P<name>.*)"

    try:
        with (
            open(input_file, "r", encoding="utf-8") as f_in,
            open(output_file, "w", encoding="utf-8") as f_out,
        ):
            for line in f_in:
                # Suppression des balises de source
                clean_line = re.sub(r"\[cite:[^\]]*\]", "", line).strip()
                if not clean_line:
                    continue

                match = re.match(regex, clean_line, re.IGNORECASE)
                if match:
                    qty = match.group("qty") or "N/A"
                    unit = match.group("unit") or "unité(s)"
                    name = match.group("name").strip()

                    # Nettoyage final du nom (suppression des parenthèses ou restes de prépositions)
                    name = re.sub(r"^[dD]['’]\s*", "", name)

                    f_out.write(f"QTY: {qty} | UNIT: {unit} | NAME: {name}\n")

    except FileNotFoundError:
        print(f"Erreur : Le fichier '{input_file}' est introuvable.")

    print("Sucess !")


if __name__ == "__main__":
    parse_and_save()
