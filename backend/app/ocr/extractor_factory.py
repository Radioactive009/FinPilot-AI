import os
import fitz
from app.ocr.base_extractor import BaseExtractor
from app.ocr.pdf_text_extractor import PDFTextExtractor
from app.ocr.paddle_ocr_extractor import PaddleOCRExtractor
from app.core.logging import logger


class ExtractorFactory:
    @staticmethod
    def get_extractor(file_path: str) -> BaseExtractor:
        filename = os.path.basename(file_path).lower()
        ext = filename.split(".")[-1] if "." in filename else ""

        if ext == "pdf":
            # Determine if PDF is searchable
            if ExtractorFactory.is_searchable_pdf(file_path):
                logger.info("Searchable PDF detected. Routing to PDFTextExtractor.", file=filename)
                return PDFTextExtractor()
            else:
                logger.info("Scanned PDF detected. Routing to PaddleOCRExtractor.", file=filename)
                return PaddleOCRExtractor()
        elif ext in ["png", "jpg", "jpeg"]:
            logger.info("Image file detected. Routing to PaddleOCRExtractor.", file=filename)
            return PaddleOCRExtractor()
        else:
            # Fallback/Default for other parsed types
            logger.info("Routing generic format to PaddleOCRExtractor.", file=filename)
            return PaddleOCRExtractor()

    @staticmethod
    def is_searchable_pdf(file_path: str) -> bool:
        try:
            doc = fitz.open(file_path)
            # Scan first few pages for readable text characters
            for idx in range(min(5, len(doc))):
                page = doc.load_page(idx)
                if page.get_text().strip():
                    doc.close()
                    return True
            doc.close()
        except Exception as e:
            logger.warning("Error checking PDF searchability", file=file_path, error=str(e))
        return False
