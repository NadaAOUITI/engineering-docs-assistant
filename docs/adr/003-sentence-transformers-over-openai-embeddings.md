# ADR 003: Use sentence-transformers locally instead of OpenAI’s embedding API

## Context

Chunk text must be turned into dense vectors before storage in pgvector. OpenAI and other hosted APIs offer embedding models with strong quality and no GPU setup: send text, receive a vector, pay per token. That minimizes local dependencies and keeps embedding quality aligned with what many production systems use.

The tradeoff is ongoing cost and coupling. Every chunk and every query-time embedding incurs API latency and billing. The system also depends on a third-party network path for a step that runs repeatedly during indexing and at query time. For a portfolio project meant to run on a laptop or a small VM with low document volume, that dependency is heavier than the data size justifies.

## Decision

Use sentence-transformers with the all-mpnet-base-v2 model running on the same machine as the Celery worker (and, at query time, the API process). It produces 768-dimensional vectors, which match the pgvector column width in the schema.

## Consequences

There is no per-token bill and no API key rotation for embeddings. Embeddings stay inside the trust boundary of the deployment. Cold start and model load add memory and startup time on the worker; CPU or GPU time is local instead of metered remotely. Quality may differ from OpenAI’s latest embedding models; closing that gap would mean either changing models or accepting the cost and dependency of a hosted API.
