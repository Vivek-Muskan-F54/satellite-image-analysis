from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SatelliteImageBase(BaseModel):
    original_filename: str
    mime_type: str
    file_size: int
    width: Optional[int] = None
    height: Optional[int] = None

class SatelliteImageResponse(SatelliteImageBase):
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ImageListResponse(BaseModel):
    items: list[SatelliteImageResponse]
    total: int
