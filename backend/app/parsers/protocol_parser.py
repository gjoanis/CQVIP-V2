from app.parsers.structured_document import StructuredDocumentParser


class ProtocolParser(StructuredDocumentParser):
    """Parser for Generic Validation Protocol documents."""

    EXPECTED_SECTIONS = ['Purpose', 'Scope', 'Roles and Responsibilities', 'Test Steps', 'Approval']
