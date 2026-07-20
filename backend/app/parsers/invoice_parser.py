import os
from typing import Any, Dict
from app.parsers.base_parser import BaseParser


class InvoiceParser(BaseParser):
    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        Parses an invoice file and returns simulated extracted structure.
        """
        content = b""
        if os.path.exists(file_path):
            try:
                with open(file_path, "rb") as f:
                    content = f.read().lower()
            except Exception:
                pass

        # Simulate missing required fields case based on file content bytes
        if b"missing_fields" in content or b"missing fields" in content:
            return {
                "invoice_number": None,
                "vendor_name": "Acme Corp",
                "invoice_date": "2026-07-20",
                "due_date": "2026-08-20",
                "currency": "USD",
                "subtotal": 100.0,
                "tax": 10.0,
                "total_amount": 110.0,
                "items": [
                    {
                        "description": "Consulting Services",
                        "quantity": 1,
                        "unit_price": 100.0,
                        "amount": 100.0
                    }
                ]
            }

        # Simulate duplicate check case based on file content bytes
        if b"duplicate" in content:
            return {
                "invoice_number": "INV-DUP-999",
                "vendor_name": "Duplicate Vendor LLC",
                "invoice_date": "2026-07-20",
                "due_date": "2026-08-20",
                "currency": "USD",
                "subtotal": 500.0,
                "tax": 50.0,
                "total_amount": 550.0,
                "items": [
                    {
                        "description": "Premium License Fees",
                        "quantity": 5,
                        "unit_price": 100.0,
                        "amount": 500.0
                    }
                ]
            }

        # Successful standard extraction simulation
        return {
            "invoice_number": "INV-2026-0001",
            "vendor_name": "Standard Vendor Inc",
            "invoice_date": "2026-07-20",
            "due_date": "2026-08-20",
            "currency": "USD",
            "subtotal": 1000.0,
            "tax": 100.0,
            "total_amount": 1100.0,
            "items": [
                {
                    "description": "Software Subscription",
                    "quantity": 2,
                    "unit_price": 400.0,
                    "amount": 800.0
                },
                {
                    "description": "Support Package",
                    "quantity": 1,
                    "unit_price": 200.0,
                    "amount": 200.0
                }
            ]
        }
