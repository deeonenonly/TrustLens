from product_details.layoutlmv3.ingredient_extractor import IngredientExtractor
from product_details.wrapper.dto import ProductDetailsResult

from product_details.utils.normalizer import normalize_ingredients
from product_details.utils.ingredient_postprocessor import postprocess_ingredients


class ProductDetailsWrapper:

    def __init__(self):
        self.extractor = IngredientExtractor()

    def extract(self, image_path, product_name=None):

        try:
            ingredients = self.extractor.extract(image_path)
            ingredients = normalize_ingredients(ingredients)
            ingredients = postprocess_ingredients(ingredients)

            return ProductDetailsResult(
                product_name=product_name,
                status=1,
                error_message=None,
                ingredients=ingredients
            )

        except Exception as e:

            return ProductDetailsResult(
                product_name=product_name,
                status=0,
                error_message=str(e),
                ingredients=[]
            )