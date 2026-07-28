from app.parsers.structured_document import StructuredDocumentParser


class CommissioningParser(StructuredDocumentParser):
    """Parser for Commissioning Record documents."""

    EXPECTED_SECTIONS = ['Purpose', 'Scope', 'Pre-Commissioning Checks', 'Commissioning Activities', 'Punch List']
