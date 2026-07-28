from app.parsers.structured_document import StructuredDocumentParser


class ReportParser(StructuredDocumentParser):
    """Parser for Generic Validation Summary Report documents."""

    EXPECTED_SECTIONS = ['Purpose', 'Scope', 'Summary of Results', 'Deviations', 'Conclusion', 'Approval']
