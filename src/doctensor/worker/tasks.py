"""
Celery tasks for async document extraction.

Phase 7: extract_document_task  — runs pipeline, stores result.
Phase 8: fires webhook on completion.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import time
from typing import Optional

from doctensor.worker.celery_app import get_celery_app

celery_app = get_celery_app()


@celery_app.task(bind=True, name="doctensor.extract", max_retries=2)
def extract_document_task(
    self,
    job_id: str,
    file_location: str,
    output_format: str = "json",
    webhook_url: Optional[str] = None,
    webhook_secret: Optional[str] = None,
):
    """
    Celery task that:
    1. Loads the uploaded file from storage.
    2. Runs the DocTensor pipeline.
    3. Persists the result to storage.
    4. Updates job status in the job store.
    5. (Phase 8) Fires a signed webhook POST if webhook_url is provided.
    """
    from doctensor.api.job_store import get_job_store
    from doctensor.api.models import JobStatusEnum
    from doctensor.storage import get_file_store
    from doctensor.api.pipeline_runner import run_extraction
    import tempfile, os

    store = get_file_store()
    job_store = get_job_store()

    job_store.set_status(job_id, JobStatusEnum.running, "Extraction in progress")

    try:
        # Load file bytes from storage → write to a temp file for PyMuPDF
        file_bytes = store.load(file_location)
        suffix = "." + file_location.rsplit(".", 1)[-1] if "." in file_location else ".pdf"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        try:
            result_str = run_extraction(tmp_path, output_format=output_format)
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

        result_location = store.save_result(job_id, result_str)
        job_store.set_status(
            job_id,
            JobStatusEnum.done,
            "Extraction completed",
            result_location=result_location,
        )

        # Phase 8 — fire webhook
        if webhook_url:
            _fire_webhook(webhook_url, job_id, result_str, webhook_secret)

    except Exception as exc:
        job_store.set_status(
            job_id,
            JobStatusEnum.failed,
            error=str(exc),
        )
        raise self.retry(exc=exc, countdown=5)


# ---------------------------------------------------------------------------
# Phase 8 helpers
# ---------------------------------------------------------------------------

def _fire_webhook(
    url: str,
    job_id: str,
    result_json: str,
    secret: Optional[str],
    timeout: int = 10,
) -> None:
    """POST the extraction result to the caller-provided webhook URL."""
    import urllib.request

    payload = json.dumps({"job_id": job_id, "status": "done", "result": json.loads(result_json)}).encode()

    headers = {"Content-Type": "application/json", "X-DocTensor-JobId": job_id}

    if secret:
        sig = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
        headers["X-DocTensor-Signature"] = f"sha256={sig}"

    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    try:
        urllib.request.urlopen(req, timeout=timeout)
    except Exception:
        pass  # Best-effort delivery; caller can poll /v1/jobs/{id}/result
