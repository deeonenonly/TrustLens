from fastapi import APIRouter, UploadFile, File
from pathlib import Path
import shutil
import re
import tempfile
from urllib.parse import urlparse, parse_qs
from urllib.request import Request, urlopen

from pipeline.trustlens_pipeline import TrustLensPipeline




router = APIRouter()

trustlens_pipeline = TrustLensPipeline()

@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/api/v1/analyze")
async def analyze(file: UploadFile = File(...)):

    upload_dir = Path("samples/images")
    upload_dir.mkdir(parents=True, exist_ok=True)

    image_path = upload_dir / file.filename

    with image_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = product_details_wrapper.extract(
        image_path=str(image_path),
        product_name=None
    )

    return {
        "productDetails": {
            "productName": result.product_name,
            "status": result.status,
            "errorMessage": result.error_message,
            "ingredients": result.ingredients
        },
        "trustReport": None
    }

def get_google_drive_download_url(image_url):
    parsed = urlparse(image_url)

    if "drive.google.com" not in parsed.netloc:
        return image_url

    file_id = None

    match = re.search(
        r"/file/d/([^/]+)",
        parsed.path
    )

    if match:
        file_id = match.group(1)

    if not file_id:
        query = parse_qs(parsed.query)
        file_id = query.get("id", [None])[0]

    if not file_id:
        raise ValueError(
            "Invalid Google Drive image URL."
        )

    return (
        "https://drive.google.com/uc"
        f"?export=download&id={file_id}"
    )


def download_image(image_url):
    download_url = get_google_drive_download_url(
        image_url
    )

    request = Request(
        download_url,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    with urlopen(request) as response:

        image_bytes = response.read()

    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".jpg"
    )

    temp_file.write(image_bytes)
    temp_file.close()

    return temp_file.name


@router.post("/api/v1/analyze-url")
async def analyze_url(image_url: str):

    image_path = None

    try:

        image_path = download_image(
            image_url
        )

        result = trustlens_pipeline.analyze(
            image_path=image_path,
            product_name=None
        )

        return result

    finally:

        if image_path:

            Path(image_path).unlink(
                missing_ok=True
            )