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
    # 1. Définition des motifs pour le parsing
    # Liste enrichie basée sur les spécificités de votre fichier (ex: pots, sachets, tasses)
    units = [
        r"cuillères? à soupe",
        r"cuillères? à café",
        r"cuillères?",
        r"g",
        r"cl",
        r"ml",
        r"l",
        r"kg",
        r"pots?",
        r"sachets?",
        r"gousses?",
        r"pincées?",
        r"tasses?",
        r"tablettes?",
        r"briques?",
        r"bouquets?",
        r"tranches?",
        r"boîtes?",
        r"morceaux?",
        r"carrés?",
    ]

    units_pattern = "|".join(units)
    # Regex capturant : Quantité (Optionnelle), Unité (Optionnelle), et Nom
    regex = rf"^(?P<qty>\d+[\s\./]\d+|\d+)?\s*(?P<unit>{units_pattern})?\s*(?:de\s+|d['’]\s*)?(?P<name>.*)"

    try:
        with (
            open(input_file, "r", encoding="utf-8") as f_in,
            open(output_file, "w", encoding="utf-8") as f_out,
        ):
            for line in f_in:
                # Nettoyage : suppression des balises [cite: 1, 15, 115]
                clean_line = re.sub(r"\[cite:[^\]]*\]", "", line).strip()

                # Ignorer les lignes vides
                if not clean_line:
                    continue

                # Application de la Regex
                match = re.match(regex, clean_line, re.IGNORECASE)
                if match:
                    qty = match.group("qty") or "N/A"
                    unit = match.group("unit") or "unité(s)"
                    name = match.group("name").strip()

                    # Formatage de la ligne de sortie
                    output_line = f"QTY: {qty} | UNIT: {unit} | NAME: {name}\n"
                    f_out.write(output_line)

        print(f"Succès ! Le fichier '{output_file}' a été généré.")

    except FileNotFoundError:
        print(f"Erreur : Le fichier '{input_file}' est introuvable.")


if __name__ == "__main__":
    parse_and_save()
