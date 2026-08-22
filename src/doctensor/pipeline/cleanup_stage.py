import re
from collections import defaultdict
from doctensor.pipeline.pipeline import PipelineStage
from doctensor.pipeline.context import PipelineContext
from doctensor.ir.models import Element

class CleanupStage(PipelineStage):
    def __init__(self, header_footer_threshold_ratio: float = 0.1, header_footer_freq_threshold: float = 0.3):
        self.threshold_ratio = header_footer_threshold_ratio
        self.freq_threshold = header_footer_freq_threshold

    def _normalize_text(self, text: str) -> str:
        if not text:
            return ""
        # Remove multiple spaces and strip
        return re.sub(r'\s+', ' ', text).strip()

    def run(self, context: PipelineContext) -> PipelineContext:
        if not context.pages:
            return context

        total_pages = len(context.pages)

        # 1. Detect headers/footers
        text_occurrences = defaultdict(set)
        
        for page_idx, page in enumerate(context.pages):
            top_bound = page.height * self.threshold_ratio
            bottom_bound = page.height * (1.0 - self.threshold_ratio)
            
            for element in page.elements:
                if not element.bbox or not element.text:
                    continue
                
                # Check if in top or bottom region
                if element.bbox.y0 <= top_bound or element.bbox.y1 >= bottom_bound:
                    norm_text = self._normalize_text(element.text)
                    if norm_text:
                        text_occurrences[norm_text].add(page_idx)

        # Find repeating texts
        repeating_texts = {
            text for text, pages in text_occurrences.items()
            if len(pages) / total_pages >= self.freq_threshold and len(pages) > 1
        }

        # Mark elements as header/footer
        for page in context.pages:
            top_bound = page.height * self.threshold_ratio
            bottom_bound = page.height * (1.0 - self.threshold_ratio)
            
            for element in page.elements:
                if not element.bbox or not element.text:
                    continue
                
                norm_text = self._normalize_text(element.text)
                
                if norm_text in repeating_texts:
                    if element.bbox.y0 <= top_bound:
                        element.type = "header"
                        element.ignored = True
                    elif element.bbox.y1 >= bottom_bound:
                        element.type = "footer"
                        element.ignored = True
                else:
                    # Check for standalone numbers (page numbers)
                    if (element.bbox.y0 <= top_bound or element.bbox.y1 >= bottom_bound) and norm_text.isdigit():
                        element.type = "page_number"
                        element.ignored = True

        # 2. Link paragraphs across page breaks
        for i in range(total_pages - 1):
            curr_page = context.pages[i]
            next_page = context.pages[i+1]
            
            valid_curr_elements = [e for e in curr_page.elements if not e.ignored]
            if not valid_curr_elements:
                continue
            last_element = valid_curr_elements[-1]
            
            valid_next_elements = [e for e in next_page.elements if not e.ignored]
            if not valid_next_elements:
                continue
            first_element = valid_next_elements[0]
            
            if last_element.type == "paragraph" and first_element.type == "paragraph":
                text = last_element.text or ""
                next_text = first_element.text or ""
                
                # Does the last element NOT end with a terminal punctuation?
                if text and not text.rstrip().endswith((".", "?", "!", ":", ";", '"', "'", "”", "’")):
                    # Also check if next_text seems to continue (e.g., starts with lowercase)
                    # We can use a simple check, but checking lowercase is safe. 
                    # If it starts with an uppercase, it might be a new sentence, but sometimes OCR messes up.
                    # A robust but simple check: just link them if it doesn't end with a period.
                    last_element.metadata["continues_to"] = first_element.id
                    first_element.metadata["continued_from"] = last_element.id

        return context
