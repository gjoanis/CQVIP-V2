from lxml import etree

from app.parsers.base import BaseParser, ParseResult


class XMLParser(BaseParser):
    def parse(self, file_path: str) -> ParseResult:
        tree = etree.parse(file_path)
        text = etree.tostring(tree, pretty_print=True, encoding="unicode")
        return ParseResult(raw_text=text, metadata={"root_tag": tree.getroot().tag})
