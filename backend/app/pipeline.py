"""
Standalone pipeline runner — executes all 5 stages sequentially as an
asyncio task in the same event loop as the API server (uvicorn).
No threads, no separate event loops, no Redis/Celery required.
"""
import asyncio
import logging

log = logging.getLogger(__name__)


class _MockTask:
    """Minimal Celery task stand-in so worker _run_async functions work."""
    def retry(self, exc=None, **kwargs):
        raise exc


async def run(job_id: str) -> None:
    """Run the full 5-stage pipeline as an asyncio coroutine."""
    mock = _MockTask()

    from app.workers.ingest import _run_async as ingest_async
    from app.workers.parse import _run_async as parse_async
    from app.workers.reconstruct import _run_async as reconstruct_async
    from app.workers.synthesize import _run_async as synthesize_async
    from app.workers.postprocess import _run_async as postprocess_async

    try:
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

    except Exception as exc:
        log.error("PIPELINE FAILED job=%s error=%s", job_id, exc, exc_info=True)
        # Fallback: mark the job as failed if a stage didn't already do it
        try:
            from app.core.database import AsyncSessionLocal
            from app.models.job import Job, JobStatus
            async with AsyncSessionLocal() as db:
                job = await db.get(Job, job_id)
                if job and job.status not in (JobStatus.COMPLETE, JobStatus.FAILED):
                    job.status = JobStatus.FAILED
                    job.error_message = f"Pipeline error: {exc}"
                    await db.commit()
        except Exception as db_exc:
            log.error("PIPELINE could not update job status: %s", db_exc)
