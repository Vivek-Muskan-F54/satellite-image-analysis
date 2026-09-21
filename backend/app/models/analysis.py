from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.sql import func
from app.db.base import Base
import uuid
import enum

def generate_uuid():
    return str(uuid.uuid4())

class AnalysisStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    image_id = Column(String, ForeignKey("satellite_images.id"), nullable=False, index=True)
    status = Column(Enum(AnalysisStatus), nullable=False, default=AnalysisStatus.PENDING, index=True)
    model_version = Column(String, nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    analysis_id = Column(String, ForeignKey("analyses.id"), nullable=False, index=True)
    predicted_class = Column(String, nullable=False)
    class_index = Column(Integer, nullable=False)
    confidence = Column(Float, nullable=False)
    probabilities = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
