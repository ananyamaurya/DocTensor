import typer
from typing import Optional

from doctensor.ingestion.pdf import PDFIngestor
from doctensor.pipeline.pipeline import DocumentPipeline
from doctensor.pipeline.stages import OCRStage
from doctensor.ocr.paddle import PaddleOCRBackend
from doctensor.layout.heuristic import HeuristicLayoutBackend
from doctensor.pipeline.layout_stage import LayoutStage
from doctensor.exporters.json import export_json
from doctensor.exporters.markdown import export_markdown

app = typer.Typer()


@app.command()
def extract(
    input_path: str = typer.Argument(..., help="Path to the input document"),
    format: str = typer.Option("json", "--format", "-f", help="Output format (json, markdown)"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path")
):
    """Universal Document Engine CLI."""
    if not input_path.lower().endswith(".pdf"):
        typer.echo(f"Unsupported file extension for MVP. Please provide a PDF: {input_path}", err=True)
        raise typer.Exit(code=1)

    typer.echo(f"Ingesting {input_path}...")
    ingestor = PDFIngestor()
    context = ingestor.ingest(input_path)

    typer.echo("Initializing OCR Backend...")
    try:
        ocr_backend = PaddleOCRBackend()
        ocr_stage = OCRStage(backend=ocr_backend)
        stages = [ocr_stage]
    except ImportError:
        typer.echo("Warning: paddleocr not installed. OCR stage will be skipped.", err=True)
        stages = []
        
    typer.echo("Initializing Layout Backend...")
    layout_backend = HeuristicLayoutBackend()
    layout_stage = LayoutStage(backend=layout_backend)
    stages.append(layout_stage)

    typer.echo("Initializing Reading Order Reconstructor...")
    from doctensor.layout.reading_order import ReadingOrderReconstructor
    from doctensor.pipeline.reading_order_stage import ReadingOrderStage
    reading_order_reconstructor = ReadingOrderReconstructor()
    reading_order_stage = ReadingOrderStage(reconstructor=reading_order_reconstructor)
    stages.append(reading_order_stage)

    typer.echo("Initializing Math Backend...")
    try:
        from doctensor.math.pix2tex_backend import Pix2TexBackend
        from doctensor.pipeline.math_stage import MathStage
        math_backend = Pix2TexBackend()
        math_stage = MathStage(backend=math_backend)
        stages.append(math_stage)
    except ImportError as e:
        typer.echo(f"Warning: Math backend disabled due to import error: {e}", err=True)
    except Exception as e:
        typer.echo(f"Warning: Math backend failed to initialize: {e}", err=True)

    typer.echo("Initializing Cleanup Stage...")
    from doctensor.pipeline.cleanup_stage import CleanupStage
    cleanup_stage = CleanupStage()
    stages.append(cleanup_stage)

    pipeline = DocumentPipeline(stages=stages)
    
    typer.echo("Running pipeline...")
    context = pipeline.run(context)
    
    if context.document is None:
        typer.echo("Pipeline failed to produce a Document IR.", err=True)
        raise typer.Exit(code=1)

    out_path = output
    if not out_path:
        base = input_path.rsplit(".", 1)[0]
        out_path = f"{base}.{format}" if format == "json" else f"{base}.md"

    typer.echo(f"Exporting to {format} at {out_path}...")
    if format == "json":
        export_json(context.document, out_path)
    elif format == "markdown":
        export_markdown(context.document, out_path)
    else:
        typer.echo(f"Unknown format: {format}", err=True)
        raise typer.Exit(code=1)
        
    typer.echo("Done!")


@app.command()
def evaluate(
    prediction_path: str = typer.Argument(..., help="Path to the predicted Document JSON"),
    reference_path: str = typer.Argument(..., help="Path to the reference Ground Truth Document JSON"),
    ignore_headers_footers: bool = typer.Option(True, "--ignore-headers-footers", "-i", help="Ignore headers and footers during evaluation")
):
    """Evaluate a predicted document against a ground truth reference."""
    import json
    from doctensor.ir.models import Document
    from doctensor.evaluation.evaluator import DocumentEvaluator

    try:
        with open(prediction_path, "r", encoding="utf-8") as f:
            pred_json = json.load(f)
            prediction = Document(**pred_json)
    except Exception as e:
        typer.echo(f"Failed to load prediction JSON: {e}", err=True)
        raise typer.Exit(code=1)

    try:
        with open(reference_path, "r", encoding="utf-8") as f:
            ref_json = json.load(f)
            reference = Document(**ref_json)
    except Exception as e:
        typer.echo(f"Failed to load reference JSON: {e}", err=True)
        raise typer.Exit(code=1)

    evaluator = DocumentEvaluator(ignore_headers_footers=ignore_headers_footers)
    typer.echo(f"Evaluating {prediction_path} against {reference_path}...")
    
    results = evaluator.evaluate(prediction, reference)
    
    typer.echo("\n--- Evaluation Results ---")
    typer.echo(f"Character Error Rate (CER): {results['cer']:.4f}")
    typer.echo(f"Edit Distance: {results['edit_distance']}")
    typer.echo(f"BLEU Score: {results['bleu']:.4f}")
    typer.echo(f"Prediction Length: {results['pred_length']} chars")
    typer.echo(f"Reference Length: {results['ref_length']} chars")


if __name__ == "__main__":
    app()
