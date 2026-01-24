import logging

import chromadb
import ollama

from muffin.constant import CHROMADB_PATH, COLLECTION_NAME, LOGGING_LEVEL
from muffin.models import (
    RecipeModel,
    SentenceTransformerEmbeddingFunction,
    SessionLocal,
    convert_model_to_dataclass,
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=LOGGING_LEVEL)

logger.info("⏳ Chargement de l'espace latent depuis ChromaDB...")
client = chromadb.PersistentClient(path=CHROMADB_PATH)
collection = client.get_collection(
    name=COLLECTION_NAME,
    embedding_function=SentenceTransformerEmbeddingFunction(),
)


def final_prompt(user_prompt: str, str_recipe: str) -> str:
    """
    Génère une réponse structurée et détaillée en utilisant le modèle Mistral.

    Args:
        user_prompt: La question ou les ingrédients de l'utilisateur.
        str_recipe: La chaîne de caractères contenant les données de la recette (contexte).

    Returns:
        str: La réponse formatée du Chef Muffin.
    """
    # Le message système définit le comportement de l'IA avec des contraintes de structure
    system_prompt: str = """
    TU ES "MC MUFFIN". UN ASSISTANT CULINAIRE QUI PRÉSENTE DES RECETTES DE MUFFINS EN RAPPANT.

    ### TES DIRECTIVES (GUARDRAILS) :
    1. LE DOGME DU MUFFIN : Tu ne cuisines QUE des muffins. Si on te demande N'IMPORTE QUEL AUTRE PLAT, remballe l'idée avec une punchline qui met fin à la conversation. 
    Par exemple :  'Ici, c'est le temple du petit gâteau rond, rien d'autre.'
    2. LANGAGE : Réponds en français, mais fais en sorte que ça rappe ! Utilise des rimes, des assonances, et un vocabulaire urbain/gastronomique (flow, fourneau, pépite, platine, etc.). 
    3. PAS DE GASPILLAGE : Tu DOIS lister TOUS les ingrédients et leurs QUANTITÉS exactes.
    4. STRUCTURE DU MORCEAU (OBLIGATOIRE) :
    - **TITRE** : Reprend le titre de la recette et essaye de le rendre RAP.
    - **INGRÉDIENTS** : Commence par le nombre de personnes ou muffins et le temps de préparation puis une liste à puces avec les dosages précis. Tu peux mettre des punchlines après les ingrédients.
    - **PRÉPARATION** : Les étapes numérotées. Utilise plein de rimes et écrit comme un texte de RAP.
    - **L'OUTRO** : Une astuce de chef légendaire ou une dédicace gourmande pour finir en beauté. 
    Salue ton audience en partant, par exemple : "PEACE, c'était MC MUFFIN le king !"
    """

    # ### INTERDICTION :
    # - Pas de résumé bâclé : on veut le morceau complet, pas un teaser.
    # - N'invente pas d'étapes : reste fidèle au texte source (le sample d'origine).
    # """

    augmented_prompt: str = f"""
    CONTEXTE (Données brutes de la recette) :
    {str_recipe}

    QUESTION DE L'UTILISATEUR :
    {user_prompt}
    
    INSTRUCTION : Produis la recette complète en respectant la structure imposée.
    """

    response = ollama.chat(
        model="mistral",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": augmented_prompt},
        ],
    )

    return str(response["message"]["content"])


def main(user_prompt: str) -> str:
    results = collection.query(query_texts=[user_prompt], n_results=1)
    with SessionLocal() as session:
        logger.info("⏳ Chargement de la recette depuis SQLite...")
        recipe_model = (
            session.query(RecipeModel).filter_by(id=int(results["ids"][0][0])).one()
        )
        recipe = convert_model_to_dataclass(recipe_model)
        logger.info(f"Found recipe : {recipe.title} with id {recipe.id}")
    return final_prompt(user_prompt, str(recipe))
