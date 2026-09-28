from pathlib import Path
import re

import torch
from PIL import Image
from transformers import (
    LayoutLMv3Processor,
    LayoutLMv3ForTokenClassification
)

from product_details.paddleocr.ocr_engine import OCREngine
from product_details.paddleocr.ocr_processor import OCRProcessor


MODEL_PATH = "models/layoutlmv3_ingredient"

LABEL_NAMES = {
    0: "O",
    1: "B-INGREDIENT",
    2: "I-INGREDIENT"
}


START_TERMS = {
    "ingredients",
    "ingredient",
    "ingredientes"
}


START_OF_LINE_STOPS = (
    "allergen",
    "allergy",
    "nutrition information",
    "nutritional information",
    "nutrition facts",
    "storage conditions",
    "directions for use",
    "best before",
    "manufactured",
    "mfg by",
    "mfd",
    "made in",
    "net wt",
    "net contents",
    "customer care",
    "toll free",
    "mrp",
    "batch no",
    "art no",
    "lic no",
    "www",
    "levercare",
    "pareve",
    "contains",
    "not to be consumed",
    "do not refrigerate",
    "product of"
)


WITHIN_LINE_STOPS = (
    "allergen advice",
    "allergen",
    "allergy",
    "nutrition information",
    "nutritional information",
    "nutrition facts",
    "storage conditions",
    "directions for use",
    "best before",
    "manufactured",
    "mfg by",
    "mfd",
    "made in",
    "net wt",
    "net contents",
    "customer care",
    "toll free",
    "mrp",
    "batch no",
    "art no",
    "lic no",
    "www",
    "levercare",
    "pareve",
    "contains added flavour",
    "contains permitted synthetic",
    "contains wheat ingredients",
    "contains sesame",
    "not to be consumed",
    "do not refrigerate",
    "product of",
    "food additives are",
    "not suitable for",
    "excessive use can"
)


def normalize_for_matching(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalized_word(text):
    text = text.lower()
    return re.sub(r"[^a-z0-9]+", "", text)


def is_start_line(text):
    normalized = normalize_for_matching(text)

    return any(
        normalized.startswith(term)
        for term in START_TERMS
    )


def is_quantity_only(text):
    normalized = normalize_for_matching(text)

    return bool(
        re.fullmatch(
            r"\d+(?:\.\d+)?\s*"
            r"(ml|mle|l|g|kg|mg|oz|cl)",
            normalized
        )
    )


def find_stop_word_index(line_words):

    normalized_words = [
        normalized_word(word.text)
        for word in line_words
    ]

    normalized_words = [
        word
        for word in normalized_words
    ]

    # First check for strong multi-word markers.
    for marker in WITHIN_LINE_STOPS:

        marker_words = [
            normalized_word(part)
            for part in marker.split()
        ]

        marker_words = [
            word
            for word in marker_words
            if word
        ]

        if not marker_words:
            continue

        for index in range(
            len(normalized_words)
            - len(marker_words)
            + 1
        ):

            if normalized_words[
                index:index + len(marker_words)
            ] == marker_words:

                return index

    # Generic "contains" is only a stop when it is the
    # first meaningful word of a new line.
    if normalized_words:

        if normalized_words[0] == "contains":
            return 0

    return None


class IngredientExtractor:

    def __init__(self):

        self.device = torch.device(
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        self.ocr_engine = OCREngine()
        self.ocr_processor = OCRProcessor()

        self.processor = (
            LayoutLMv3Processor.from_pretrained(
                MODEL_PATH,
                apply_ocr=False
            )
        )

        self.model = (
            LayoutLMv3ForTokenClassification
            .from_pretrained(MODEL_PATH)
        )

        self.model.to(self.device)
        self.model.eval()


    def normalize_box(
        self,
        box,
        width,
        height
    ):

        x1, y1, x2, y2 = box

        return [
            max(
                0,
                min(
                    1000,
                    int(x1 * 1000 / width)
                )
            ),
            max(
                0,
                min(
                    1000,
                    int(y1 * 1000 / height)
                )
            ),
            max(
                0,
                min(
                    1000,
                    int(x2 * 1000 / width)
                )
            ),
            max(
                0,
                min(
                    1000,
                    int(y2 * 1000 / height)
                )
            )
        ]


    def get_section_word_indices(
        self,
        ocr_words
    ):

        lines = {}

        for index, word in enumerate(
            ocr_words
        ):

            lines.setdefault(
                word.line_id,
                []
            ).append(index)


        ordered_line_ids = sorted(
            lines
        )


        start_position = None

        for position, line_id in enumerate(
            ordered_line_ids
        ):

            line_words = [
                ocr_words[index]
                for index in lines[line_id]
            ]

            line_text = " ".join(
                word.text
                for word in line_words
            )

            if is_start_line(line_text):

                start_position = position
                break


        if start_position is None:
            return None


        selected_indices = []


        for position in range(
            start_position,
            len(ordered_line_ids)
        ):

            line_id = ordered_line_ids[
                position
            ]

            line_indices = lines[line_id]

            line_words = [
                ocr_words[index]
                for index in line_indices
            ]


            # A second Ingredients/Ingredientes
            # heading starts another section.
            if (
                position > start_position
                and is_start_line(
                    " ".join(
                        word.text
                        for word in line_words
                    )
                )
            ):

                break


            # Stop at a new section.
            stop_index = find_stop_word_index(
                line_words
            )


            if stop_index == 0:

                break


            # Keep only words before an
            # in-line stop marker.
            if stop_index is not None:

                selected_indices.extend(
                    line_indices[:stop_index]
                )

                break


            # Skip standalone package quantities.
            line_text = " ".join(
                word.text
                for word in line_words
            )

            if is_quantity_only(line_text):
                continue


            # Remove the Ingredients heading itself
            # and punctuation immediately following it.
            if position == start_position:

                skip_heading = True

                for index in line_indices:

                    word = ocr_words[index]

                    normalized = (
                        normalize_for_matching(
                            word.text
                        )
                    )

                    if (
                        normalized in START_TERMS
                    ):

                        continue


                    if skip_heading:

                        # Skip punctuation such as ":".
                        if not normalized:
                            continue

                        skip_heading = False


                    selected_indices.append(
                        index
                    )

            else:

                selected_indices.extend(
                    line_indices
                )


        return selected_indices


    def extract(self, image_path):

        image_path = Path(
            image_path
        )


        if not image_path.exists():

            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )


        image = Image.open(
            image_path
        ).convert("RGB")


        width, height = image.size


        raw_result = self.ocr_engine.extract(
            str(image_path)
        )


        _, ocr_words = (
            self.ocr_processor.process(
                raw_result
            )
        )


        section_indices = (
            self.get_section_word_indices(
                ocr_words
            )
        )


        if section_indices is None:

            raise ValueError(
                "Ingredients section not found."
            )


        section_words = [
            ocr_words[index]
            for index in section_indices
        ]


        words = [
            word.text
            for word in section_words
        ]


        pixel_boxes = [
            word.bounding_box
            for word in section_words
        ]


        boxes = [
            self.normalize_box(
                box,
                width,
                height
            )
            for box in pixel_boxes
        ]


        encoding = self.processor(
            image,
            words,
            boxes=boxes,
            return_tensors="pt",
            truncation=True,
            padding="max_length",
            max_length=512
        )


        input_ids = encoding[
            "input_ids"
        ].to(self.device)

        attention_mask = encoding[
            "attention_mask"
        ].to(self.device)

        bbox = encoding[
            "bbox"
        ].to(self.device)

        pixel_values = encoding[
            "pixel_values"
        ].to(self.device)


        with torch.no_grad():

            outputs = self.model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                bbox=bbox,
                pixel_values=pixel_values
            )


        predictions = torch.argmax(
            outputs.logits,
            dim=-1
        )[0]


        word_ids = encoding.word_ids(
            batch_index=0
        )


        seen_words = set()

        ingredient_words = []


        for token_index, word_id in enumerate(
            word_ids
        ):

            if word_id is None:
                continue


            if word_id in seen_words:
                continue


            seen_words.add(
                word_id
            )


            label_id = predictions[
                token_index
            ].item()


            label = LABEL_NAMES.get(
                label_id,
                "O"
            )


            word = words[word_id]


            line_id = (
                section_words[
                    word_id
                ].line_id
            )


            if label != "O":

                print(
                    word,
                    "->",
                    label,
                    "-> line",
                    line_id,
                    "-> box",
                    section_words[
                        word_id
                    ].bounding_box
                )

                ingredient_words.append(
                    (
                        word,
                        label,
                        line_id,
                        word_id
                    )
                )

        def has_delimiter_between(
                previous_index,
                current_index
        ):

            for index in range(
                    previous_index + 1,
                    current_index
            ):

                text = section_words[
                    index
                ].text.strip()

                if any(
                        delimiter in text
                        for delimiter in [",", ";", ":"]
                ):
                    return True

            previous_text = section_words[
                previous_index
            ].text.strip()

            if any(
                    delimiter in previous_text
                    for delimiter in [",", ";", ":"]
            ):
                return True

            if previous_text.endswith(
                    (")", "]")
            ):
                return True

            return False

        ingredients = []

        current = []

        for index, (
                word,
                label,
                line_id,
                word_index
        ) in enumerate(
            ingredient_words
        ):

            if label == "B-INGREDIENT":

                if current:

                    previous_word = current[-1]

                    previous_index = previous_word[3]

                    previous_line = previous_word[2]

                    same_line = (
                            line_id == previous_line
                    )

                    delimiter = (
                        has_delimiter_between(
                            previous_index,
                            word_index
                        )
                    )

                    if same_line and not delimiter:
                        current.append(
                            (
                                word,
                                label,
                                line_id,
                                word_index
                            )
                        )

                        continue

                    ingredients.append(
                        " ".join(
                            item[0]
                            for item in current
                        )
                    )

                current = [
                    (
                        word,
                        label,
                        line_id,
                        word_index
                    )
                ]

            elif label == "I-INGREDIENT":

                if current:

                    current.append(
                        (
                            word,
                            label,
                            line_id,
                            word_index
                        )
                    )

                elif index == 0:

                    current = [
                        (
                            word,
                            label,
                            line_id,
                            word_index
                        )
                    ]

        if current:
            ingredients.append(
                " ".join(
                    item[0]
                    for item in current
                )
            )
            return ingredients