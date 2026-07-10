"""
Internal service authentication for OCR.
"""

from fastapi import Header, HTTPException, status
from app.config import settings

def verify_service_token(x_service_token: str = Header(...)) -> None:
    """FastAPI dependency – raises 403 when the token is absent or wrong."""
    if not settings.INTERNAL_SERVICE_TOKEN:
        import logging
        logging.getLogger(__name__).warning(
            "INTERNAL_SERVICE_TOKEN is not set – internal auth is disabled!"
        )
        return

    if x_service_token != settings.INTERNAL_SERVICE_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid service token",
        )
