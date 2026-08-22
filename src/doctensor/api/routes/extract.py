"""
/v1/extract   — synchronous extraction (small files)
/v1/jobs      — async job submission
/v1/jobs/{id} — job status poll
/v1/jobs/{id}/result — fetch completed result
"""
from __future__ import annotations

import json
import os
import tempfile
from typing import Annotated, Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from doctensor.api.models import (
    ExtractionResponse,
    JobResponse,
    JobStatusEnum,
    JobStatusResponse,
    OutputFormat,
)

router = APIRouter(prefix="/v1", tags=["extraction"])


# ---------------------------------------------------------------------------
# Synchronous endpoint  (files ≤ MAX_SYNC_FILE_SIZE_MB)
# ---------------------------------------------------------------------------

@router.post(
    "/extract",
    response_model=ExtractionResponse,
    summary="Synchronous extraction",
    description="Upload a document and receive the extracted content immediately. "
                "Best for files under 5 MB.",
)
async def extract_sync(
    file: Annotated[UploadFile, File(description="PDF, image (jpg/png), or other supported doc")],
    format: OutputFormat = Form(OutputFormat.json),
):
    from doctensor.api.config import get_settings
    from doctensor.api.pipeline_runner import run_extraction

    settings = get_settings()
    data = await file.read()
    size_mb = len(data) / (1024 * 1024)

    if size_mb > settings.max_file_size_mb:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large ({size_mb:.1f} MB). Maximum is {settings.max_file_size_mb} MB.",
        )

    if size_mb > settings.max_sync_file_size_mb:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds sync limit ({settings.max_sync_file_size_mb} MB). "
                   "Use POST /v1/jobs for async processing.",
        )

    # Write to a temp file and run the pipeline
    suffix = os.path.splitext(file.filename or "upload.pdf")[1] or ".pdf"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(data)
        tmp_path = tmp.name

        try:
            result_str = run_extraction(tmp_path, output_format=format.value)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

    result = json.loads(result_str) if format == OutputFormat.json else result_str
    return ExtractionResponse(format=format, result=result)


# ---------------------------------------------------------------------------
# Async endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/jobs",
    response_model=JobResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Submit async extraction job",
)
async def submit_job(
    file: Annotated[UploadFile, File(description="Document to process")],
    format: OutputFormat = Form(OutputFormat.json),
    webhook_url: Optional[str] = Form(None),
):
    from doctensor.api.config import get_settings
    from doctensor.api.job_store import get_job_store
    from doctensor.storage import get_file_store

    settings = get_settings()
    data = await file.read()
    size_mb = len(data) / (1024 * 1024)

    if size_mb > settings.max_file_size_mb:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large ({size_mb:.1f} MB). Maximum is {settings.max_file_size_mb} MB.",
        )

    job_store = get_job_store()
    file_store = get_file_store()

    job_id = job_store.create()
    filename = file.filename or f"upload{os.path.splitext(file.filename or '.pdf')[1]}"
    file_location = file_store.save(job_id, filename, data)

    # Enqueue Celery task (or run inline if Celery not available)
    try:
        from doctensor.worker.tasks import extract_document_task
        extract_document_task.delay(
            job_id=job_id,
            file_location=file_location,
            output_format=format.value,
            webhook_url=webhook_url,
            webhook_secret=settings.webhook_secret if webhook_url else None,
        )
    except Exception:
        # Celery/Redis not available → run synchronously in background thread
        import threading
        from doctensor.api.pipeline_runner import run_extraction
        from doctensor.storage import get_file_store as _fs

        def _run():
            try:
                job_store.set_status(job_id, JobStatusEnum.running)
                result_str = run_extraction(file_location, output_format=format.value)
                loc = _fs().save_result(job_id, result_str)
                job_store.set_status(job_id, JobStatusEnum.done, result_location=loc)
            except Exception as e:
                job_store.set_status(job_id, JobStatusEnum.failed, error=str(e))

        threading.Thread(target=_run, daemon=True).start()

    return JobResponse(job_id=job_id, status=JobStatusEnum.queued)


@router.get(
    "/jobs/{job_id}",
    response_model=JobStatusResponse,
    summary="Poll job status",
)
async def job_status(job_id: str):
    from doctensor.api.job_store import get_job_store

    record = get_job_store().get(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobStatusResponse(
        job_id=job_id,
        status=record["status"],
        message=record.get("message", ""),
        error=record.get("error"),
    )


@router.get(
    "/jobs/{job_id}/result",
    summary="Fetch completed job result",
)
async def job_result(job_id: str):
    from doctensor.api.job_store import get_job_store
    from doctensor.storage import get_file_store

    record = get_job_store().get(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Job not found")

    if record["status"] == JobStatusEnum.failed:
        raise HTTPException(status_code=500, detail=record.get("error", "Unknown error"))

    if record["status"] != JobStatusEnum.done:
        raise HTTPException(status_code=202, detail=f"Job is {record['status']}")

    result_str = get_file_store().load_result(record["result_location"])
    try:
        return json.loads(result_str)
    except json.JSONDecodeError:
        return {"result": result_str}
