# ADR 002: Handle document indexing in a Celery worker instead of the FastAPI request

## Context

After upload, a document must be read from disk, text extracted, split into chunks, embedded, and written to the database. That work scales with file size and page count. Doing it inside the same HTTP handler that accepted the upload is the simplest deployment story: one process, no queue, no extra moving parts.

The cost is response time. A large PDF can easily spend thirty seconds or more on extraction and embedding before the client gets a reply, assuming CPU is available. HTTP clients and reverse proxies often time out first. Even when they do not, tying up a worker thread for that long reduces throughput for unrelated requests on the same instance.

## Decision

FastAPI records the document, stores the file, enqueues an index_document task, and returns immediately with a pending status. A Celery worker performs extraction, chunking, embedding, and persistence, then updates status to indexed or failed.

## Consequences

Running Redis and a worker process is more to configure, monitor, and deploy than a single web container. Failures can surface asynchronously: the client must poll or subscribe to status if it needs to know when indexing finished. In exchange, upload latency stays predictable, the API stays responsive under bursty uploads, and long-running work can be scaled by adding workers without multiplying HTTP front ends.
