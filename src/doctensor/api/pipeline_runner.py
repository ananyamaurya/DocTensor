"""
Shared helper that builds and runs the DocumentPipeline.
Used by both the sync API endpoint and the Celery worker task.
"""
from __future__ import annotations

import tempfile
import os
from pathlib import Path
from typing import Literal


def build_pipeline():
    """Instantiate the full extraction pipeline (OCR + Layout + Math + Cleanup)."""
    from doctensor.pipeline.stages import OCRStage
    from doctensor.layout.heuristic import HeuristicLayoutBackend
    from doctensor.pipeline.layout_stage import LayoutStage
    from doctensor.layout.reading_order import ReadingOrderReconstructor
    from doctensor.pipeline.reading_order_stage import ReadingOrderStage
    from doctensor.pipeline.cleanup_stage import CleanupStage
    from doctensor.pipeline.pipeline import DocumentPipeline

    stages = []

    # OCR stage
    try:
        from doctensor.ocr.paddle import PaddleOCRBackend
        stages.append(OCRStage(backend=PaddleOCRBackend()))
    except Exception:
        pass  # PaddleOCR optional — skipped if not installed

    # Layout + reading order
    stages.append(LayoutStage(backend=HeuristicLayoutBackend()))
    stages.append(ReadingOrderStage(reconstructor=ReadingOrderReconstructor()))

    # Math (optional — requires pix2tex)
    try:
        from doctensor.math.pix2tex_backend import Pix2TexBackend
        from doctensor.pipeline.math_stage import MathStage
        stages.append(MathStage(backend=Pix2TexBackend()))
    except Exception:
        pass

    stages.append(CleanupStage())
    return DocumentPipeline(stages=stages)


def run_extraction(
    file_path: str,
    output_format: Literal["json", "markdown"] = "json",
) -> str:
    """
    Run the full pipeline on *file_path* and return the result
    as a JSON string (or Markdown string if format=markdown).
    """
    from doctensor.ingestion.pdf import PDFIngestor

    ingestor = PDFIngestor()
    context = ingestor.ingest(file_path)
    pipeline = build_pipeline()
    context = pipeline.run(context)

    if context.document is None:
        raise RuntimeError("Pipeline produced no Document IR.")

    if output_format == "markdown":
        from doctensor.exporters.markdown import export_markdown
        import tempfile, os
        tmp = tempfile.NamedTemporaryFile(suffix=".md", delete=False)
        tmp.close()
        export_markdown(context.document, tmp.name)
        result = Path(tmp.name).read_text(encoding="utf-8")
        os.unlink(tmp.name)
        return result
    else:
        return context.document.model_dump_json(indent=2, exclude_none=True)
