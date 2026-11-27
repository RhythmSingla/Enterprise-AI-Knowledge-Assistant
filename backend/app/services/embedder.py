from fastembed import TextEmbedding

from app.core.config import settings

_embedding_model: TextEmbedding | None = None # local ONNX embedding engine


def get_embedding_model() -> TextEmbedding:
    """Lazy-loads and caches the ONNX embedding model in memory once per process."""
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = TextEmbedding(
            model_name=settings.EMBEDDING_MODEL_NAME
        )
    return _embedding_model


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    model = get_embedding_model()
    # Convert NumPy arrays to standard Python float lists for pgvector compatibility
    vectors = [vector.tolist() for vector in model.embed(texts)]

    if vectors and len(vectors[0]) != settings.EMBEDDING_DIMENSION:
        raise ValueError(
            f"Expected embedding dimension {settings.EMBEDDING_DIMENSION}, got {len(vectors[0])}."
        )

    return vectors


def embed_query(query: str) -> list[float]:
    cleaned = query.strip()
    if not cleaned:
        raise ValueError("Query text cannot be empty.")
    return embed_texts([cleaned])[0]