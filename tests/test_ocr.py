import pytest
from PIL import Image

from doctensor.ir.models import Element, BoundingBox
from doctensor.ocr.base import OCRBackend
from doctensor.pipeline.context import PipelineContext
from doctensor.ir.models import Page, DocumentMetadata
from doctensor.pipeline.stages import OCRStage


class MockOCRBackend(OCRBackend):
    def recognize(self, image: Image.Image, page_number: int) -> list[Element]:
        # Just return a dummy element to verify the stage works
        return [
            Element(
                id=f"p{page_number}_mock_0",
                type="paragraph",
                page=page_number,
                bbox=BoundingBox(x0=0, y0=0, x1=10, y1=10),
                confidence=0.99,
                source="ocr",
                text="Mocked OCR text"
            )
        ]


def test_ocr_stage_execution():
    # Setup a mock context with a page needing OCR
    # We need a mock raw_document (fitz.Document) for the rendering stage, 
    # but rendering requires an actual fitz page. 
    # For this unit test, we can just monkeypatch render_page.
    import doctensor.pipeline.stages
    
    def mock_render_page(fitz_page, dpi):
        return Image.new('RGB', (100, 100))
        
    doctensor.pipeline.stages.render_page = mock_render_page
    
    page = Page(
        physical_page_number=1,
        width=100,
        height=100,
        elements=[]
    )
    page.metadata["needs_ocr"] = True
    
    context = PipelineContext(
        source_path="mock.pdf",
        source_type="pdf",
        raw_document=[None], # Just needs to be indexable by physical_index (0)
        pages=[page]
    )
    
    backend = MockOCRBackend()
    stage = OCRStage(backend=backend)
    
    result_context = stage.run(context)
    
    assert len(result_context.pages) == 1
    assert result_context.pages[0].metadata.get("ocr_applied") is True
    assert len(result_context.pages[0].elements) == 1
    assert result_context.pages[0].elements[0].source == "ocr"
    assert result_context.pages[0].elements[0].text == "Mocked OCR text"
