import fitz
from PIL import Image


def render_page(page: fitz.Page, dpi: int = 200) -> Image.Image:
    """
    Renders a fitz.Page to a PIL Image at the specified DPI.
    """
    zoom = dpi / 72.0
    matrix = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=matrix, alpha=False)
    
    # Convert PyMuPDF pixmap to PIL Image
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    return img
