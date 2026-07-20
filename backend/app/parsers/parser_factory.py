from app.models.document import DocumentType
from app.parsers.base_parser import BaseParser
from app.parsers.invoice_parser import InvoiceParser


class ParserFactory:
    @staticmethod
    def get_parser(document_type: DocumentType) -> BaseParser:
        if document_type == DocumentType.INVOICE:
            return InvoiceParser()
        else:
            raise ValueError(f"No parser implemented for document type: {document_type}")
