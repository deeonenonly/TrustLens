from product_details.layoutlmv3.ingredient_extractor import IngredientExtractor


IMAGE_PATH = "samples/images/test_001.jpg"


print("=" * 60)
print("TRUSTLENS LAYOUTLMV3 TEST")
print("=" * 60)

print("\nLoading Ingredient Extractor...")

extractor = IngredientExtractor()

print("Ingredient Extractor loaded successfully.")

print("\nRunning ingredient extraction...")

ingredients = extractor.extract(IMAGE_PATH)

print("\n" + "=" * 60)
print("EXTRACTED INGREDIENTS")
print("=" * 60)

for i, ingredient in enumerate(ingredients, start=1):
    print(f"{i:3d}. {ingredient}")

print("\n" + "=" * 60)
print(f"Total ingredients: {len(ingredients)}")
print("=" * 60)