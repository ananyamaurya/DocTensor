from typing import Literal, Any
from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    x0: float
    y0: float
    x1: float
    y1: float


class Span(BaseModel):
    type: Literal["text", "math"]
    text: str | None = None
    latex: str | None = None


class Element(BaseModel):
    id: str
    type: str
    page: int
    bbox: BoundingBox | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)
    source: str
    ignored: bool = False

    text: str | None = None
    spans: list[Span] = []
    latex: str | None = None

    metadata: dict[str, Any] = Field(default_factory=dict)


class Page(BaseModel):
    physical_page_number: int
    printed_page_number: str | None = None
    width: float
    height: float
    elements: list[Element] = []


class DocumentMetadata(BaseModel):
    title: str | None = None
    authors: list[str] = []
    language: str | None = None
    source_type: str
    page_count: int


class Document(BaseModel):
    schema_version: str = "1.0"
    metadata: DocumentMetadata
    pages: list[Page]
