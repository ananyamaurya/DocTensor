from doctensor.pipeline.pipeline import PipelineStage
from doctensor.pipeline.context import PipelineContext
from doctensor.math.base import MathBackend
from doctensor.rendering.pdf_renderer import render_page

class MathStage(PipelineStage):
    def __init__(self, backend: MathBackend, dpi: int = 200):
        self.backend = backend
        self.dpi = dpi

    def run(self, context: PipelineContext) -> PipelineContext:
        if context.source_type != "pdf" or context.raw_document is None:
            return context

        import fitz
        from PIL import Image

        doc: fitz.Document = context.raw_document

        for page_index, page_model in enumerate(context.pages):
            fitz_page = doc[page_index]
            page_image: Image.Image | None = None

            for element in page_model.elements:
                if element.type == "equation" and element.bbox:
                    if page_image is None:
                        page_image = render_page(fitz_page, dpi=self.dpi)

                    scale = self.dpi / 72.0
                    crop_box = (
                        element.bbox.x0 * scale,
                        element.bbox.y0 * scale,
                        element.bbox.x1 * scale,
                        element.bbox.y1 * scale
                    )
                    
                    try:
                        equation_img = page_image.crop(crop_box)
                        latex = self.backend.recognize(equation_img)
                        element.latex = latex
                        element.source = f"math_ocr_{element.source}"
                    except Exception as e:
                        element.metadata["math_error"] = str(e)

        return context
