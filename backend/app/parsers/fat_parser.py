from app.parsers.structured_document import StructuredDocumentParser


class FATParser(StructuredDocumentParser):
    """Parser for Factory Acceptance Test documents."""

    EXPECTED_SECTIONS = ['Purpose', 'Scope', 'Test Prerequisites', 'Test Cases', 'Acceptance Criteria', 'Deviations']
