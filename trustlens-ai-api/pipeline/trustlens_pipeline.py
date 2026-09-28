from product_details.wrapper.product_details_wrapper import ProductDetailsWrapper
from trust_report.wrapper.trust_report_wrapper import TrustReportWrapper


class TrustLensPipeline:

    def __init__(self):
        self.product_details_wrapper = ProductDetailsWrapper()
        self.trust_report_wrapper = TrustReportWrapper()

    def analyze(self, image_path, product_name=None):

        product_result = self.product_details_wrapper.extract(
            image_path=image_path,
            product_name=product_name
        )

        if product_result.status != 1:
            return {
                "productDetails": {
                    "productName": product_result.product_name,
                    "status": product_result.status,
                    "errorMessage": product_result.error_message,
                    "ingredients": product_result.ingredients
                },
                "trustReport": None
            }

        trust_report = self.trust_report_wrapper.generate(
            product_result.ingredients
        )

        return {
            "productDetails": {
                "productName": product_result.product_name,
                "status": product_result.status,
                "errorMessage": product_result.error_message,
                "ingredients": product_result.ingredients
            },
            "trustReport": trust_report.to_dict()
        }