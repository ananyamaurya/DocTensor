"""S3/MinIO implementation of FileStore (Phase 8).

Activated when STORAGE_BACKEND=s3 is set in env.
Requires: boto3  (add to [project.optional-dependencies] s3 = ["boto3"])
"""
from __future__ import annotations

from doctensor.storage.base import FileStore


class S3FileStore(FileStore):
    def __init__(
        self,
        bucket: str,
        endpoint: str = "",
        access_key: str = "",
        secret_key: str = "",
        region: str = "us-east-1",
    ):
        try:
            import boto3
        except ImportError as e:
            raise RuntimeError(
                "boto3 is required for S3 storage. Install it with: pip install boto3"
            ) from e

        kwargs: dict = {"region_name": region}
        if endpoint:
            kwargs["endpoint_url"] = endpoint
        if access_key and secret_key:
            kwargs["aws_access_key_id"] = access_key
            kwargs["aws_secret_access_key"] = secret_key

        self.s3 = boto3.client("s3", **kwargs)
        self.bucket = bucket

    def _key(self, job_id: str, name: str) -> str:
        return f"jobs/{job_id}/{name}"

    def save(self, job_id: str, filename: str, data: bytes) -> str:
        key = self._key(job_id, filename)
        self.s3.put_object(Bucket=self.bucket, Key=key, Body=data)
        return f"s3://{self.bucket}/{key}"

    def load(self, location: str) -> bytes:
        # location is s3://bucket/key
        _, _, rest = location.partition("://")
        bucket, _, key = rest.partition("/")
        obj = self.s3.get_object(Bucket=bucket, Key=key)
        return obj["Body"].read()

    def save_result(self, job_id: str, result_json: str) -> str:
        return self.save(job_id, "result.json", result_json.encode("utf-8"))

    def load_result(self, location: str) -> str:
        return self.load(location).decode("utf-8")

    def presigned_url(self, location: str, expires: int = 3600) -> str:
        """Generate a pre-signed download URL (Phase 8 enterprise feature)."""
        _, _, rest = location.partition("://")
        bucket, _, key = rest.partition("/")
        return self.s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=expires,
        )
