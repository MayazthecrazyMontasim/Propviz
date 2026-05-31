#!/bin/bash
set -e

echo "=== Starting Celery worker ==="
celery -A app.workers.celery_app:celery worker \
  --loglevel=info \
  --queues=celery,ingest,parse,reconstruct,synthesize,postprocess \
  --concurrency=1 \
  --pool=solo &

CELERY_PID=$!
echo "=== Celery PID: $CELERY_PID ==="

echo "=== Running migrations ==="
alembic upgrade head

echo "=== Starting API server ==="
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
