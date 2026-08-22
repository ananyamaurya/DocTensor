from PIL import Image

from doctensor.pipeline.pipeline import PipelineStage
from doctensor.pipeline.context import PipelineContext
from doctensor.ocr.base import OCRBackend
from doctensor.rendering.pdf_renderer import render_page


class OCRStage(PipelineStage):
    def __init__(self, backend: OCRBackend, dpi: int = 200):
        self.backend = backend
        self.dpi = dpi

    def run(self, context: PipelineContext) -> PipelineContext:
        if context.raw_document is None:
            return context

        doc = context.raw_document # Assuming this is a fitz.Document

        for page_model in context.pages:
            needs_ocr = page_model.metadata.get("needs_ocr", False)
            if needs_ocr:
                # Get the actual fitz page (0-indexed)
                physical_index = page_model.physical_page_number - 1
                fitz_page = doc[physical_index]
                
                # Render to image
                image = render_page(fitz_page, dpi=self.dpi)
                
                # Perform OCR
                ocr_elements = self.backend.recognize(image, page_model.physical_page_number)
                
                # Add elements to page
                page_model.elements.extend(ocr_elements)
                
                # Update metadata so we know it was OCR'd
                page_model.metadata["ocr_applied"] = True

        return context
