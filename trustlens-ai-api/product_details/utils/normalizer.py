import re


def normalize_ingredient(ingredient):
    ingredient = re.sub(r"\s+", " ", ingredient)
    ingredient = ingredient.strip()

    return ingredient


def normalize_ingredients(ingredients):
    return [
        normalize_ingredient(ingredient)
        for ingredient in ingredients
    ]