from doctensor.ir.models import Document
from doctensor.evaluation.metrics import compute_edit_distance, compute_bleu

class DocumentEvaluator:
    def __init__(self, ignore_headers_footers: bool = True):
        self.ignore_headers_footers = ignore_headers_footers

    def _extract_text(self, document: Document) -> str:
        """
        Extracts all valid text from the document in reading order.
        """
        texts = []
        for page in document.pages:
            for element in page.elements:
                if self.ignore_headers_footers and element.ignored:
                    continue
                if element.text:
                    texts.append(element.text.strip())
        return "\n".join(texts)

    def evaluate(self, prediction: Document, reference: Document) -> dict:
        """
        Evaluates a predicted document against a reference ground truth document.
        Returns a dictionary of aggregated metrics.
        """
        pred_text = self._extract_text(prediction)
        ref_text = self._extract_text(reference)
        
        edit_metrics = compute_edit_distance(pred_text, ref_text)
        bleu_metrics = compute_bleu(pred_text, ref_text)
        
        return {
            "cer": edit_metrics["cer"],
            "edit_distance": edit_metrics["edit_distance"],
            "bleu": bleu_metrics["bleu"],
            "pred_length": len(pred_text),
            "ref_length": len(ref_text)
        }
