from doctensor.math.base import MathBackend
from PIL import Image

class Pix2TexBackend(MathBackend):
    def __init__(self):
        try:
            from pix2tex.cli import LatexOCR
            # LatexOCR initializes the model and weights
            self.model = LatexOCR()
        except ImportError:
            raise ImportError("pix2tex is not installed. Please install it with `pip install pix2tex`.")
        except Exception as e:
            # Handle possible torch/model loading issues gracefully if needed
            raise RuntimeError(f"Failed to initialize pix2tex model: {e}")

    def recognize(self, image: Image.Image) -> str:
        """
        Takes a cropped PIL Image of an equation and returns the LaTeX string.
        """
        # The LatexOCR instance is callable on a PIL Image
        return self.model(image)
