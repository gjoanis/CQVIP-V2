from app.parsers.structured_document import StructuredDocumentParser


class PQParser(StructuredDocumentParser):
    """Parser for Performance Qualification documents."""

    EXPECTED_SECTIONS = ['Purpose', 'Scope', 'Performance Criteria', 'Test Runs', 'Statistical Analysis', 'Acceptance Criteria']
