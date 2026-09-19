import os
import shutil
from typing import IO
from fastapi import HTTPException
from app.storage.base import StorageService

class LocalStorageService(StorageService):
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)
        
    def _get_abs_path(self, object_key: str) -> str:
        # Prevent path traversal
        normalized_key = object_key.replace('/', os.sep)
        file_path = os.path.abspath(os.path.join(self.base_dir, normalized_key))
        if not file_path.startswith(os.path.abspath(self.base_dir)):
            raise HTTPException(status_code=400, detail="Invalid object key")
        return file_path
        
    def save(self, file_obj: IO, object_key: str, content_type: str) -> str:
        file_path = self._get_abs_path(object_key)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file_obj, f)
        return object_key
        
    def delete(self, object_key: str) -> bool:
        try:
            file_path = self._get_abs_path(object_key)
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
        except Exception:
            pass
        return False
        
    def exists(self, object_key: str) -> bool:
        try:
            return os.path.exists(self._get_abs_path(object_key))
        except Exception:
            return False
            
    def get(self, object_key: str) -> IO:
        file_path = self._get_abs_path(object_key)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        return open(file_path, "rb")
