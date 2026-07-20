# Prompt templates for RAG and Agents analysis

INVOICE_ANALYSIS_PROMPT = """
You are an expert AI financial auditor. Analyze the following invoice text:
{text}
Extract the key fields, potential discrepancies, billing errors, or payment anomalies.
"""

EXPENSE_REPORT_PROMPT = """
Analyze the following expense report:
{text}
Validate it against standard compliance rules. Highlight any policy violations.
"""
