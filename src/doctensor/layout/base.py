from abc import ABC, abstractmethod
from doctensor.pipeline.context import PipelineContext


class LayoutBackend(ABC):
    @abstractmethod
    def classify(self, context: PipelineContext):
        """
        Analyzes the context and assigns semantic layout types to Elements.
        Modifies the elements in place.
        """
        raise NotImplementedError
