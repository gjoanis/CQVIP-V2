from dataclasses import dataclass


@dataclass
class Citation:
    text: str
    metadata: dict
    distance: float | None = None

    @property
    def source_label(self) -> str:
        meta = self.metadata
        return meta.get("title") or meta.get("body") or meta.get("standard") or meta.get("category") or "unknown"


def citations_from_query_result(result: dict) -> list[Citation]:
    documents = (result.get("documents") or [[]])[0]
    metadatas = (result.get("metadatas") or [[]])[0]
    distances = (result.get("distances") or [[]])[0] if result.get("distances") else [None] * len(documents)
    return [
        Citation(text=doc, metadata=meta or {}, distance=dist)
        for doc, meta, dist in zip(documents, metadatas, distances)
    ]
