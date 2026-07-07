import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    def __init__(self):
        self.AZURE_OCR_ENDPOINT = os.getenv("AZURE_OCR_ENDPOINT")
        self.AZURE_OCR_KEY = os.getenv("AZURE_OCR_KEY")
        self.AZURE_OCR_TIMEOUT = int(os.getenv("AZURE_OCR_TIMEOUT", 30))
        self.AZURE_OCR_MAX_POLLS = int(os.getenv("AZURE_OCR_MAX_POLLS", 60))
        self.AZURE_OCR_POLL_SECONDS = float(os.getenv("AZURE_OCR_POLL_SECONDS", 1))
        self.ARABIC_CONFIDENCE_THRESHOLD = float(
            os.getenv("ARABIC_CONFIDENCE_THRESHOLD", 0.7)
        )

        self.SCORE_WEIGHT = 0.7
        self.AREA_WEIGHT = 0.3

        if not self.AZURE_OCR_ENDPOINT:
            raise ValueError("AZURE_OCR_ENDPOINT not found in .env")

        if not self.AZURE_OCR_KEY:
            raise ValueError("AZURE_OCR_KEY not found in .env")


settings = Settings()
