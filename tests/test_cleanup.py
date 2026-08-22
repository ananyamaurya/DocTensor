import pytest
from doctensor.ir.models import Page, Element, BoundingBox
from doctensor.pipeline.context import PipelineContext
from doctensor.pipeline.cleanup_stage import CleanupStage

def create_element(id: str, type: str, page: int, y0: float, y1: float, text: str):
    return Element(
        id=id,
        type=type,
        page=page,
        bbox=BoundingBox(x0=0, y0=y0, x1=100, y1=y1),
        source="test",
        text=text
    )

def test_header_footer_detection():
    # Create 3 pages with repeating header and footer
    pages = []
    for i in range(3):
        elements = [
            create_element(f"h_{i}", "paragraph", i, 5, 10, "CONFIDENTIAL DOCUMENT"),
            create_element(f"p_{i}", "paragraph", i, 50, 60, f"Some random text on page {i}."),
            create_element(f"f_{i}", "paragraph", i, 950, 960, "Page Footer"),
            create_element(f"pn_{i}", "paragraph", i, 960, 970, str(i + 1)),
        ]
        pages.append(Page(physical_page_number=i, width=800, height=1000, elements=elements))

    context = PipelineContext(source_path="test", source_type="test", pages=pages)
    
    # 0.3 freq threshold means it needs to appear on 1 page (0.33) to be header/footer.
    # Our repeating texts appear on all 3 pages.
    stage = CleanupStage(header_footer_threshold_ratio=0.1, header_footer_freq_threshold=0.3)
    result = stage.run(context)
    
    for i in range(3):
        # Header
        assert result.pages[i].elements[0].type == "header"
        assert result.pages[i].elements[0].ignored is True
        
        # Body
        assert result.pages[i].elements[1].type == "paragraph"
        assert result.pages[i].elements[1].ignored is False
        
        # Footer
        assert result.pages[i].elements[2].type == "footer"
        assert result.pages[i].elements[2].ignored is True
        
        # Page Number
        assert result.pages[i].elements[3].type == "page_number"
        assert result.pages[i].elements[3].ignored is True

def test_paragraph_merging():
    # Create 2 pages
    p1_elements = [
        create_element("p1_1", "paragraph", 0, 50, 60, "This is a normal paragraph."),
        create_element("p1_2", "paragraph", 0, 80, 90, "This paragraph is split across"),
    ]
    p2_elements = [
        create_element("p2_1", "paragraph", 1, 50, 60, "two pages and continues here."),
        create_element("p2_2", "paragraph", 1, 80, 90, "Another normal paragraph."),
    ]
    
    pages = [
        Page(physical_page_number=0, width=800, height=1000, elements=p1_elements),
        Page(physical_page_number=1, width=800, height=1000, elements=p2_elements),
    ]

    context = PipelineContext(source_path="test", source_type="test", pages=pages)
    stage = CleanupStage()
    result = stage.run(context)
    
    # p1_2 should continue to p2_1
    assert result.pages[0].elements[1].metadata.get("continues_to") == "p2_1"
    assert result.pages[1].elements[0].metadata.get("continued_from") == "p1_2"
    
    # p1_1 and p2_2 should have no continues_to/continued_from
    assert "continues_to" not in result.pages[0].elements[0].metadata
    assert "continued_from" not in result.pages[1].elements[1].metadata
