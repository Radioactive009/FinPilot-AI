from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseParser(ABC):
    @abstractmethod
    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        Parses a document file and returns a dictionary of extracted values.
        """
        pass
