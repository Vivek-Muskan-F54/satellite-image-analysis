from typing import List, Optional, Union
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import json
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "satellite-image-analysis-api"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    CORS_ORIGINS: List[str] = ["http://localhost:5173"]

    @field_validator("CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, str) and v.startswith("["):
            return json.loads(v)
        return v

    DATABASE_URL: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    MAX_UPLOAD_SIZE_MB: int = 10

    STORAGE_PROVIDER: str = "local"
    STORAGE_LOCAL_ROOT: str = "storage/uploads"

    S3_ENDPOINT_URL: Optional[str] = None
    S3_REGION: Optional[str] = None
    S3_BUCKET_NAME: Optional[str] = None
    S3_ACCESS_KEY_ID: Optional[str] = None
    S3_SECRET_ACCESS_KEY: Optional[str] = None

    ML_MODEL_PATH: str = "ml/models/land_cover/v1/best_model.pt"
    ML_MODEL_VERSION: str = "v1"
    ML_DEVICE: str = "cpu"

    @model_validator(mode="after")
    def validate_production(self):
        if self.ENVIRONMENT == "production":
            if not self.DATABASE_URL or self.DATABASE_URL == "postgresql://user:password@localhost:5432/db":
                raise ValueError("DATABASE_URL must be explicitly supplied in production.")
            weak_secrets = ["development_secret_key_change_in_production", "secret", "changeme", "password", "test"]
            if not self.JWT_SECRET_KEY or self.JWT_SECRET_KEY in weak_secrets:
                raise ValueError("JWT_SECRET_KEY must be a strong secret in production.")
            if len(self.JWT_SECRET_KEY) < 32:
                raise ValueError("JWT_SECRET_KEY must be at least 32 characters for HS256.")
            if not self.CORS_ORIGINS:
                raise ValueError("CORS_ORIGINS must not be empty in production.")
            if not os.path.exists(self.ML_MODEL_PATH):
                raise ValueError(f"ML_MODEL_PATH {self.ML_MODEL_PATH} must exist when starting in production.")

        if self.JWT_ALGORITHM not in ["HS256", "RS256"]:
            raise ValueError("JWT_ALGORITHM must be HS256 or RS256.")
        if self.ACCESS_TOKEN_EXPIRE_MINUTES <= 0:
            raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES must be positive.")
        if self.STORAGE_PROVIDER not in ["local", "s3"]:
            raise ValueError("STORAGE_PROVIDER must be 'local' or 's3'.")
        if self.STORAGE_PROVIDER == "s3":
            missing_s3 = []
            if not self.S3_BUCKET_NAME: missing_s3.append("S3_BUCKET_NAME")
            if not self.S3_ACCESS_KEY_ID: missing_s3.append("S3_ACCESS_KEY_ID")
            if not self.S3_SECRET_ACCESS_KEY: missing_s3.append("S3_SECRET_ACCESS_KEY")
            if missing_s3:
                raise ValueError(f"S3_BUCKET_NAME, S3_ACCESS_KEY_ID, and S3_SECRET_ACCESS_KEY are required for s3 storage. Missing: {', '.join(missing_s3)}")
        if self.ML_DEVICE not in ["cpu", "cuda", "mps"]:
            raise ValueError("ML_DEVICE must be one of: cpu, cuda, mps")
        return self

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8', case_sensitive=True, extra="ignore")

settings = Settings()
