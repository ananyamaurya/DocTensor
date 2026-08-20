import pytest
from doctensor.ir.models import Document, Page, Element, BoundingBox, DocumentMetadata


def test_document_creation():
    metadata = DocumentMetadata(
        title="Test Doc",
        source_type="pdf",
        page_count=1
    )
    doc = Document(metadata=metadata, pages=[])
    
    assert doc.metadata.title == "Test Doc"
    assert doc.metadata.source_type == "pdf"
    assert doc.schema_version == "1.0"
    assert len(doc.pages) == 0


def test_page_and_element_creation():
    bbox = BoundingBox(x0=0, y0=0, x1=100, y1=100)
    elem = Element(
        id="test_id",
        type="paragraph",
        page=1,
        bbox=bbox,
        confidence=0.95,
        source="test",
        text="Hello world"
    )
    
    page = Page(
        physical_page_number=1,
        width=800,
        height=1000,
        elements=[elem]
    )
    
    assert page.physical_page_number == 1
    assert len(page.elements) == 1
    assert page.elements[0].text == "Hello world"
    assert page.elements[0].bbox.x1 == 100
