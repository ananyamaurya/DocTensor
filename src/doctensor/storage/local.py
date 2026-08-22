"""Local disk implementation of FileStore."""
import os
from pathlib import Path

from doctensor.storage.base import FileStore


class LocalFileStore(FileStore):
    def __init__(self, root: str = "./tmp_uploads"):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _job_dir(self, job_id: str) -> Path:
        d = self.root / job_id
        d.mkdir(parents=True, exist_ok=True)
        return d

    def save(self, job_id: str, filename: str, data: bytes) -> str:
        dest = self._job_dir(job_id) / filename
        dest.write_bytes(data)
        return str(dest)

    def load(self, location: str) -> bytes:
        return Path(location).read_bytes()

    def save_result(self, job_id: str, result_json: str) -> str:
        dest = self._job_dir(job_id) / "result.json"
        dest.write_text(result_json, encoding="utf-8")
        return str(dest)

    def load_result(self, location: str) -> str:
        return Path(location).read_text(encoding="utf-8")
