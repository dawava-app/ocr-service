import logging
from fastapi import FastAPI, Depends

from app.controllers.ocr_controller import router
from app.core.security import verify_service_token

# Initialize logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

app = FastAPI(title="Medicine OCR API")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


app.include_router(router, prefix="/api", dependencies=[Depends(verify_service_token)])

