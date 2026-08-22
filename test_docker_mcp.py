import os
import time
import requests
import fitz  # PyMuPDF
import sys

PDF_PATH = r"f:\DataExtract\Ananya_Resume.pdf"
IMAGE_PATH = r"f:\DataExtract\DocTensor\testImages\Ananya_Resume_page0.png"
API_URL = "http://localhost:8000"

def convert_pdf_to_image():
    print(f"Converting PDF {PDF_PATH} to image...")
    doc = fitz.open(PDF_PATH)
    page = doc.load_page(0)
    pix = page.get_pixmap(dpi=150)
    pix.save(IMAGE_PATH)
    print(f"Saved image to {IMAGE_PATH}")
    doc.close()

def wait_for_api():
    print("Waiting for API to be ready...")
    for _ in range(120):
        try:
            r = requests.get(f"{API_URL}/health")
            if r.status_code == 200:
                print("API is ready!")
                return
        except Exception:
            pass
        time.sleep(3)
    print("API failed to become ready.")
    sys.exit(1)

def test_api_extraction(file_path):
    print(f"\n--- Testing API Extraction on {os.path.basename(file_path)} ---")
    with open(file_path, "rb") as f:
        files = {"file": (os.path.basename(file_path), f, "application/pdf" if file_path.endswith(".pdf") else "image/png")}
        data = {"format": "json"}
        
        start = time.time()
        # Using sync extract for now since it is < 5MB
        response = requests.post(f"{API_URL}/v1/extract", files=files, data=data)
        elapsed = time.time() - start
        
        if response.status_code == 200:
            res_json = response.json()
            print(f"Success in {elapsed:.2f}s!")
            print(f"Schema Version: {res_json.get('result', {}).get('schema_version')}")
            pages = res_json.get('result', {}).get('pages', [])
            print(f"Extracted {len(pages)} pages.")
            for i, p in enumerate(pages):
                print(f"  Page {i} size: {p.get('dimensions')}")
                elements = p.get('elements', [])
                print(f"  Page {i} elements: {len(elements)}")
                # Print first few chars of text if any
                text = "\n".join(e.get("text", "") for e in elements if "text" in e)
                print(f"  Preview: {text[:100]}...\n")
        else:
            print(f"Failed! Status: {response.status_code}")
            print(response.text)

def test_mcp_extraction(file_path):
    print(f"\n--- Testing MCP Extraction on {os.path.basename(file_path)} ---")
    # We can just import mcp_server and run the function directly for testing
    from doctensor.mcp_server import extract_document
    start = time.time()
    result_str = extract_document(file_path, format="json")
    elapsed = time.time() - start
    
    if result_str.startswith("Error") or result_str.startswith("Extraction failed"):
        print(f"MCP extraction failed in {elapsed:.2f}s: {result_str}")
    else:
        print(f"MCP Success in {elapsed:.2f}s!")
        print(f"JSON Length: {len(result_str)} chars")


if __name__ == "__main__":
    convert_pdf_to_image()
    wait_for_api()
    test_api_extraction(PDF_PATH)
    test_api_extraction(IMAGE_PATH)
    test_mcp_extraction(PDF_PATH)
    test_mcp_extraction(IMAGE_PATH)
    print("\nAll tests completed!")
