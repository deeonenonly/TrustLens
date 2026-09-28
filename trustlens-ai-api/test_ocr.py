from product_details.paddleocr.ocr_engine import OCREngine
from product_details.paddleocr.ocr_processor import OCRProcessor


IMAGE_PATH = "samples/images/test_007.jpg"


print("=" * 60)
print("TRUSTLENS OCR TEST")
print("=" * 60)

print("\nLoading PaddleOCR...")

ocr_engine = OCREngine()
ocr_processor = OCRProcessor()

print("PaddleOCR loaded successfully.")

print("\nRunning OCR...")

raw_result = ocr_engine.extract(IMAGE_PATH)

processed_lines, ocr_words = ocr_processor.process(
    raw_result
)

print(f"\nOCR words detected: {len(ocr_words)}")
print(f"OCR lines detected: {len(processed_lines)}")

print("\n" + "=" * 60)
print("OCR WORDS")
print("=" * 60)

for word in ocr_words:
    print(
        f"{word.id:3d}  "
        f"{word.text!r:30} "
        f"line={word.line_id:3d} "
        f"box={word.bounding_box}"
    )

print("\n" + "=" * 60)
print("OCR TEST COMPLETE")
print("=" * 60)