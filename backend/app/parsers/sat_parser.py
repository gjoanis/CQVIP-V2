from app.parsers.structured_document import StructuredDocumentParser


class SATParser(StructuredDocumentParser):
    """Parser for Site Acceptance Test documents."""

    EXPECTED_SECTIONS = ['Purpose', 'Scope', 'Site Conditions', 'Test Cases', 'Acceptance Criteria', 'Deviations']
