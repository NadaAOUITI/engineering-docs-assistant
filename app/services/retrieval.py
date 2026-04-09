# pgvector similarity search and prompt assembly (user_id filter required on every search).

def retrieve_relevant_chunks(
    user_id: int,
    question_embedding: list[float],
    *,
    limit: int = 5,
) -> list[dict]:
    """Stub: nearest-neighbor search on Chunk.embedding with WHERE user_id = :user_id."""
    raise NotImplementedError


def answer_with_citations(
    user_id: int,
    question: str,
    retrieved_chunks: list[dict],
) -> tuple[str, list[int]]:
    """Stub: call Groq with context, return answer and cited chunk ids."""
    raise NotImplementedError
