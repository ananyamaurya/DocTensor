import sys
import os
sys.path.insert(0, os.path.abspath('src'))

import pymupdf as fitz
from doctensor.ingestion.pdf import PDFIngestor
from doctensor.exporters.json import export_json
from doctensor.exporters.markdown import export_markdown

# create a dummy pdf to test
doc = fitz.open()
page = doc.new_page()
page.insert_text((50, 50), "Hello World! This is a test document.\nWith multiple lines.", fontsize=12)
doc.save("dummy_test.pdf")
doc.close()

print("Ingesting dummy_test.pdf...")
ingestor = PDFIngestor()
context = ingestor.ingest("dummy_test.pdf")

print("Exporting to JSON...")
export_json(context.document, "dummy_test.json")

print("Exporting to Markdown...")
export_markdown(context.document, "dummy_test.md")

print("Done! Check dummy_test.json and dummy_test.md")
