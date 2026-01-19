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


def final_prompt(user_prompt: str, str_recipe: str) -> str:
    # Le message système définit le comportement de l'IA
    system_prompt = """
    TU ES "CHEF MUFFIN", UN ASSISTANT CULINAIRE OBSESSIONNEL MAIS SYMPATHIQUE.
    TON OBJECTIF EST DE TROUVER LA RECETTE DE MUFFIN IDÉALE PARMI LE CONTEXTE FOURNI.

    ### TES DIRECTIVES (GUARDRAILS) :
    1. OBSESSION : Tu ne cuisines QUE des muffins. Si on te demande des lasagnes ou une pizza, REFUSE poliment avec humour.
    2. ANCRAGE : Utilise UNIQUEMENT les recettes fournies dans le bloc [CONTEXTE]. N'invente rien. Détaille la préparation en utilisant toutes les instructions et ingrédients fournies dans la recette.
    3. LANGUE : Réponds toujours en français courant et appétissant.
    """

    augmented_prompt = f"""
    CONTEXTE (La recette trouvée) :
    {str_recipe}

    QUESTION DE L'UTILISATEUR :
    {user_prompt}
    """

    response = ollama.chat(
        model="mistral",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": augmented_prompt},
        ],
    )

    return response["message"]["content"]


# # --- Exemple d'utilisation ---
# ma_recette_db = (
#     "Muffins au cacao : 200g farine, 50g cacao, 2 oeufs. Cuire 20min à 180°C."
# )
# ma_question = "J'ai du cacao et de la farine, qu'est-ce que je peux faire ?"

# reponse_finale = synthetiser_reponse(ma_question, ma_recette_db)
# print(reponse_finale)


def main():
    client = chromadb.PersistentClient(path=CHROMADB_PATH)

    collection = client.get_collection(
        name=COLLECTION_NAME,
        embedding_function=SentenceTransformerEmbeddingFunction(),
    )

    user_prompt = input(
        "😎Dis moi ce qu'il y a dans ton frigo, je te dirai quel muffin cuisiner.🤪 \n👉"
    )
    results = collection.query(query_texts=[user_prompt], n_results=1)
    with SessionLocal() as session:
        logger.info("⏳ Chargement de la recette depuis SQLite...")
        recipe_model = (
            session.query(RecipeModel).filter_by(id=int(results["ids"][0][0])).one()
        )
        recipe = convert_model_to_dataclass(recipe_model)
    chief_answer = final_prompt(user_prompt, str(recipe))
    print(chief_answer)


if __name__ == "__main__":
    main()
