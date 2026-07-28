from app.parsers.structured_document import StructuredDocumentParser


class URSParser(StructuredDocumentParser):
    """Parser for User Requirements Specification documents."""

    EXPECTED_SECTIONS = ['Purpose', 'Scope', 'User Requirements', 'Regulatory Requirements', 'Glossary']
