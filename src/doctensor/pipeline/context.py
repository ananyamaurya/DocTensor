from dataclasses import dataclass, field
from typing import Any

from doctensor.ir.models import Document, Page


@dataclass
class PipelineContext:
    source_path: str
    source_type: str

    raw_document: Any | None = None
    pages: list[Page] = field(default_factory=list)

    detected_elements: list[Any] = field(default_factory=list)

    document: Document | None = None

    debug: dict[str, Any] = field(default_factory=dict)
