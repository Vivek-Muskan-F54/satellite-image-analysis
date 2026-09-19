from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "satellite-image-analysis-api"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Database
    DATABASE_URL: str
    
    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

    # Uploads
    MAX_UPLOAD_SIZE_MB: int = 10
    
    # Storage
    STORAGE_PROVIDER: str = "local" # 'local' or 's3'
    UPLOAD_DIR: str = "storage/uploads"
    
    # S3 Settings (optional, only needed if STORAGE_PROVIDER=s3)
    S3_ENDPOINT_URL: str | None = None
    S3_REGION: str | None = None
    S3_BUCKET: str | None = None
    S3_ACCESS_KEY_ID: str | None = None
    S3_SECRET_ACCESS_KEY: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8', case_sensitive=True, extra="ignore")

settings = Settings()
