from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.api import deps
from app.models.user import User
from app.schemas.image import SatelliteImageResponse, ImageListResponse
from app.services import image_service
from typing import Any

router = APIRouter()

@router.post("/upload", response_model=SatelliteImageResponse)
def upload_image(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    file: UploadFile = File(...)
) -> Any:
    """
    Upload a satellite image.
    """
    return image_service.upload_image(db, current_user.id, file)

@router.get("", response_model=ImageListResponse)
def get_images(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    List user's uploaded images.
    """
    images = image_service.get_images(db, current_user.id)
    return {"items": images, "total": len(images)}

@router.get("/{image_id}", response_model=SatelliteImageResponse)
def get_image(
    image_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Get a specific image metadata.
    """
    image = image_service.get_image(db, image_id, current_user.id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return image

@router.get("/{image_id}/content")
def get_image_content(
    image_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Get the image file content securely.
    """
    from fastapi.responses import StreamingResponse
    
    image = image_service.get_image(db, image_id, current_user.id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
        
    from app.storage import storage_service
    try:
        file_stream = storage_service.get(image.storage_key)
        return StreamingResponse(file_stream, media_type=image.mime_type)
    except Exception as e:
        raise HTTPException(status_code=404, detail="File not found in storage")

@router.delete("/{image_id}")
def delete_image(
    image_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Delete a specific image.
    """
    success = image_service.delete_image(db, image_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Image not found")
    return {"message": "Image deleted successfully"}
