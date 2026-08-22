import numpy as np
from PIL import Image

from doctensor.ocr.base import OCRBackend
from doctensor.ir.models import Element, BoundingBox


class PaddleOCRBackend(OCRBackend):
    def __init__(self, lang: str = 'en'):
        import os
        os.environ['FLAGS_use_mkldnn'] = '0'
        from paddleocr import PaddleOCR
        # Initialize PaddleOCR (downloads models on first run if needed)
        self.engine = PaddleOCR(use_angle_cls=True, lang=lang, use_mkldnn=False)

    def recognize(self, image: Image.Image, page_number: int) -> list[Element]:
        # Convert PIL image to numpy array for PaddleOCR
        img_array = np.array(image.convert('RGB'))
        # paddle expects BGR generally, but RGB works fine for text recognition.
        # To be safe, convert RGB to BGR:
        img_array = img_array[:, :, ::-1].copy()
        
        results = self.engine.ocr(img_array, cls=True)
        
        elements = []
        if not results or not results[0]:
            return elements

        for i, line in enumerate(results[0]):
            # line is [[x1, y1], [x2, y2], [x3, y3], [x4, y4]], (text, confidence)
            box = line[0]
            text, confidence = line[1]
            
            x_coords = [p[0] for p in box]
            y_coords = [p[1] for p in box]
            
            bbox = BoundingBox(
                x0=min(x_coords),
                y0=min(y_coords),
                x1=max(x_coords),
                y1=max(y_coords)
            )
            
            elements.append(
                Element(
                    id=f"p{page_number}_ocr_{i}",
                    type="paragraph", # Assuming everything is paragraph until Layout detection
                    page=page_number,
                    bbox=bbox,
                    confidence=float(confidence),
                    source="ocr",
                    text=text
                )
            )
        return elements
