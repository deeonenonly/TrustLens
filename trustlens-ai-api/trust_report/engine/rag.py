import json
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings


BASE_DIR = Path(__file__).resolve().parent
PRODUCTS_FILE = BASE_DIR / "products.json"

with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
    DATA = json.load(f)


if isinstance(DATA, list):
    INGREDIENTS = DATA

elif isinstance(DATA, dict):
    INGREDIENTS = DATA.get("ingredients", [])

else:
    INGREDIENTS = []


def normalize(text):

    if not isinstance(text, str):
        return ""

    return text.strip().lower()


def load_store():

    
    valid_ingredients = [
        ingredient
        for ingredient in INGREDIENTS
        if isinstance(ingredient, dict)
    ]

    texts = [
        json.dumps(
            ingredient,
            ensure_ascii=False
        )
        for ingredient in valid_ingredients
    ]

    embeddings = OllamaEmbeddings(
        model="nomic-embed-text"
    )

    return FAISS.from_texts(
        texts,
        embeddings
    )


def find_ingredient(ingredient_name):

    name = normalize(ingredient_name)

    for ingredient in INGREDIENTS:

        
        if not isinstance(ingredient, dict):
            continue

        
        if normalize(
            ingredient.get("ingredient_name", "")
        ) == name:

            return ingredient

        
        aliases = ingredient.get(
            "aliases",
            []
        )

        
        if not isinstance(aliases, list):
            continue

        for alias in aliases:

            if normalize(alias) == name:

                return ingredient

    return None


def retrieve(store, ingredients_input):

    results = []

    unknown_ingredients = []

    for ingredient_name in ingredients_input:

        ingredient_name = ingredient_name.strip()

        if not ingredient_name:
            continue

        match = find_ingredient(
            ingredient_name
        )

        if match:

            results.append({

                "input_ingredient": ingredient_name,

                "database_match": match

            })

        else:

            unknown_ingredients.append(
                ingredient_name
            )

    return json.dumps(
        {

            "matched_ingredients": results,

            "unknown_ingredients": unknown_ingredients

        },

        indent=2,

        ensure_ascii=False
    )