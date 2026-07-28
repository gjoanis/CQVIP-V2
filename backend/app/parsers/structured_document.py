import re

from app.parsers.base import BaseParser, ParseResult, Section
from app.parsers.docx_parser import DOCXParser
from app.parsers.pdf_parser import PDFParser

_HEADING_RE = re.compile(
    r"^\s*(\d+(\.\d+)*\s+[A-Z][^\n]{2,100}|[A-Z][A-Z0-9 /\-]{4,80})\s*$", re.MULTILINE
)


class StructuredDocumentParser(BaseParser):
    """Base for validation document parsers (URS/FS/DS/.../Protocol/Report).

    Delegates raw text extraction to PDFParser/DOCXParser by file extension, then
    splits the text into sections using a generic numbered/ALL-CAPS heading
    heuristic. Subclasses set EXPECTED_SECTIONS so app.ai.gap_analysis has
    something to check the extracted sections against.
    """

    EXPECTED_SECTIONS: list[str] = []

    def _raw_parser(self, file_path: str) -> BaseParser:
        return DOCXParser() if file_path.lower().endswith(".docx") else PDFParser()

    def parse(self, file_path: str) -> ParseResult:
        base_result = self._raw_parser(file_path).parse(file_path)
        sections = self._split_sections(base_result.raw_text)
        return ParseResult(raw_text=base_result.raw_text, sections=sections, metadata=base_result.metadata)

    @staticmethod
    def _split_sections(text: str) -> list[Section]:
        matches = list(_HEADING_RE.finditer(text))
        if not matches:
            return [Section(heading="Full Document", text=text)]
        sections = []
        for i, match in enumerate(matches):
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            sections.append(Section(heading=match.group(1).strip(), text=text[start:end].strip()))
        return sections
