import re


def clean_ingredient(ingredient):
    ingredient = re.sub(r"\s+", " ", ingredient)
    ingredient = ingredient.strip()

    ingredient = re.sub(r"\s+([,;])", r"\1", ingredient)
    ingredient = re.sub(r"([(\[])\s+", r"\1", ingredient)

    return ingredient


def postprocess_ingredients(ingredients):
    cleaned = []

    for ingredient in ingredients:
        ingredient = clean_ingredient(ingredient)

        if ingredient:
            cleaned.append(ingredient)
    return cleaned

    return cleaned