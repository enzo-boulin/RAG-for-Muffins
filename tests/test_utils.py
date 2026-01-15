import pytest
from src.muffin.utils import clean_ingredients, fraction_to_float


# @pytest.mark.parametrize(
#     "input_line, expected",
#     [
#         # Test 1: Capture basique QTY + UNIT + NAME
#         ("200 g de farine", {"qty": "200", "unit": "g", "name": "farine"}),
#         # Test 2: Unités complexes (cuillères)
#         (
#             "2 belles cuillères à soupe de miel",
#             {"qty": "2", "unit": "belles cuillères à soupe", "name": "miel"},
#         ),
#         # Test 3: Fractions
#         ("1/2 sachet de levure", {"qty": "1/2", "unit": "sachet", "name": "levure"}),
#         # Test 4: Élimination des parenthèses
#         (
#             "500g de tomates (bio et mûres)",
#             {"qty": "500", "unit": "g", "name": "tomates"},
#         ),
#         # Test 5: Élimination des points de suspension
#         ("1 pincée de sel...", {"qty": "1", "unit": "pincée", "name": "sel"}),
#         # Test 6: Nouvelle règle (Conjonctions) - Coupure à "et"
#         ("3 pommes et 2 poires", {"qty": "3", "unit": "unité", "name": "pommes"}),
#         # Test 7: Nouvelle règle (Symboles) - Coupure à "+"
#         (
#             "100g de sucre + un peu pour le moule",
#             {"qty": "100", "unit": "g", "name": "sucre"},
#         ),
#         # Test 8: Nettoyage apostrophe (d')
#         ("2 gousses d'ail", {"qty": "2", "unit": "gousses", "name": "ail"}),
#         # Test 9: Cas sans quantité ni unité
#         ("Farine", {"qty": "N/A", "unit": "unité", "name": "Farine"}),
#     ],
# )
# def test_parsing_logic(input_line, expected):
#     result = clean_ingredients(input_line, units_pattern)
#     assert result == expected


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
