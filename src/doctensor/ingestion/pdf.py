import pymupdf as fitz

from doctensor.ingestion.base import DocumentIngestor
from doctensor.pipeline.context import PipelineContext
from doctensor.ir.models import Page, Element, BoundingBox, DocumentMetadata


class PDFIngestor(DocumentIngestor):
    def ingest(self, file_path: str) -> PipelineContext:
        doc = fitz.open(file_path)
        
        metadata = DocumentMetadata(
            title=doc.metadata.get("title"),
            authors=[doc.metadata.get("author")] if doc.metadata.get("author") else [],
            source_type="pdf",
            page_count=len(doc)
        )
        
        pages = []
        for index, page in enumerate(doc):
            text = page.get_text("text")
            
            elements = []
            needs_ocr = False
            
            if text.strip():
                elements.append(
                    Element(
                        id=f"p{index+1}_text",
                        type="paragraph",
                        page=index + 1,
                        bbox=BoundingBox(
                            x0=page.rect.x0, 
                            y0=page.rect.y0, 
                            x1=page.rect.x1, 
                            y1=page.rect.y1
                        ),
                        confidence=1.0,
                        source="native",
                        text=text.strip(),
                    )
                )
            else:
                needs_ocr = True

            page_model = Page(
                physical_page_number=index + 1,
                printed_page_number=str(index + 1),
                width=page.rect.width,
                height=page.rect.height,
                elements=elements
            )
            # Attach needs_ocr to page metadata
            page_model.metadata["needs_ocr"] = needs_ocr
            pages.append(page_model)
            
        context = PipelineContext(
            source_path=file_path,
            source_type="pdf",
            raw_document=doc,
            pages=pages,
        )
        
        from doctensor.ir.models import Document
        context.document = Document(
            metadata=metadata,
            pages=pages
        )
        
        return context
