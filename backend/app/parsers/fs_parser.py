from app.parsers.structured_document import StructuredDocumentParser


class FSParser(StructuredDocumentParser):
    """Parser for Functional Specification documents."""

    EXPECTED_SECTIONS = ['Purpose', 'Scope', 'System Overview', 'Functional Requirements', 'Interfaces', 'Alarms']
