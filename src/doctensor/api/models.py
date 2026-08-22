"""Pydantic request/response models for the DocTensor REST API."""
from __future__ import annotations
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, HttpUrl


class OutputFormat(str, Enum):
    json = "json"
    markdown = "markdown"


class JobStatusEnum(str, Enum):
    queued = "queued"
    running = "running"
    done = "done"
    failed = "failed"


class JobResponse(BaseModel):
    job_id: str
    status: JobStatusEnum
    message: str = ""


class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatusEnum
    message: str = ""
    # Non-null when status == done
    result: Optional[Any] = None
    error: Optional[str] = None


class ExtractionResponse(BaseModel):
    """Returned by the synchronous /v1/extract endpoint."""
    status: str = "completed"
    format: OutputFormat
    result: Any   # Document JSON dict or markdown string


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str


class WebhookJobRequest(BaseModel):
    """Body accepted by POST /v1/jobs for async submission."""
    format: OutputFormat = OutputFormat.json
    # Phase 8: optional webhook callback
    webhook_url: Optional[str] = None
    webhook_secret: Optional[str] = None
