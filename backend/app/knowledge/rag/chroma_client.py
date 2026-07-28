from functools import lru_cache
from typing import Any

from app.config import get_settings


@lru_cache
def get_chroma_client() -> Any:
    """Imports chromadb lazily so the rest of the app can boot even if chromadb
    (and its onnxruntime dependency) isn't installed for the current Python version.
    """
    import chromadb

    settings = get_settings()
    return chromadb.PersistentClient(path=settings.chroma_persist_dir)


def get_collection(name: str) -> Any:
    from app.knowledge.rag.embeddings import embedding_function

    client = get_chroma_client()
    return client.get_or_create_collection(name=name, embedding_function=embedding_function())
