import Levenshtein
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction

def compute_edit_distance(hypothesis: str, reference: str) -> dict:
    """
    Computes Levenshtein distance and Character Error Rate (CER).
    """
    dist = Levenshtein.distance(hypothesis, reference)
    cer = dist / len(reference) if len(reference) > 0 else (1.0 if len(hypothesis) > 0 else 0.0)
    
    return {
        "edit_distance": dist,
        "cer": cer
    }

def compute_bleu(hypothesis: str, reference: str) -> dict:
    """
    Computes BLEU score for a given hypothesis and reference text.
    Uses smoothing method 1 to prevent 0 scores for short texts.
    """
    ref_tokens = [reference.split()]
    hyp_tokens = hypothesis.split()
    
    if not ref_tokens[0] or not hyp_tokens:
        return {"bleu": 0.0 if (ref_tokens[0] or hyp_tokens) else 1.0}
        
    smoothie = SmoothingFunction().method1
    bleu_score = sentence_bleu(ref_tokens, hyp_tokens, smoothing_function=smoothie)
    
    return {
        "bleu": bleu_score
    }
