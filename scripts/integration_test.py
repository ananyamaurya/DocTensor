# -*- coding: utf-8 -*-
"""
Integration test: download sample PDFs and images from open sources,
run doctensor extraction, and report results.
"""
import os
import sys
import json
import subprocess
import urllib.request
import tempfile
from pathlib import Path

PYTHON = str(Path("venv_311/Scripts/python.exe").resolve())
CLI_MODULE = [PYTHON, "-m", "doctensor.cli", "extract"]

SAMPLES = [
    # --- PDFs ---
    {
        "name": "arXiv-attention-is-all-you-need",
        "type": "pdf",
        "url": "https://arxiv.org/pdf/1706.03762",
    },
    {
        "name": "arXiv-bert-paper",
        "type": "pdf",
        "url": "https://arxiv.org/pdf/1810.04805",
    },
    {
        "name": "IRS-tax-form-w4",
        "type": "pdf",
        "url": "https://www.irs.gov/pub/irs-pdf/fw4.pdf",
    },
    # --- Images (scanned/text-heavy) ---
    {
        "name": "scanned-receipt-png",
        "type": "image",
        "url": "https://upload.wikimedia.org/wikipedia/commons/5/5e/Recibo_de_supermercado_mercadona.jpg",
    },
    {
        "name": "typed-letter-jpg",
        "type": "image",
        "url": "https://upload.wikimedia.org/wikipedia/commons/c/c3/Letter_of_resignation_of_Richard_Nixon.jpg",
    },
    {
        "name": "newspaper-scan",
        "type": "image",
        "url": "https://upload.wikimedia.org/wikipedia/commons/a/a8/Gutenberg_Bible%2C_Lenox_Copy%2C_New_York_Public_Library%2C_2009._Pic_01.jpg",
    },
]

TIMEOUT = 120  # seconds per file


def download_file(url: str, dest: Path) -> bool:
    print(f"  Downloading {url[:70]}...")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as r, open(dest, "wb") as f:
            f.write(r.read())
        size_kb = dest.stat().st_size // 1024
        print(f"  Saved {size_kb} KB -> {dest.name}")
        return True
    except Exception as e:
        print(f"  DOWNLOAD FAILED: {e}")
        return False


def run_extraction(input_path: Path, out_json: Path) -> dict:
    cmd = CLI_MODULE + [str(input_path), "-f", "json", "-o", str(out_json)]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
            cwd=str(Path(__file__).parent.parent),
        )
        return {
            "returncode": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }
    except subprocess.TimeoutExpired:
        return {"returncode": -1, "stdout": "", "stderr": "TIMEOUT"}
    except Exception as e:
        return {"returncode": -1, "stdout": "", "stderr": str(e)}


def count_elements(json_path: Path) -> dict:
    if not json_path.exists():
        return {"pages": 0, "elements": 0, "chars": 0, "sample_text": ""}
    try:
        doc = json.loads(json_path.read_text(encoding="utf-8"))
        pages = doc.get("pages", [])
        all_elements = [el for p in pages for el in p.get("elements", [])]
        all_text = " ".join(el.get("text", "") for el in all_elements)
        return {
            "pages": len(pages),
            "elements": len(all_elements),
            "chars": len(all_text),
            "sample_text": all_text[:200].replace("\n", " "),
        }
    except Exception as e:
        return {"pages": 0, "elements": 0, "chars": 0, "sample_text": f"Parse error: {e}"}


def main():
    out_dir = Path("tests/sample_outputs")
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("DocTensor Integration Test — Open-Source Samples")
    print("=" * 70)

    results = []
    for sample in SAMPLES:
        name = sample["name"]
        ext = ".pdf" if sample["type"] == "pdf" else ".jpg"
        input_path = out_dir / f"{name}{ext}"
        out_json = out_dir / f"{name}.json"

        print(f"\n[{name}]")

        # Download
        ok = download_file(sample["url"], input_path)
        if not ok:
            results.append({"name": name, "status": "DOWNLOAD_FAILED"})
            continue

        # Extract
        print("  Running extraction pipeline...")
        proc = run_extraction(input_path, out_json)
        success = proc["returncode"] == 0

        # Parse output
        counts = count_elements(out_json)

        status = "[PASS]" if success and counts["elements"] > 0 else (
            "[EMPTY]" if success else "[FAIL]"
        )
        results.append({
            "name": name,
            "type": sample["type"],
            "status": status,
            **counts,
        })

        print(f"  Status   : {status}")
        print(f"  Pages    : {counts['pages']}")
        print(f"  Elements : {counts['elements']}")
        print(f"  Chars    : {counts['chars']}")
        print(f"  Preview  : {counts['sample_text'][:120]}")
        if not success:
            last_err = proc["stderr"].splitlines()
            print(f"  Error    : {last_err[-1] if last_err else 'unknown'}")

    # Summary table
    print("\n" + "=" * 70)
    print(f"{'Sample':<40} {'Type':<8} {'Status':<12} {'Pages':>5} {'Elems':>6} {'Chars':>7}")
    print("-" * 70)
    for r in results:
        if "type" in r:
            print(f"{r['name']:<40} {r['type']:<8} {r['status']:<12} {r.get('pages',0):>5} {r.get('elements',0):>6} {r.get('chars',0):>7}")
        else:
            print(f"{r['name']:<40} {'?':<8} {r['status']:<12}")
    print("=" * 70)

    pass_count = sum(1 for r in results if "[PASS]" in r.get("status", ""))
    warn_count = sum(1 for r in results if "[EMPTY]" in r.get("status", ""))
    fail_count = len(results) - pass_count - warn_count
    print(f"\n  PASSED: {pass_count}  EMPTY: {warn_count}  FAILED: {fail_count}  TOTAL: {len(results)}")


if __name__ == "__main__":
    main()
