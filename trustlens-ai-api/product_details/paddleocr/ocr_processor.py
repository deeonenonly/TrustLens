from product_details.paddleocr.ocr_line import OCRLine
from product_details.paddleocr.ocr_word import OCRWord


class OCRProcessor:

    def process(self, raw_result):

        texts = raw_result["rec_texts"]
        scores = raw_result["rec_scores"]
        boxes = raw_result["rec_boxes"]

        word_texts = raw_result["text_word"]
        word_boxes = raw_result["text_word_boxes"]

        lines = []

        for text, score, box, line_words, line_boxes in zip(
            texts,
            scores,
            boxes,
            word_texts,
            word_boxes
        ):

            line = OCRLine(
                id=-1,
                text=text.strip(),
                confidence=float(score),
                bounding_box=box.tolist()
            )

            lines.append({
                "line": line,
                "words": line_words,
                "word_boxes": line_boxes
            })

        lines.sort(
            key=lambda item: item["line"].bounding_box[1]
        )

        processed = []
        words = []
        word_id = 0

        for line_id, item in enumerate(lines):

            line = item["line"]
            line.id = line_id

            processed.append(line)

            for text, box in zip(
                item["words"],
                item["word_boxes"]
            ):

                words.append(
                    OCRWord(
                        id=word_id,
                        text=text,
                        bounding_box=box.tolist(),
                        line_id=line_id
                    )
                )

                word_id += 1

        return processed, words