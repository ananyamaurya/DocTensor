from abc import ABC, abstractmethod
from typing import Any

from doctensor.ir.models import DocumentMetadata
from doctensor.pipeline.context import PipelineContext


class DocumentIngestor(ABC):
    @abstractmethod
    def ingest(self, file_path: str) -> PipelineContext:
        """Reads a file and creates the initial PipelineContext."""
        raise NotImplementedError
