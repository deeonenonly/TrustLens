class ProductDetailsResult:
    def __init__(
        self,
        product_name,
        status,
        error_message,
        ingredients
    ):
        self.product_name = product_name
        self.status = status
        self.error_message = error_message
        self.ingredients = ingredients

    def to_dict(self):
        return {
            "productName": self.product_name,
            "status": self.status,
            "errorMessage": self.error_message,
            "ingredients": self.ingredients
        }