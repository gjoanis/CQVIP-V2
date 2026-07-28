from pypdf import PdfReader

from app.parsers.base import BaseParser, ParseResult


class PDFParser(BaseParser):
    def parse(self, file_path: str) -> ParseResult:
        reader = PdfReader(file_path)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        return ParseResult(raw_text=text, metadata={"page_count": len(reader.pages)})
