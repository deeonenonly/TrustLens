class OCRWord:

    def __init__(
        self,
        id,
        text,
        bounding_box,
        line_id
    ):
        self.id = id
        self.text = text
        self.bounding_box = bounding_box
        self.line_id = line_id
