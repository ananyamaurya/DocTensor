"""Storage factory — returns the configured FileStore instance."""
from functools import lru_cache

from doctensor.storage.base import FileStore


@lru_cache
def get_file_store() -> FileStore:
    from doctensor.api.config import get_settings
    settings = get_settings()

    if settings.storage_backend == "s3":
        from doctensor.storage.s3 import S3FileStore
        return S3FileStore(
            bucket=settings.s3_bucket,
            endpoint=settings.s3_endpoint,
            access_key=settings.aws_access_key_id,
            secret_key=settings.aws_secret_access_key,
            region=settings.aws_region,
        )

    from doctensor.storage.local import LocalFileStore
    return LocalFileStore(root=settings.storage_root)
