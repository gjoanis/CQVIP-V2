import os

from app.parsers.base import BaseParser
from app.parsers.commissioning_parser import CommissioningParser
from app.parsers.csv_parser import CSVParser
from app.parsers.docx_parser import DOCXParser
from app.parsers.ds_parser import DSParser
from app.parsers.excel_parser import ExcelParser
from app.parsers.fat_parser import FATParser
from app.parsers.fs_parser import FSParser
from app.parsers.hds_parser import HDSParser
from app.parsers.iq_parser import IQParser
from app.parsers.json_parser import JSONParser
from app.parsers.oq_parser import OQParser
from app.parsers.pdf_parser import PDFParser
from app.parsers.pq_parser import PQParser
from app.parsers.protocol_parser import ProtocolParser
from app.parsers.report_parser import ReportParser
from app.parsers.sat_parser import SATParser
from app.parsers.sds_parser import SDSParser
from app.parsers.urs_parser import URSParser
from app.parsers.xml_parser import XMLParser

# Add new file-type parsers here (see 'Future Parsers' in the architecture diagram).
_BY_EXTENSION: dict[str, type[BaseParser]] = {
    ".pdf": PDFParser, ".docx": DOCXParser, ".xlsx": ExcelParser, ".xls": ExcelParser,
    ".csv": CSVParser, ".xml": XMLParser, ".json": JSONParser,
}

# doc_type values as stored on app.models.document.Document.doc_type
_BY_DOC_TYPE: dict[str, type[BaseParser]] = {
    "URS": URSParser, "FS": FSParser, "DS": DSParser, "HDS": HDSParser, "SDS": SDSParser,
    "FAT": FATParser, "SAT": SATParser, "IQ": IQParser, "OQ": OQParser, "PQ": PQParser,
    "COMMISSIONING": CommissioningParser, "PROTOCOL": ProtocolParser, "REPORT": ReportParser,
}


class ParserFactory:
    @staticmethod
    def for_file(file_path: str, doc_type: str | None = None) -> BaseParser:
        """doc_type (e.g. 'URS', 'OQ') takes priority since it determines expected
        sections; falls back to plain file-extension parsing otherwise."""
        if doc_type and doc_type.upper() in _BY_DOC_TYPE:
            return _BY_DOC_TYPE[doc_type.upper()]()
        ext = os.path.splitext(file_path)[1].lower()
        parser_cls = _BY_EXTENSION.get(ext)
        if parser_cls is None:
            raise ValueError(f"No parser registered for extension: {ext}")
        return parser_cls()
