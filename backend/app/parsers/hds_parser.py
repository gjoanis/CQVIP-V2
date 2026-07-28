from app.parsers.structured_document import StructuredDocumentParser


class HDSParser(StructuredDocumentParser):
    """Parser for Hardware Design Specification documents."""

    EXPECTED_SECTIONS = ['Purpose', 'Scope', 'Equipment List', 'Instrumentation', 'Wiring', 'Panel Layout']
