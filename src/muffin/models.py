from typing import List, Optional

from sqlalchemy import Float, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    sessionmaker,
)

from muffin.recipe import Ingredient, Recipe, Servings, ServingUnit

engine = create_engine("sqlite:///recipes.db", echo=True)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


# 2. Modèles de données (Tables)
class RecipeModel(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    prep_time: Mapped[int] = mapped_column(Integer)
    cook_time: Mapped[int] = mapped_column(Integer)
    total_time: Mapped[int] = mapped_column(Integer)

    # Relations
    servings: Mapped["ServingsModel"] = relationship(
        back_populates="recipe", cascade="all, delete-orphan"
    )

    ingredients: Mapped[List["IngredientModel"]] = relationship(
        back_populates="recipe", cascade="all, delete-orphan"
    )
    instructions: Mapped[List["InstructionModel"]] = relationship(
        back_populates="recipe", cascade="all, delete-orphan"
    )


class ServingsModel(Base):
    __tablename__ = "servings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"))
    quantity: Mapped[int] = mapped_column(Integer)
    unit: Mapped[str] = mapped_column(String(50))

    recipe: Mapped["RecipeModel"] = relationship(back_populates="servings")


class IngredientModel(Base):
    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"))
    name: Mapped[str] = mapped_column(String(255))
    quantity: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    recipe: Mapped["RecipeModel"] = relationship(back_populates="ingredients")


class InstructionModel(Base):
    __tablename__ = "instructions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"))
    text: Mapped[str] = mapped_column(String)
    order: Mapped[int] = mapped_column(Integer)

    recipe: Mapped["RecipeModel"] = relationship(back_populates="instructions")


def setup_database() -> None:
    Base.metadata.create_all(engine)


def save_recipe(recipe_data: any) -> None:
    """
    Prend un objet Recipe (dataclass) et l'enregistre en base de données.
    """
    with SessionLocal() as session:
        # Création de l'objet principal
        new_recipe = RecipeModel(
            id=recipe_data.id,
            title=recipe_data.title,
            prep_time=recipe_data.prep_time,
            cook_time=recipe_data.cook_time,
            total_time=recipe_data.total_time,
        )

        # Ajout des portions
        new_recipe.servings = ServingsModel(
            quantity=recipe_data.servings.quantity,
            unit=recipe_data.servings.unit,
        )

        # Ajout des ingrédients
        for ingredient in recipe_data.ingredients:
            new_recipe.ingredients.append(
                IngredientModel(
                    name=ingredient.name,
                    quantity=ingredient.quantity,
                    unit=ingredient.unit,
                )
            )

        # Ajout des instructions
        for index, text in enumerate(recipe_data.instructions):
            new_recipe.instructions.append(InstructionModel(text=text, order=index))

        session.add(new_recipe)
        session.commit()


def get_recipe_by_id(recipe_id: int) -> Recipe | None:
    """
    Récupère une recette en base et la convertit en dataclass Recipe.
    """
    with SessionLocal() as session:
        db_recipe = session.get(RecipeModel, recipe_id)

        if not db_recipe:
            return None

        servings = Servings(
            quantity=db_recipe.servings.quantity,
            unit=ServingUnit(db_recipe.servings.unit),
        )

        ingredients_list = [
            Ingredient(name=ing.name, quantity=ing.quantity, unit=ing.unit)
            for ing in db_recipe.ingredients
        ]

        instructions_sorted = sorted(db_recipe.instructions, key=lambda x: x.order)
        instructions_list = [ins.text for ins in instructions_sorted]

        return Recipe(
            id=db_recipe.id,
            title=db_recipe.title,
            prep_time=db_recipe.prep_time,
            cook_time=db_recipe.cook_time,
            total_time=db_recipe.total_time,
            servings=servings,
            ingredients=ingredients_list,
            instructions=instructions_list,
        )
