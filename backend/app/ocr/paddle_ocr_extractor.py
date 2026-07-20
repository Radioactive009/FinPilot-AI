from typing import List
import os
from app.ocr.base_extractor import BaseExtractor
from app.schemas.ocr import DocumentText
from app.core.logging import logger


class PaddleOCRExtractor(BaseExtractor):
    def __init__(self):
        # Deferred import to allow testing environments without full paddleocr installations
        try:
            from paddleocr import PaddleOCR
            # Initialize PaddleOCR engine (English model, angle classifier enabled)
            self.ocr = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
        except ImportError:
            self.ocr = None
            logger.warning("paddleocr library is not installed in the current python runtime environment")

    def extract_text(self, file_path: str) -> List[DocumentText]:
        logger.info("Starting text extraction with PaddleOCR", file_path=file_path)
        
        if self.ocr is None:
            # Fallback for mock/testing setup when library is missing
            logger.info("Simulating PaddleOCR extraction due to missing library")
            return [
                DocumentText(
                    page_number=1,
                    raw_text="Simulated PaddleOCR Extracted Text content",
                    confidence=0.9850,
                    metadata={"simulated": True, "engine": "PaddleOCR"}
                )
            ]

        try:
            # paddleocr takes image paths or pdf paths
            result = self.ocr.ocr(file_path, cls=True)
            
            pages_text: List[DocumentText] = []
            
            # paddleocr output structure:
            # result = [ [ [ [box], (text, confidence) ], ... ], ... ] (one list per page/image)
            if not result or result[0] is None:
                # Handle empty documents
                return [
                    DocumentText(
                        page_number=1,
                        raw_text="",
                        confidence=0.0,
                        metadata={"empty": True}
                    )
                ]

            for page_idx, page_result in enumerate(result):
                raw_text_parts = []
                confidences = []
                boxes = []

                if page_result:
                    for line in page_result:
                        box = line[0]  # list of 4 points: [[x0,y0], [x1,y1], [x2,y2], [x3,y3]]
                        text, confidence = line[1]
                        raw_text_parts.append(text)
                        confidences.append(confidence)
                        boxes.append({"text": text, "box": box, "confidence": float(confidence)})

                avg_conf = sum(confidences) / len(confidences) if confidences else 1.0
                pages_text.append(
                    DocumentText(
                        page_number=page_idx + 1,
                        raw_text="\n".join(raw_text_parts),
                        confidence=float(avg_conf),
                        metadata={
                            "boxes": boxes,
                            "engine": "PaddleOCR"
                        }
                    )
                )
            logger.info("Successfully extracted text using PaddleOCR", file_path=file_path, pages=len(pages_text))
            return pages_text
        except Exception as e:
            logger.error("Failed to extract text using PaddleOCR", file_path=file_path, error=str(e))
            raise RuntimeError(f"PaddleOCR extraction failed: {str(e)}")
