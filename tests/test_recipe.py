from dataclasses import asdict

import pytest

from muffin.recipe import (
    ServingUnit,
    clean_ingredient,
    clean_servings,
    clean_time,
    raw_json_to_recipe,
)


@pytest.mark.parametrize(
    "raw, expected",
    [
        # Capture basique quantity + UNIT + NAME
        ("200 g de farine", {"quantity": 200, "unit": "g", "name": "farine"}),
        # Unités complexes (cuillères)
        (
            "2 belles cuillères à soupe de miel",
            {"quantity": 2, "unit": "belles cuillères à soupe", "name": "miel"},
        ),
        # Fractions
        (
            "1/2 sachet de levure",
            {"quantity": 0.5, "unit": "sachet", "name": "levure"},
        ),
        # Nettoyage apostrophe (d')
        ("2 gousses d'ail", {"quantity": 2, "unit": "gousses", "name": "ail"}),
        # Cas sans quantité ni unité
        ("Sucre glace", {"quantity": None, "unit": None, "name": "Sucre glace"}),
        # Élimination des parenthèses
        (
            "500 g de tomates (bio et mûres)",
            {"quantity": 500, "unit": "g", "name": "tomates"},
        ),
        # Élimination des points de suspension
        ("1 pincée de sel...", {"quantity": 1, "unit": "pincée", "name": "sel"}),
        # Coupure à "et"
        ("3 pommes et 2 poires", {"quantity": 3, "unit": None, "name": "pommes"}),
        # Coupure à "+"
        (
            "100 g de sucre + un peu pour le moule",
            {"quantity": 100, "unit": "g", "name": "sucre"},
        ),
        # Coupure à "ou"
        (
            "2 oeufs ou un substitut d'œuf",
            {"quantity": 2, "unit": None, "name": "oeufs"},
        ),
        # Coupure avec "pour"
        (
            "500 g de farine pour la pâte",
            {"quantity": 500, "unit": "g", "name": "farine"},
        ),
    ],
)
def test_clean_ingredient(raw, expected):
    result = clean_ingredient(raw)
    assert asdict(result) == expected


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("3 gros brioches", {"quantity": 3, "unit": ServingUnit.pieces}),
        (
            "1 belles portion",
            {"quantity": 1, "unit": ServingUnit.persons},
        ),
    ],
)
def test_clean_servings(raw, expected):
    result = clean_servings(raw)
    assert asdict(result) == expected


def test_clean_time():
    result = clean_time("PT42M")
    assert result == 42


def test_raw_json_to_recipe():
    recipe = raw_json_to_recipe("data/raw_recipes/recipe_10620.json")
    expected = {
        "id": 10620,
        "title": "Muffins myrtilles au coeur frais",
        "prep_time": 10,
        "cook_time": 25,
        "total_time": 35,
        "servings": {"quantity": 4, "unit": ServingUnit.persons},
        "ingredients": [
            {"name": "farine", "quantity": 180.0, "unit": "g"},
            {"name": "sucre cristallisé", "quantity": 200.0, "unit": "g"},
            {"name": "sel", "quantity": 0.5, "unit": "cuillères à café"},
            {"name": "levure", "quantity": 2.0, "unit": "cuillères à café"},
            {"name": "zeste de citron", "quantity": None, "unit": None},
            {"name": "oeufs", "quantity": 1.0, "unit": None},
            {"name": "yaourt", "quantity": 20.0, "unit": "cl"},
            {"name": "frais", "quantity": 2.0, "unit": "carré"},
            {"name": "huile", "quantity": 6.0, "unit": "cl"},
            {"name": "myrtilles congelées", "quantity": 150.0, "unit": "g"},
            {"name": "noix de pécan hachées", "quantity": 25.0, "unit": "g"},
        ],
        "instructions": [
            "Préchauffer le four à 190°C. Utiliser des moules à muffin en siliconne.",
            "Bien mélanger les ingrédients suivants dans 2 récipients séparés :",
            "Mélange 1 : farine, levure, bicarbonate, sel, sucre, zeste de citron et noix de pécan",
            "Mélange 2 : oeuf, yaourt, carrés frais, huile.",
            "Faire un puit dans le mélange 1 et y introduire le mélange 2. Homogénéiser légèrement et rapidement, mais surtout, ne pas trop battre la pâte, elle doit avoir un aspect grumeleux. Ajouter les myrtilles.",
            "A l'aide d'une cuillère, remplir les moules de pâte au 2/3 et faire cuire 20 à 25 minutes.",
            "Laisser refroidir 10 minutes puis démouler sur une grille.",
            "Déguster !",
        ],
    }
    assert asdict(recipe) == expected
