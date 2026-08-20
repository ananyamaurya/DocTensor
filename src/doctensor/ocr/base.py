from abc import ABC, abstractmethod
from typing import Any
from PIL import Image

from doctensor.ir.models import BoundingBox, Element


class OCRBackend(ABC):
    @abstractmethod
    def recognize(self, image: Image.Image, page_number: int) -> list[Element]:
        """Recognizes text in an image and returns a list of Elements."""
        raise NotImplementedError
