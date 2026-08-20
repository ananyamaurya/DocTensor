from doctensor.layout.base import LayoutBackend
from doctensor.pipeline.context import PipelineContext


class HeuristicLayoutBackend(LayoutBackend):
    def classify(self, context: PipelineContext):
        for page in context.pages:
            for element in page.elements:
                text = element.text or ""
                text_len = len(text)
                
                # Default fallback
                element.type = "paragraph"
                
                if not text.strip():
                    element.type = "unknown"
                    continue
                    
                bbox = element.bbox
                if bbox:
                    height = bbox.y1 - bbox.y0
                    width = bbox.x1 - bbox.x0
                    
                    # Very basic heuristics based on dimensions and text
                    if text_len < 100 and height > 20:
                        # Likely a heading or title (large font / large bbox height relative to text)
                        if height > 35:
                            element.type = "title"
                        else:
                            element.type = "heading"
                    elif text.strip().startswith(("1.", "-", "*", "•")):
                        element.type = "list"
                    elif width > page.width * 0.8 and height > 200:
                        # Huge blocks might be tables or figures (if we had better structural parsing)
                        pass
                        
                # This heuristic engine is very basic for MVP.
                # In future phases, PaddleStructure or LayoutLM should be used.
