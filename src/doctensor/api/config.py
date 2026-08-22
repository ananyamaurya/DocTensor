from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # API
    app_name: str = "DocTensor API"
    app_version: str = "0.1.0"
    api_prefix: str = "/v1"
    debug: bool = False

    # File handling
    max_sync_file_size_mb: int = 5          # Files above this → async job
    max_file_size_mb: int = 200             # Hard limit for uploads

    # Storage backend
    storage_backend: str = "local"          # local | s3
    storage_root: str = "./tmp_uploads"     # Used when storage_backend=local

    # S3 / MinIO  (Phase 8)
    s3_bucket: str = "doctensor"
    s3_endpoint: str = ""                   # Leave blank for AWS; set for MinIO
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "us-east-1"

    # Redis / Celery
    redis_url: str = "redis://localhost:6379/0"
    celery_concurrency: int = 2

    # Webhooks  (Phase 8)
    webhook_secret: str = "change-me-in-production"
    webhook_timeout_seconds: int = 10


@lru_cache
def get_settings() -> Settings:
    return Settings()
