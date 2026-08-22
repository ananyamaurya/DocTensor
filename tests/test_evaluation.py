import pytest
from doctensor.evaluation.metrics import compute_edit_distance, compute_bleu
from doctensor.evaluation.evaluator import DocumentEvaluator
from doctensor.ir.models import Document, DocumentMetadata, Page, Element

def test_metrics():
    ref = "The quick brown fox jumps over the lazy dog."
    hyp = "The fast brown fox jumps over the lazy dog."
    
    # "quick" -> "fast": 5 edits
    edit_res = compute_edit_distance(hyp, ref)
    assert edit_res["edit_distance"] == 5
    assert edit_res["cer"] == 5 / len(ref)
    
    bleu_res = compute_bleu(hyp, ref)
    assert 0.0 < bleu_res["bleu"] < 1.0

def test_evaluator():
    meta = DocumentMetadata(source_type="test", page_count=1)
    
    ref_doc = Document(metadata=meta, pages=[
        Page(physical_page_number=1, width=100, height=100, elements=[
            Element(id="1", type="paragraph", page=1, source="test", text="Hello world.")
        ])
    ])
    
    pred_doc = Document(metadata=meta, pages=[
        Page(physical_page_number=1, width=100, height=100, elements=[
            Element(id="1", type="paragraph", page=1, source="test", text="Hello word.")
        ])
    ])
    
    evaluator = DocumentEvaluator()
    results = evaluator.evaluate(pred_doc, ref_doc)
    
    assert results["edit_distance"] == 1
    assert results["ref_length"] == len("Hello world.")
    assert results["pred_length"] == len("Hello word.")
