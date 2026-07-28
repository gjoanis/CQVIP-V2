from app.parsers.structured_document import StructuredDocumentParser


class SDSParser(StructuredDocumentParser):
    """Parser for Software Design Specification documents."""

    EXPECTED_SECTIONS = ['Purpose', 'Scope', 'Software Architecture', 'Modules', 'Data Flow', 'Alarms and Interlocks']
