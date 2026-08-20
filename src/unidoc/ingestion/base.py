from abc import ABC, abstractmethod
from typing import Any

from unidoc.ir.models import DocumentMetadata
from unidoc.pipeline.context import PipelineContext


class DocumentIngestor(ABC):
    @abstractmethod
    def ingest(self, file_path: str) -> PipelineContext:
        """Reads a file and creates the initial PipelineContext."""
        raise NotImplementedError
