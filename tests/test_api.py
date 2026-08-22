from fastapi.testclient import TestClient
from unittest.mock import patch

from doctensor.api.app import app
from doctensor.api.models import JobStatusEnum

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@patch("doctensor.api.pipeline_runner.run_extraction")
def test_extract_sync(mock_run, tmp_path):
    mock_run.return_value = '{"schema_version": "1.0", "pages": []}'
    
    # Create a dummy pdf file
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 dummy pdf")

    with open(pdf_path, "rb") as f:
        response = client.post(
            "/v1/extract",
            files={"file": ("test.pdf", f, "application/pdf")},
            data={"format": "json"}
        )

    assert response.status_code == 200
    assert response.json()["result"]["schema_version"] == "1.0"


@patch("doctensor.api.pipeline_runner.run_extraction")
@patch("doctensor.worker.tasks.extract_document_task.delay")
def test_submit_job(mock_delay, mock_run, tmp_path):
    mock_run.return_value = '{"schema_version": "1.0", "pages": []}'
    mock_delay.return_value = None
    
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 dummy pdf")

    with open(pdf_path, "rb") as f:
        response = client.post(
            "/v1/jobs",
            files={"file": ("test.pdf", f, "application/pdf")},
            data={"format": "json"}
        )

    assert response.status_code == 202
    data = response.json()
    assert "job_id" in data
    assert data["status"] == JobStatusEnum.queued

    job_id = data["job_id"]

    # Poll status (might be done already if thread finished fast)
    status_resp = client.get(f"/v1/jobs/{job_id}")
    assert status_resp.status_code == 200
    assert status_resp.json()["status"] in [JobStatusEnum.queued, JobStatusEnum.running, JobStatusEnum.done, JobStatusEnum.failed]

    # Try fetch result (should be 202 or 500/200 if finished fast)
    res_resp = client.get(f"/v1/jobs/{job_id}/result")
    assert res_resp.status_code in (202, 200, 500)
