import typer
from typing import Optional

from unidoc.ingestion.pdf import PDFIngestor
from unidoc.pipeline.pipeline import DocumentPipeline
from unidoc.exporters.json import export_json
from unidoc.exporters.markdown import export_markdown

app = typer.Typer()


@app.command()
def main(
    input_path: str = typer.Argument(..., help="Path to the input document"),
    format: str = typer.Option("json", "--format", "-f", help="Output format (json, markdown)"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path")
):
    """Universal Document Engine CLI."""
    # In a full app, we'd have a FileDetector stage to pick the right Ingestor
    if not input_path.lower().endswith(".pdf"):
        typer.echo(f"Unsupported file extension for MVP. Please provide a PDF: {input_path}", err=True)
        raise typer.Exit(code=1)

    ingestor = PDFIngestor()
    
    typer.echo(f"Ingesting {input_path}...")
    context = ingestor.ingest(input_path)

    # The pipeline is mostly empty for the absolute MVP as PDFIngestor does native extraction
    pipeline = DocumentPipeline(stages=[])
    
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


if __name__ == "__main__":
    app()
