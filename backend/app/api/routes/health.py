from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.config import settings
from app.api.deps import get_db
from app.services.analysis_service import check_model_ready
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": settings.PROJECT_NAME
    }

@router.get("/ready")
def readiness_check(db: Session = Depends(get_db)):
    # Check Database
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        logger.error("Readiness check failed on DB (connection error).")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database not ready")

    # Check ML Model
    if not check_model_ready():
        logger.error("Readiness check failed on ML model")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="ML Model not ready")

    return {
        "status": "ready"
    }
