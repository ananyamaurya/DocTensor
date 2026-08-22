import os
import subprocess
import json
from datasets import load_dataset
from huggingface_hub import hf_hub_download
from doctensor.evaluation.metrics import compute_edit_distance, compute_bleu

def main():
    repo_id = "piushorn/pdf-parse-bench"
    config_name = "2026-q1-formulas-only"
    
    print(f"Loading dataset {repo_id} ({config_name})...")
    ds = load_dataset(repo_id, config_name, split="test")
    
    num_samples = min(3, len(ds))
    
    total_cer = 0
    total_bleu = 0
    
    for i in range(num_samples):
        sample = ds[i]
        pdf_path_in_repo = sample['pdf']
        raw_gt = sample['ground_truth']
        if isinstance(raw_gt, list) and len(raw_gt) > 0 and isinstance(raw_gt[0], dict):
            ground_truth_text = "\n".join(item.get('data', '') for item in raw_gt)
        else:
            ground_truth_text = str(raw_gt)
        
        print(f"\n--- Processing Sample {i+1}/{num_samples} ---")
        print(f"Downloading {pdf_path_in_repo}...")
        
        try:
            full_repo_path = f"{config_name}/{pdf_path_in_repo}"
            local_pdf_path = hf_hub_download(repo_id=repo_id, filename=full_repo_path, repo_type="dataset")
        except Exception as e:
            print(f"Failed to download {pdf_path_in_repo}: {e}")
            continue
            
        print("Running DocTensor extraction pipeline...")
        pred_json = f"pred_{i}.json"
        try:
            subprocess.run([
                r".\venv_311\Scripts\python.exe", "-m", "doctensor.cli", "extract",
                local_pdf_path, "-f", "json", "-o", pred_json
            ], check=True, capture_output=True)
            
            # Extract text from predicted document, ignoring headers/footers
            with open(pred_json, "r", encoding="utf-8") as f:
                doc_data = json.load(f)
                
            pred_texts = []
            for page in doc_data.get("pages", []):
                for element in page.get("elements", []):
                    if not element.get("ignored", False) and element.get("text"):
                        pred_texts.append(element["text"].strip())
            
            pred_text = "\n".join(pred_texts)
            
            # Compute metrics
            edit_metrics = compute_edit_distance(pred_text, ground_truth_text)
            bleu_metrics = compute_bleu(pred_text, ground_truth_text)
            
            print(f"CER: {edit_metrics['cer']:.4f}")
            print(f"BLEU: {bleu_metrics['bleu']:.4f}")
            
            total_cer += edit_metrics['cer']
            total_bleu += bleu_metrics['bleu']
            
        except subprocess.CalledProcessError as e:
            print(f"Extraction failed: {e.stderr.decode('utf-8')}")
        except Exception as e:
            import traceback
            print(f"Processing failed: {e}")
            traceback.print_exc()
            
    print("\n=== Benchmark Summary ===")
    print(f"Average CER: {total_cer / num_samples:.4f}")
    print(f"Average BLEU: {total_bleu / num_samples:.4f}")

if __name__ == "__main__":
    main()
