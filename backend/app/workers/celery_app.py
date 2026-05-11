from celery import Celery
from app.core.config import settings

celery = Celery(
    "propviz",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "app.workers.ingest",
        "app.workers.parse",
        "app.workers.reconstruct",
        "app.workers.synthesize",
        "app.workers.postprocess",
    ],
)

celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    result_expires=86400,  # 24 hours
    task_routes={
        "app.workers.ingest.*": {"queue": "ingest"},
        "app.workers.parse.*": {"queue": "parse"},
        "app.workers.reconstruct.*": {"queue": "reconstruct"},
        "app.workers.synthesize.*": {"queue": "synthesize"},
        "app.workers.postprocess.*": {"queue": "postprocess"},
    },
)
