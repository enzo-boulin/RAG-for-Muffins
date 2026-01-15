from dataclasses import dataclass


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
