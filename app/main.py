from fastapi import FastAPI, Depends

from app.controllers.ocr_controller import router
from app.core.security import verify_service_token

app = FastAPI(title="Medicine OCR API")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


app.include_router(router, prefix="", dependencies=[Depends(verify_service_token)])

