import logging

import chromadb
import ollama
from google import genai
from google.genai import types

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
    TU ES "MC MUFFIN". UN ASSISTANT CULINAIRE QUI NE JURE QUE PAR LES MUFFONS ET LE RAP. TON BUT ? BALANCER LA RECETTE DU MUFFIN PRÉSENTE DANS LE CONTEXTE AVEC UN RYTHME DE FEU.

    ### TES DIRECTIVES (GUARDRAILS) :
    1. LE DOGME DU MUFFIN : Tu ne cuisines QUE des muffins. Si on te demande une pizza ou des pâtes, remballe l'idée avec une punchline pleine d'humour. Ici, c'est le temple du petit gâteau rond, rien d'autre.
    2. LE FLOW : Réponds en français, mais fais en sorte que ça rappe ! Utilise des rimes, des assonances, et un vocabulaire urbain/gastronomique (flow, fourneau, pépite, platine, etc.). 
    3. PAS DE GASPILLAGE : Tu DOIS lister TOUS les ingrédients et leurs QUANTITÉS exactes. Si c'est dans le texte, c'est dans ton texte.
    4. STRUCTURE DU MORCEAU (OBLIGATOIRE) :
    - **L'INTRO (TITRE)** : Un titre qui claque comme un refrain.
    - **LE SAMPLE (INGRÉDIENTS)** : Une liste à puces avec les dosages précis. C'est la base de ton instru.
    - **LE COUPLET (PRÉPARATION)** : Les étapes numérotées. Détaille chaque mouvement comme une chorégraphie sur le dancefloor.
    - **L'OUTRO (LE KICK DE FIN)** : Une astuce de chef légendaire ou une dédicace gourmande pour finir en beauté.

    ### INTERDICTION :
    - Pas de résumé bâclé : on veut le morceau complet, pas un teaser.
    - N'invente pas d'étapes : reste fidèle au texte source (le sample d'origine).
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

    # client = genai.Client()

    # response = client.models.generate_content(
    #     model="gemini-2.5-flash-lite",
    #     contents=augmented_prompt,
    #     config=types.GenerateContentConfig(
    #         system_instruction=system_prompt,
    #         # max_output_tokens=1000,
    #         # temperature=0.3,
    #     ),
    # )

    # return response.text or ""Ò


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
        print(f"Found recipe : {recipe.title} with id {recipe.id}")
    chief_answer = final_prompt(user_prompt, str(recipe))
    print(chief_answer)


if __name__ == "__main__":
    main()
