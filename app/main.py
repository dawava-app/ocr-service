from fastapi import FastAPI

from app.controllers.ocr_controller import router

app = FastAPI(title="Medicine OCR API")


app.include_router(router, prefix="/ocr")
