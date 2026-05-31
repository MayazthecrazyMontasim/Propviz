"""
Standalone pipeline runner — executes all 5 stages sequentially in a
background thread without requiring Celery or Redis.
"""
import asyncio
import logging
from typing import Any

log = logging.getLogger(__name__)


class _MockTask:
    """Minimal Celery task stand-in so worker _run_async functions work."""
    def retry(self, exc=None, **kwargs):
        raise exc


async def _run(job_id: str) -> None:
    mock = _MockTask()

    from app.workers.ingest import _run_async as ingest_async
    from app.workers.parse import _run_async as parse_async
    from app.workers.reconstruct import _run_async as reconstruct_async
    from app.workers.synthesize import _run_async as synthesize_async
    from app.workers.postprocess import _run_async as postprocess_async

    log.warning("PIPELINE stage=ingest job=%s", job_id)
    manifest = await ingest_async(mock, job_id)

    log.warning("PIPELINE stage=parse job=%s", job_id)
    parse_result = await parse_async(mock, job_id, manifest)

    log.warning("PIPELINE stage=reconstruct job=%s", job_id)
    reconstruct_result = await reconstruct_async(mock, job_id, parse_result)

    log.warning("PIPELINE stage=synthesize job=%s", job_id)
    synthesize_result = await synthesize_async(mock, job_id, reconstruct_result)

    log.warning("PIPELINE stage=postprocess job=%s", job_id)
    await postprocess_async(mock, job_id, synthesize_result)

    log.warning("PIPELINE complete job=%s", job_id)


def start_in_thread(job_id: str) -> None:
    """Run the full pipeline in a background thread."""
    import threading

    def _target():
        try:
            asyncio.run(_run(job_id))
        except Exception as exc:
            log.error("PIPELINE FAILED job=%s error=%s", job_id, exc, exc_info=True)

    t = threading.Thread(target=_target, daemon=True, name=f"pipeline-{job_id}")
    t.start()
