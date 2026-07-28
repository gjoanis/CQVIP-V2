from app.parsers.structured_document import StructuredDocumentParser


class DSParser(StructuredDocumentParser):
    """Parser for Design Specification documents."""

    EXPECTED_SECTIONS = ['Purpose', 'Scope', 'Hardware Design', 'Software Design', 'Configuration']
