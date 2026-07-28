import csv

from app.parsers.base import BaseParser, ParseResult


class CSVParser(BaseParser):
    def parse(self, file_path: str) -> ParseResult:
        with open(file_path, newline="", encoding="utf-8") as fh:
            rows = list(csv.reader(fh))
        text = "\n".join(", ".join(row) for row in rows)
        return ParseResult(raw_text=text, metadata={"row_count": len(rows)})
