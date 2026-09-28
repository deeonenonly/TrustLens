import json
import re

from .rag import load_store, retrieve
from .llm import generate
from .analysis import calculate_overall_analysis


def extract_json(text):
    text = re.sub(r"```json", "", text, flags=re.IGNORECASE)
    text = re.sub(r"```", "", text)

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise ValueError("No JSON object found in LLM response.")

    return json.loads(text[start:end + 1])


def generate_report(ingredient_string):
    ingredients = [
        ingredient.strip()
        for ingredient in ingredient_string.split(",")
        if ingredient.strip()
    ]

    if not ingredients:
        raise ValueError("No ingredients were provided.")

    store = load_store()

    context = retrieve(
        store,
        ingredients
    )

    result = generate(context)

    data = extract_json(result)

    individual_ingredients = data.get(
        "individual_ingredients",
        []
    )

    unknown_ingredients = data.get(
        "unknown_ingredients",
        []
    )

    overall_analysis = calculate_overall_analysis(
        individual_ingredients,
        unknown_ingredients
    )

    return {
        "overall_analysis": overall_analysis,
        "individual_ingredients": individual_ingredients,
        "unknown_ingredients": unknown_ingredients
    }