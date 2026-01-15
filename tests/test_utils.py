from dataclasses import asdict

import pytest

from muffin.utils import clean_ingredient, fraction_to_float


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
def test_parsing_logic(raw, expected):
    result = clean_ingredient(raw)
    assert asdict(result) == expected


def test_fraction_to_float():
    test_cases = {
        "1/2": 0.5,
        "3/4": 0.75,
        "2": 2.0,
        "5.5": 5.5,
        "7,25": 7.25,
    }

    for input_str, expected in test_cases.items():
        result = fraction_to_float(input_str)
        assert result == expected, f"Failed for input: {input_str}"
