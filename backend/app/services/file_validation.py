import os
from fastapi import UploadFile, HTTPException
from PIL import Image, UnidentifiedImageError
import io

# Allowed mime types and extensions
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/tiff"}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tif", ".tiff"}

def validate_image_file(file: UploadFile, max_size_bytes: int):
    # 1. File exists and not empty
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # 4. Extension validation
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file extension")
    
    # 5. MIME validation
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported MIME type")
    
    # Read file content for integrity and size checks
    content = file.file.read()
    file_size = len(content)
    
    # 2. File not empty
    if file_size == 0:
        raise HTTPException(status_code=400, detail="File is empty")
    
    # 3. File size validation
    if file_size > max_size_bytes:
        raise HTTPException(status_code=413, detail=f"File too large. Maximum size is {max_size_bytes / (1024 * 1024)} MB")
    
    # 6 & 7. Image integrity validation
    try:
        image = Image.open(io.BytesIO(content))
        image.verify() # Verify that it is, in fact, an image
        
        # We need to open it again to get dimensions reliably in some formats
        image = Image.open(io.BytesIO(content))
        width, height = image.size
    except (UnidentifiedImageError, Exception):
        raise HTTPException(status_code=400, detail="Invalid or malformed image")
    
    # Reset file cursor for saving
    file.file.seek(0)
    
    return {
        "file_size": file_size,
        "width": width,
        "height": height,
        "extension": ext
    }
