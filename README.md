# DocTensor

DocTensor is a scalable document extraction and parsing pipeline that converts unstructured documents (PDFs, images) into structured, LLM-ready JSON layouts. It utilizes `PyMuPDF` for fast native PDF text extraction and integrates `PaddleOCR` to gracefully handle scanned documents and images.

## Features

- **Robust Ingestion**: Supports PDF files, Images (JPG, PNG).
- **Hybrid Extraction**: Automatically detects if a page needs OCR. Extracts native text layers lightning-fast or falls back to PaddleOCR for scanned pages.
- **Structured Schema**: Organizes documents by pages, blocks, and precise bounding boxes for advanced Retrieval-Augmented Generation (RAG) pipelines.
- **RESTful API**: FastAPI server offering asynchronous task-based extraction using Celery and Redis.
- **Docker Support**: Completely containerized setup out-of-the-box including API, Workers, and Redis.
- **MCP Server**: Includes an MCP (Model Context Protocol) integration to directly expose document extraction tools to AI agents like Claude.

## Installation

### Local Setup (Python 3.11+)

1. Clone the repository and configure your environment:
   ```bash
   git clone https://github.com/your-username/DocTensor.git
   cd DocTensor
   python -m venv venv
   # On Windows: venv\Scripts\activate
   # On macOS/Linux: source venv/bin/activate
   ```

2. Install the package and its dependencies:
   ```bash
   # For standard API and OCR support:
   pip install -e .[api,ocr]

   # For the MCP server integration:
   pip install -e .[mcp]
   ```

### Docker Setup

You can run the full asynchronous stack (API, Redis, and Celery Worker) using Docker Compose:

```bash
docker-compose up --build -d
```

The API will be available at `http://localhost:8000`.

## Usage

### As a Library

```python
from doctensor.api.pipeline_runner import build_pipeline
from doctensor.ingestion.pdf import PDFIngestor
import os

pipeline = build_pipeline()
ingestor = PDFIngestor()

context = ingestor.ingest("sample.pdf")
pipeline.run(context)

json_output = context.document.model_dump_json(indent=2)
print(json_output)
```

### API Endpoints

- **`POST /v1/extract`**: Synchronous extraction of a document.
- **`POST /v1/jobs`**: Asynchronously dispatch an extraction task. Returns a `job_id`.
- **`GET /v1/jobs/{job_id}`**: Check the status and fetch results of an asynchronous job.

### Model Context Protocol (MCP)

To use DocTensor directly from Claude or other MCP-compatible clients, run the MCP server:

```bash
python -m doctensor.mcp.server
```

You can configure your AI assistant (e.g. Claude Desktop) with this MCP integration to provide dynamic data extraction and semantic search integration.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
