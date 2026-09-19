import os
import uuid
from typing import List, Optional
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.models.image import SatelliteImage
from app.core.config import settings
from app.services import file_validation
from app.storage import storage_service

def upload_image(db: Session, user_id: str, file: UploadFile) -> SatelliteImage:
    max_size_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    
    # 1. Validate
    validation_data = file_validation.validate_image_file(file, max_size_bytes)
    
    # 2. Generate unique object key (e.g. users/{user_id}/images/{uuid}.ext)
    image_uuid = str(uuid.uuid4())
    object_key = f"users/{user_id}/images/{image_uuid}{validation_data['extension']}"
    
    # 3. Save file using generic storage provider
    storage_key = storage_service.save(file.file, object_key, file.content_type)
    
    # 4. Create database record
    db_image = SatelliteImage(
        id=image_uuid,
        user_id=user_id,
        original_filename=file.filename,
        storage_provider=settings.STORAGE_PROVIDER,
        storage_key=storage_key,
        mime_type=file.content_type,
        file_size=validation_data["file_size"],
        file_extension=validation_data["extension"],
        width=validation_data["width"],
        height=validation_data["height"]
    )
    
    try:
        db.add(db_image)
        db.commit()
        db.refresh(db_image)
        return db_image
    except Exception as e:
        # 5. Clean up orphaned file on DB failure
        db.rollback()
        storage_service.delete(storage_key)
        raise HTTPException(status_code=500, detail="Failed to save image metadata")

def get_images(db: Session, user_id: str) -> List[SatelliteImage]:
    return db.query(SatelliteImage).filter(SatelliteImage.user_id == user_id).order_by(SatelliteImage.created_at.desc()).all()

def get_image(db: Session, image_id: str, user_id: str) -> Optional[SatelliteImage]:
    image = db.query(SatelliteImage).filter(SatelliteImage.id == image_id).first()
    if not image:
        return None
    if image.user_id != user_id:
        return None # Return None to simulate 404
    return image

def delete_image(db: Session, image_id: str, user_id: str) -> bool:
    image = get_image(db, image_id, user_id)
    if not image:
        return False
        
    storage_service.delete(image.storage_key)
    
    db.delete(image)
    db.commit()
    return True
