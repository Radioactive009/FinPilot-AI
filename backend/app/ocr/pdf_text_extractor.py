from typing import List
import fitz  # PyMuPDF
from app.ocr.base_extractor import BaseExtractor
from app.schemas.ocr import DocumentText
from app.core.logging import logger


class PDFTextExtractor(BaseExtractor):
    def extract_text(self, file_path: str) -> List[DocumentText]:
        """
        Extracts text from a digital searchable PDF using PyMuPDF.
        """
        logger.info("Starting text extraction with PyMuPDF", file_path=file_path)
        pages_text: List[DocumentText] = []
        
        try:
            doc = fitz.open(file_path)
            page_count = len(doc)
            doc_metadata = doc.metadata or {}

            for page_idx in range(page_count):
                page = doc.load_page(page_idx)
                text = page.get_text()
                
                pages_text.append(
                    DocumentText(
                        page_number=page_idx + 1,
                        raw_text=text,
                        confidence=1.0,  # Digital text has 100% confidence
                        metadata={
                            "page_count": page_count,
                            "doc_metadata": doc_metadata,
                            "rect": [page.rect.x0, page.rect.y0, page.rect.x1, page.rect.y1]
                        }
                    )
                )
            doc.close()
            logger.info("Successfully extracted text from digital PDF", file_path=file_path, pages=page_count)
            return pages_text
        except Exception as e:
            logger.error("Failed to extract text using PyMuPDF", file_path=file_path, error=str(e))
            raise RuntimeError(f"PyMuPDF extraction failed: {str(e)}")
