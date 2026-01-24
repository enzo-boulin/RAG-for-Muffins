import unicodedata


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


def normalize_text(text: str) -> str:
    """Supprime les accents et convertit en minuscules."""
    text = text.lower()
    text = "".join(
        c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn"
    )
    return text
