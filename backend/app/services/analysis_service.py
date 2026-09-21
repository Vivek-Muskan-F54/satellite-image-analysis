import json
import logging
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.analysis import Analysis, AnalysisStatus, Prediction
from app.models.image import SatelliteImage
from app.storage import storage_service
import traceback

logger = logging.getLogger(__name__)

# Lazy loaded predictor singleton
_predictor = None

def get_predictor():
    global _predictor
    if _predictor is None:
        from ml.inference.predict import LULCPredictor
        try:
            # We explicitly configure it to use CPU inside the predictor
            _predictor = LULCPredictor(model_version="v1")
        except Exception as e:
            logger.error(f"Failed to load ML model: {e}")
            raise RuntimeError(f"ML Model initialization failed: {str(e)}")
    return _predictor

def check_model_ready():
    try:
        get_predictor()
        return True
    except Exception:
        return False

def run_analysis(db: Session, analysis_id: str):
    """
    Executes the ML inference. Should be called after analysis is created in PENDING/PROCESSING.
    """
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        return

    image = db.query(SatelliteImage).filter(SatelliteImage.id == analysis.image_id).first()
    if not image:
        analysis.status = AnalysisStatus.FAILED
        analysis.error_message = "Image not found."
        db.commit()
        return

    try:
        analysis.status = AnalysisStatus.PROCESSING
        db.commit()

        predictor = get_predictor()

        # Get image bytes from storage
        file_obj = storage_service.get(image.storage_key)

        # Predict
        result = predictor.predict(file_obj)
        file_obj.close()

        # Create prediction
        prediction = Prediction(
            analysis_id=analysis.id,
            predicted_class=result["predicted_class"],
            class_index=result["class_index"],
            confidence=result["confidence"],
            probabilities=result["probabilities"]
        )
        db.add(prediction)

        analysis.status = AnalysisStatus.COMPLETED
        analysis.completed_at = func.now()
        db.commit()

    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}\n{traceback.format_exc()}")
        analysis.status = AnalysisStatus.FAILED
        analysis.error_message = f"Inference failed: {str(e)}"
        db.commit()

from sqlalchemy.sql import func
