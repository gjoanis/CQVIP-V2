"""One-off script to load the regulatory PDFs on the user's Desktop into the
RAG knowledge base. Run from backend/ with the .venv312 interpreter:

    .venv312/bin/python scripts/ingest_regulatory_docs.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.knowledge.regulatory_library import ingest
from app.parsers.pdf_parser import PDFParser

SOURCE_DIR = Path("/Users/garyjoanis/Desktop/Regulatory Docs")

DOCUMENTS = [
    ("2015-10_annex15_0.pdf", "EMA", "EU GMP Annex 15: Qualification and Validation (2015)"),
    ("annex11_01-2011_en_0.pdf", "EMA", "EU GMP Annex 11: Computerised Systems (2011)"),
    ("Data Integrity.pdf", "FDA",
     "Data Integrity and Compliance With Drug CGMP — Q&A Guidance for Industry (Dec 2018)"),
    ("Part-11--Electronic-Records--Electronic-Signatures---Scope-and-Application-(PDF).pdf", "FDA",
     "Part 11, Electronic Records; Electronic Signatures — Scope and Application"),
    ("Process-Validation--General-Principles-and-Practices.pdf", "FDA",
     "Process Validation: General Principles and Practices"),
    ("Q9R1QRM.pdf", "ICH", "ICH Q9(R1): Quality Risk Management"),
    ("Q12_EWG_Draft_Guideline.pdf", "ICH",
     "ICH Q12: Technical and Regulatory Considerations for Pharmaceutical Product Lifecycle Management (Draft)"),
]


def main() -> None:
    parser = PDFParser()
    for filename, body, title in DOCUMENTS:
        path = SOURCE_DIR / filename
        result = parser.parse(str(path))
        chunk_count = ingest(body, title, result.raw_text, source_url=filename)
        print(f"[{body}] {title}: {chunk_count} chunks ({result.metadata.get('page_count')} pages)")


if __name__ == "__main__":
    main()
