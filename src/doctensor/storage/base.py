"""Abstract FileStore interface."""
from abc import ABC, abstractmethod
from pathlib import Path


class FileStore(ABC):
    @abstractmethod
    def save(self, job_id: str, filename: str, data: bytes) -> str:
        """Persist *data* and return a resolvable location string."""

    @abstractmethod
    def load(self, location: str) -> bytes:
        """Load bytes from a previously saved location."""

    @abstractmethod
    def save_result(self, job_id: str, result_json: str) -> str:
        """Persist a JSON result string and return its location."""

    @abstractmethod
    def load_result(self, location: str) -> str:
        """Load a previously saved JSON result string."""
