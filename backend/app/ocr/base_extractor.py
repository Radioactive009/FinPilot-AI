from abc import ABC, abstractmethod
from typing import List
from app.schemas.ocr import DocumentText


class BaseExtractor(ABC):
    @abstractmethod
    def extract_text(self, file_path: str) -> List[DocumentText]:
        """
        Extracts text from a document and returns a list of DocumentText objects (one per page).
        """
        pass
