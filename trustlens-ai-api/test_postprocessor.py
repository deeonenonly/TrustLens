from product_details.utils.ingredient_postprocessor import postprocess_ingredients


ingredients = [
    "Water",
    "Mixed   Fruit   Concentrate  (",
    "Appie   Juice   Conc",
    "Orange Juice conc",
    "Passion   Fruit   Juice   Conc"
]

cleaned = postprocess_ingredients(ingredients)

print(cleaned)
