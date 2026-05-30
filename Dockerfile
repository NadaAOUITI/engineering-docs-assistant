# Container image for the FastAPI API and Celery worker (same deps, different command).

FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
# Force CPU-only PyTorch to avoid 1GB CUDA downloads
ENV PIP_EXTRA_INDEX_URL=https://download.pytorch.org/whl/cpu

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY scripts ./scripts
RUN chmod +x scripts/*.sh

# Railway sets PORT; start-api.sh reads it. Override for worker in Railway service settings.
CMD ["bash", "scripts/start-api.sh"]
