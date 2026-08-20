import pytest
from doctensor.ir.models import Element, BoundingBox, Page, DocumentMetadata
from doctensor.pipeline.context import PipelineContext
from doctensor.layout.heuristic import HeuristicLayoutBackend
from doctensor.pipeline.layout_stage import LayoutStage


def test_heuristic_layout_stage():
    # Setup context with a mock page and elements
    title_element = Element(
        id="p1_e1",
        type="paragraph",
        page=1,
        bbox=BoundingBox(x0=10, y0=10, x1=200, y1=60), # Height 50
        source="native",
        text="This is a Title"
    )
    
    heading_element = Element(
        id="p1_e2",
        type="paragraph",
        page=1,
        bbox=BoundingBox(x0=10, y0=100, x1=150, y1=130), # Height 30
        source="native",
        text="This is a Heading"
    )
    
    paragraph_element = Element(
        id="p1_e3",
        type="paragraph",
        page=1,
        bbox=BoundingBox(x0=10, y0=200, x1=500, y1=215), # Height 15
        source="native",
        text="This is a standard paragraph of text that should just be a paragraph."
    )
    
    list_element = Element(
        id="p1_e4",
        type="paragraph",
        page=1,
        bbox=BoundingBox(x0=20, y0=250, x1=300, y1=265),
        source="native",
        text="- List item 1"
    )

    page = Page(
        physical_page_number=1,
        width=800,
        height=1000,
        elements=[title_element, heading_element, paragraph_element, list_element]
    )
    
    context = PipelineContext(
        source_path="mock.pdf",
        source_type="pdf",
        raw_document=None,
        pages=[page]
    )
    
    backend = HeuristicLayoutBackend()
    stage = LayoutStage(backend=backend)
    
    result_context = stage.run(context)
    elements = result_context.pages[0].elements
    
    assert len(elements) == 4
    assert elements[0].type == "title"
    assert elements[1].type == "heading"
    assert elements[2].type == "paragraph"
    assert elements[3].type == "list"
