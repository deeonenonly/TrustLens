from trust_report.engine.report_generator import generate_report
from trust_report.wrapper.dto import TrustReportResult


class TrustReportWrapper:

    def generate(self, ingredients):

        ingredient_string = ", ".join(
            ingredient.strip()
            for ingredient in ingredients
            if ingredient.strip()
        )

        report = generate_report(ingredient_string)

        return TrustReportResult(
            report=report
        )