# ADR 001: Store embeddings in PostgreSQL (pgvector) instead of Qdrant

## Context

This project is a portfolio-sized RAG backend: a single developer, moderate document volume, and a goal of keeping operational surface area small. Vector search must coexist with relational metadata (users, plans, documents, chunks, query history) and enforce row-level isolation by user_id on every similarity query.

Qdrant is a strong dedicated vector database (filtering, hybrid search, horizontal scaling). PostgreSQL with the pgvector extension provides approximate and exact nearest-neighbor search inside the same database that already holds users and foreign keys.

## Decision

Use PostgreSQL + pgvector as the only datastore for relational data and chunk embeddings.

## Consequences

**Positive**

- One system to run and back up: No separate vector service to version, secure, and monitor for this scale.
- Transactional consistency: Document rows and chunk rows (including embeddings) can be written in the same database transaction; deleting a document can cascade to chunks without cross-service orchestration.
- Simpler security model for isolation: Similarity search is a SQL query with WHERE user_id = :user_id, which maps directly to the non-negotiable rule that pgvector search must always filter by user.
- Cost and footprint: Fits a free-tier or small VM deployment without another managed service.

**Negative / tradeoffs**

- Scaling limits: Very large embedding corpora or extreme QPS may eventually warrant a specialized vector store or read replicas; that is out of scope for the current milestone.
- Index tuning: IVFFlat/HNSW parameters and EXPLAIN work differ from Qdrant's tuning knobs; performance work stays in PostgreSQL land.

## Alternatives considered

- Qdrant (or another external vector DB): Better for massive scale and vector-only workloads; adds sync complexity and another failure domain for a portfolio project that already standardizes on PostgreSQL.

## References

- pgvector: https://github.com/pgvector/pgvector
