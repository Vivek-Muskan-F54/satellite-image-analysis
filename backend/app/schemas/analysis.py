from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict
from datetime import datetime
from app.models.analysis import AnalysisStatus

class PredictionResponse(BaseModel):
    predicted_class: str
    class_index: int
    confidence: float
    probabilities: Dict[str, float]

    model_config = ConfigDict(from_attributes=True)

class AnalysisBase(BaseModel):
    image_id: str

class AnalysisCreate(AnalysisBase):
    pass

class AnalysisResponse(AnalysisBase):
    id: str
    user_id: str
    status: AnalysisStatus
    model_version: str
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]
    created_at: datetime

    prediction: Optional[PredictionResponse] = None

    model_config = ConfigDict(from_attributes=True)

class AnalysisListResponse(BaseModel):
    items: list[AnalysisResponse]
    total: int

    model_config = ConfigDict(from_attributes=True)
