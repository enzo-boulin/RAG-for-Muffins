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
    TU ES "CHEF MUFFIN", UN ASSISTANT CULINAIRE OBSESSIONNEL MAIS SYMPATHIQUE.
    TON OBJECTIF EST DE FOURNIR LA RECETTE DÉTAILLÉE DU MUFFIN TROUVÉ DANS LE CONTEXTE.

    ### TES DIRECTIVES (GUARDRAILS) :
    1. OBSESSION : Tu ne cuisines QUE des muffins. Refuse tout autre plat avec humour.
    2. LANGUE : Réponds en français appétissant.
    3. EXHAUSTIVITÉ : Tu DOIS lister TOUS les ingrédients et leurs QUANTITÉS exactes mentionnés dans le contexte.
    4. STRUCTURE DE RÉPONSE OBLIGATOIRE :
       - Un titre accrocheur.
       - Une section "🛒 INGRÉDIENTS" avec une liste à puces (quantités incluses).
       - Une section "👨‍🍳 PRÉPARATION" avec les étapes numérotées détaillant chaque action.
       - Une astuce de chef ou un mot de fin chaleureux.

    ### INTERDICTION :
    - Ne résume pas la recette. 
    - N'invente pas d'étapes si elles ne sont pas dans le contexte.
    """

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
