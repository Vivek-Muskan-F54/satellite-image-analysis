from app.core.config import settings
from app.storage.base import StorageService
from app.storage.local import LocalStorageService
from app.storage.cloud import S3StorageService

def get_storage_provider() -> StorageService:
    provider = settings.STORAGE_PROVIDER.lower()

    if provider == "local":
        from .local import LocalStorageService
        return LocalStorageService(base_dir=settings.STORAGE_LOCAL_ROOT)
    elif provider == "s3":
        return S3StorageService()
    else:
        raise ValueError(f"Unknown storage provider: {provider}")

storage_service = get_storage_provider()
