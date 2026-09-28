class TrustReportResult:
    def __init__(self, report):
        self.report = report

    def to_dict(self):
        return {
            "report": self.report
        }