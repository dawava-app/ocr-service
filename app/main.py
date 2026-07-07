from fastapi import FastAPI
<<<<<<< HEAD

from app.controllers.ocr_controller import router

app = FastAPI(title="Medicine OCR API")


app.include_router(router, prefix="/ocr")
=======
from app.controllers import ocr_controller

app = FastAPI()

app.include_router(
    ocr_controller.router,
    prefix="/ocr",
    tags=["OCR"]
)
>>>>>>> 8cf4df6bd2031e4c282704330e2d754150a5e0c5
