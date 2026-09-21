from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.image import SatelliteImage
from app.models.analysis import Analysis, AnalysisStatus, Prediction
from app.schemas.analysis import AnalysisResponse, AnalysisListResponse, PredictionResponse
from app.services.analysis_service import run_analysis, check_model_ready
from sqlalchemy.sql import func

router = APIRouter()

@router.post("/images/{image_id}", response_model=AnalysisResponse)
def create_analysis(
    image_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify model is ready before attempting
    if not check_model_ready():
        raise HTTPException(status_code=503, detail="ML Model is currently unavailable")

    # Verify image ownership
    image = db.query(SatelliteImage).filter(
        SatelliteImage.id == image_id,
        SatelliteImage.user_id == current_user.id
    ).first()

    if not image:
        raise HTTPException(status_code=404, detail="Image not found or not accessible")

    # Check if a successful analysis already exists for this image and model version
    existing_analysis = db.query(Analysis).filter(
        Analysis.image_id == image_id,
        Analysis.user_id == current_user.id,
        Analysis.model_version == "v1",
        Analysis.status.in_([AnalysisStatus.COMPLETED, AnalysisStatus.PROCESSING, AnalysisStatus.PENDING])
    ).order_by(desc(Analysis.created_at)).first()

    if existing_analysis:
        return get_analysis_response(db, existing_analysis)

    # Create new analysis
    analysis = Analysis(
        user_id=current_user.id,
        image_id=image_id,
        status=AnalysisStatus.PENDING,
        model_version="v1",
        started_at=func.now()
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    # Run analysis (in a real production system this might be a background task via Celery/etc)
    # For this phase, run inline or handle it properly. The requirements say:
    # "The API must remain responsive and deployable."
    # Since MobileNetV3 CPU is fast (~100ms), we can run it synchronously for simplicity,
    # or use FastAPI BackgroundTasks. Let's run it synchronously to guarantee immediate return
    # for the frontend flow, or we can use background task.
    # The requirement says "The API must remain responsive". Let's just run it inline for now,
    # as 64x64 mobilenetv3 is extremely fast.
    run_analysis(db, analysis.id)

    db.refresh(analysis)
    return get_analysis_response(db, analysis)

@router.get("", response_model=AnalysisListResponse)
def list_analyses(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Analysis).filter(Analysis.user_id == current_user.id)
    total = query.count()
    analyses = query.order_by(desc(Analysis.created_at)).offset(skip).limit(limit).all()

    items = [get_analysis_response(db, a) for a in analyses]

    return {"items": items, "total": total}

@router.get("/{analysis_id}", response_model=AnalysisResponse)
def get_analysis(
    analysis_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    analysis = db.query(Analysis).filter(
        Analysis.id == analysis_id,
        Analysis.user_id == current_user.id
    ).first()

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return get_analysis_response(db, analysis)

def get_analysis_response(db: Session, analysis: Analysis) -> dict:
    # Build dictionary response including prediction if available
    result = {
        "id": analysis.id,
        "image_id": analysis.image_id,
        "user_id": analysis.user_id,
        "status": analysis.status,
        "model_version": analysis.model_version,
        "started_at": analysis.started_at,
        "completed_at": analysis.completed_at,
        "error_message": analysis.error_message,
        "created_at": analysis.created_at,
    }

    if analysis.status == AnalysisStatus.COMPLETED:
        prediction = db.query(Prediction).filter(Prediction.analysis_id == analysis.id).first()
        if prediction:
            result["prediction"] = {
                "predicted_class": prediction.predicted_class,
                "class_index": prediction.class_index,
                "confidence": prediction.confidence,
                "probabilities": prediction.probabilities
            }

    return result
