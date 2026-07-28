from app.parsers.structured_document import StructuredDocumentParser


class IQParser(StructuredDocumentParser):
    """Parser for Installation Qualification documents."""

    EXPECTED_SECTIONS = ['Purpose', 'Scope', 'Installation Verification', 'Documentation Review', 'Component Verification']
