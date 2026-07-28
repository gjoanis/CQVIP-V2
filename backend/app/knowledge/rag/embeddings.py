from functools import lru_cache


@lru_cache
def embedding_function():
    """Default local embedding model (all-MiniLM-L6-v2 via ONNX, runs offline).

    Swap for OpenAIEmbeddingFunction / a hosted embedding API if you need higher
    quality or multilingual support -- everything downstream only depends on this
    returning a chromadb-compatible EmbeddingFunction.
    """
    from chromadb.utils import embedding_functions

    return embedding_functions.DefaultEmbeddingFunction()
