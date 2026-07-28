from app.parsers.structured_document import StructuredDocumentParser


class OQParser(StructuredDocumentParser):
    """Parser for Operational Qualification documents."""

    EXPECTED_SECTIONS = ['Purpose', 'Scope', 'Test Cases', 'Operational Parameters', 'Acceptance Criteria']
