from typing import Optional
# from pydantic import BaseModel
from pydantic import BaseModel, HttpUrl

class OCRRequest(BaseModel):
    image_url: HttpUrl

class OCRResponse(BaseModel):
    text: Optional[str]
    language: Optional[str]
    confidence: Optional[float]
