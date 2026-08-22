from abc import ABC, abstractmethod
from PIL import Image


class MathBackend(ABC):
    @abstractmethod
    def recognize(self, image: Image.Image) -> str:
        """
        Takes an image of a mathematical equation and returns the LaTeX representation.
        """
        raise NotImplementedError
