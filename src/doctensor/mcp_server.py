"""
Model Context Protocol (MCP) Server for DocTensor.

Provides tools for AI agents to extract structured text and metadata from documents.
"""
import json
import os
from typing import Literal

from fastmcp import FastMCP

from doctensor.api.pipeline_runner import run_extraction
from doctensor.ingestion.pdf import PDFIngestor

# Create the MCP Server
mcp = FastMCP("DocTensor")


@mcp.tool()
def extract_document(
    file_path: str,
    format: Literal["markdown", "json"] = "json"
) -> str:
    """
    Extracts text, tables, and structured data from a PDF or image file.
    
    This is a heavy operation that performs OCR and layout analysis. It supports 
    PDF, JPG, PNG, DOCX, and XLSX files.

    Args:
        file_path: Absolute path to the file.
        format: The desired output format. "json" for structured data, "markdown" for raw text. Defaults to "json".

    Returns:
        The extracted document content as a string.
    """
    if not os.path.exists(file_path):
        return f"Error: File not found at {file_path}"
    
    try:
        result = run_extraction(file_path, output_format=format)
        return result
    except Exception as e:
        return f"Extraction failed: {str(e)}"


@mcp.tool()
def get_document_metadata(file_path: str) -> str:
    """
    Quickly retrieves metadata (e.g. number of pages) for a document without running full OCR/extraction.

    Args:
        file_path: Absolute path to the document.

    Returns:
        JSON string containing metadata.
    """
    if not os.path.exists(file_path):
        return f"Error: File not found at {file_path}"
        
    try:
        # Ingest just reads the document into memory to get page count
        ingestor = PDFIngestor()
        ctx = ingestor.ingest(file_path)
        meta = {
            "num_pages": len(ctx.document),
            "file_size_bytes": os.path.getsize(file_path)
        }
        return json.dumps(meta, indent=2)
    except Exception as e:
        return f"Metadata extraction failed: {str(e)}"


def main():
    """CLI entry point for starting the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
