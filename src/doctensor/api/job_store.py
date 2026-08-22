"""
Job registry — tracks status and result locations for async extraction jobs.

Uses Redis when available (production), falls back to an in-process dict
for local development without Redis.
"""
from __future__ import annotations

import json
import uuid
from typing import Any, Optional

from doctensor.api.models import JobStatusEnum


def _new_job_id() -> str:
    return str(uuid.uuid4())


# ---------------------------------------------------------------------------
# Redis-backed store
# ---------------------------------------------------------------------------

class RedisJobStore:
    TTL = 60 * 60 * 24  # 24 hours

    def __init__(self, redis_url: str):
        import redis
        self._r = redis.from_url(redis_url, decode_responses=True)

    def _key(self, job_id: str) -> str:
        return f"doctensor:job:{job_id}"

    def create(self) -> str:
        job_id = _new_job_id()
        self._r.setex(
            self._key(job_id),
            self.TTL,
            json.dumps({"status": JobStatusEnum.queued, "message": "", "result_location": None, "error": None}),
        )
        return job_id

    def set_status(self, job_id: str, status: JobStatusEnum, message: str = "", result_location: Optional[str] = None, error: Optional[str] = None):
        self._r.setex(
            self._key(job_id),
            self.TTL,
            json.dumps({"status": status, "message": message, "result_location": result_location, "error": error}),
        )

    def get(self, job_id: str) -> Optional[dict]:
        raw = self._r.get(self._key(job_id))
        return json.loads(raw) if raw else None


# ---------------------------------------------------------------------------
# In-memory fallback (single-process dev mode)
# ---------------------------------------------------------------------------

class InMemoryJobStore:
    def __init__(self):
        self._store: dict[str, dict] = {}

    def create(self) -> str:
        job_id = _new_job_id()
        self._store[job_id] = {
            "status": JobStatusEnum.queued,
            "message": "",
            "result_location": None,
            "error": None,
        }
        return job_id

    def set_status(self, job_id: str, status: JobStatusEnum, message: str = "", result_location: Optional[str] = None, error: Optional[str] = None):
        if job_id in self._store:
            self._store[job_id].update({
                "status": status,
                "message": message,
                "result_location": result_location,
                "error": error,
            })

    def get(self, job_id: str) -> Optional[dict]:
        return self._store.get(job_id)


# ---------------------------------------------------------------------------
# Singleton factory
# ---------------------------------------------------------------------------

_job_store: Optional[Any] = None


def get_job_store():
    global _job_store
    if _job_store is not None:
        return _job_store

    from doctensor.api.config import get_settings
    settings = get_settings()

    try:
        store = RedisJobStore(settings.redis_url)
        # Quick connectivity check
        import redis
        redis.from_url(settings.redis_url).ping()
        _job_store = store
    except Exception:
        _job_store = InMemoryJobStore()

    return _job_store
