import sys
sys.path.append("src")
from PIL import Image, ImageDraw
from doctensor.ir.models import Element, BoundingBox, Page
from doctensor.pipeline.context import PipelineContext
from doctensor.math.pix2tex_backend import Pix2TexBackend
from doctensor.pipeline.math_stage import MathStage

import pytest

def test_pix2tex():
    print("Creating mock equation image...")
    img = Image.new('RGB', (200, 50), color = (255, 255, 255))
    d = ImageDraw.Draw(img)
    d.text((10,10), "E = mc^2", fill=(0,0,0))
    
    print("Initializing Pix2TexBackend...")
    backend = Pix2TexBackend()
    
    print("Running recognize...")
    result = backend.recognize(img)
    print(f"Result: {result}")

if __name__ == "__main__":
    test_pix2tex()
