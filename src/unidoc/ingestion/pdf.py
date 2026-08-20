import fitz

from unidoc.ingestion.base import DocumentIngestor
from unidoc.pipeline.context import PipelineContext
from unidoc.ir.models import Page, Element, BoundingBox, DocumentMetadata


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
            
            # Very basic native element extraction for MVP
            elements = []
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
            
            # Note: For MVP we don't fully decompose blocks natively yet, just treating whole page text
            # as paragraph element, but a full implementation would use page.get_text("dict") to extract blocks.

            page_model = Page(
                physical_page_number=index + 1,
                printed_page_number=str(index + 1),
                width=page.rect.width,
                height=page.rect.height,
                elements=elements
            )
            pages.append(page_model)
            
        context = PipelineContext(
            source_path=file_path,
            source_type="pdf",
            raw_document=doc,
            pages=pages,
        )
        
        # Initialize Document inside context early so pipeline has it
        from unidoc.ir.models import Document
        context.document = Document(
            metadata=metadata,
            pages=pages
        )
        
        return context
