from app.knowledge.rag.chunk_index import index_document

STANDARDS_BODIES = [
    "GAMP 5", "ASTM E2500", "ISPE Baseline Guides", "PDA Technical Reports",
    "ISO Standards", "IEC Standards", "ISA Standards",
]

COLLECTION = "industry_standards"


def ingest(standard: str, title: str, text: str, source_url: str = "") -> int:
    if standard not in STANDARDS_BODIES:
        raise ValueError(f"Unknown standards body: {standard}")
    return index_document(
        COLLECTION, text, metadata={"standard": standard, "title": title, "source_url": source_url},
    )
