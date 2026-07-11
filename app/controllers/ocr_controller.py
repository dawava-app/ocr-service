import os
import tempfile
import httpx
from fastapi import APIRouter, UploadFile, File

from app.services.ocr_service import match_medicine
from app.schemas.ocr_schema import OCRResponse, OCRRequest
from app.utils.file_utils import get_temp_path, remove_file
from app.utils.image_utils import save_upload
from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.post("/ocr", response_model=OCRResponse)
async def predict(request: OCRRequest):
    suffix = os.path.splitext(str(request.image_url))[1] or ".jpg"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        temp_path = tmp.name

    try:
        # Download image
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(str(request.image_url))

        if response.status_code != 200:
            raise HTTPException(
                status_code=400,
                detail="Failed to download image."
            )

        with open(temp_path, "wb") as f:
            f.write(response.content)

        # OCR
        text, dose, lang, confidence = match_medicine(temp_path)

        return OCRResponse(
            text=text,
            dose=dose,
            language=lang,
            confidence=confidence,
        )

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
