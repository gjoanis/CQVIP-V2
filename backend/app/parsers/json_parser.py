import json

from app.parsers.base import BaseParser, ParseResult


class JSONParser(BaseParser):
    def parse(self, file_path: str) -> ParseResult:
        with open(file_path, encoding="utf-8") as fh:
            data = json.load(fh)
        return ParseResult(raw_text=json.dumps(data, indent=2), metadata={"type": type(data).__name__})
