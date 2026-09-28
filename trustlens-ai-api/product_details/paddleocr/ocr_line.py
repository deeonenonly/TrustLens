class OCRLine:

    def __init__(
        self,
        id,
        text,
        confidence,
        bounding_box
    ):
        self.id = id
        self.text = text
        self.confidence = confidence
        self.bounding_box = bounding_box