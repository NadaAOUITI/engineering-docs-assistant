# Parse uploads, split text, compute embeddings, and persist chunks (invoked by worker).

def chunk_and_enqueue(document_id: int) -> None:
    """Stub: validate path, split content, enqueue Celery task to index_document."""
    raise NotImplementedError


def index_document_sync(document_id: int) -> None:
    """Stub: same pipeline as worker task for local/dev without Celery."""
    raise NotImplementedError
