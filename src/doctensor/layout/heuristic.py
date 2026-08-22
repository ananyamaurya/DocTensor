from doctensor.layout.base import LayoutBackend
from doctensor.pipeline.context import PipelineContext
import re

class HeuristicLayoutBackend(LayoutBackend):
    def classify(self, context: PipelineContext):
        for page in context.pages:
            for i, element in enumerate(page.elements):
                text = element.text or ""
                text_strip = text.strip()
                text_len = len(text)
                
                # Default fallback
                element.type = "paragraph"
                
                if not text_strip:
                    element.type = "unknown"
                    continue
                    
                bbox = element.bbox
                if bbox:
                    height = bbox.y1 - bbox.y0
                    width = bbox.x1 - bbox.x0
                    page_width = page.width if page.width else 800
                    
                    # Detect large blocks
                    is_large_block = width > page_width * 0.7 and height > 150
                    
                    # Heuristics based on text and dimensions
                    if is_large_block and not text_strip.startswith(("1.", "-", "*", "•")):
                        # Check for tables/figures
                        if "|" in text_strip or text_strip.count("\n") > 5:
                            element.type = "table"
                        else:
                            element.type = "figure"
                    elif text_len < 150 and height > 20:
                        if height > 35:
                            element.type = "title"
                        else:
                            element.type = "heading"
                    elif text_strip.startswith(("1.", "-", "*", "•")) or re.match(r'^\\d+\\.', text_strip):
                        element.type = "list"
                    elif text_strip.lower().startswith(("figure", "fig.", "table", "tab.")) and text_len < 200:
                        element.type = "caption"
                    elif re.search(r'[=+∑∫√]', text_strip) or (text_strip.startswith('\\') and '}' in text_strip):
                        element.type = "equation"
                        
                # Note: This heuristic engine remains basic.
                # In future phases, PaddleStructure or LayoutLM should be used.
