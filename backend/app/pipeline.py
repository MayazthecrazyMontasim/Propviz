"""
Standalone pipeline runner — executes all 5 stages sequentially.
Uses print() so output is guaranteed visible in Railway logs.
"""
import sys


class _MockTask:
    def retry(self, exc=None, **kwargs):
        raise exc


async def run(job_id: str) -> None:
    """Run the full 5-stage pipeline."""
    print(f"[PIPELINE] START job={job_id}", flush=True)
    sys.stdout.flush()

    try:
        mock = _MockTask()

        # Import workers inside try so import errors are caught and logged
        print(f"[PIPELINE] importing workers", flush=True)
        from app.workers.ingest import _run_async as ingest_async
        from app.workers.parse import _run_async as parse_async
        from app.workers.reconstruct import _run_async as reconstruct_async
        from app.workers.synthesize import _run_async as synthesize_async
        from app.workers.postprocess import _run_async as postprocess_async
        print(f"[PIPELINE] workers imported OK", flush=True)

        print(f"[PIPELINE] stage=ingest job={job_id}", flush=True)
        manifest = await ingest_async(mock, job_id)
        print(f"[PIPELINE] ingest OK manifest={manifest}", flush=True)

        print(f"[PIPELINE] stage=parse job={job_id}", flush=True)
        parse_result = await parse_async(mock, job_id, manifest)
        print(f"[PIPELINE] parse OK rooms={len(parse_result.get('rooms', []))}", flush=True)

        print(f"[PIPELINE] stage=reconstruct job={job_id}", flush=True)
        reconstruct_result = await reconstruct_async(mock, job_id, parse_result)
        print(f"[PIPELINE] reconstruct OK", flush=True)

        print(f"[PIPELINE] stage=synthesize job={job_id}", flush=True)
        synthesize_result = await synthesize_async(mock, job_id, reconstruct_result)
        print(f"[PIPELINE] synthesize OK", flush=True)

        print(f"[PIPELINE] stage=postprocess job={job_id}", flush=True)
        await postprocess_async(mock, job_id, synthesize_result)
        print(f"[PIPELINE] COMPLETE job={job_id}", flush=True)

    except Exception as exc:
        print(f"[PIPELINE] FAILED job={job_id} error={exc}", flush=True)
        import traceback
        traceback.print_exc()
        # Fallback: mark job as failed if a stage didn't already do it
        try:
            from app.core.database import AsyncSessionLocal
            from app.models.job import Job, JobStatus
            async with AsyncSessionLocal() as db:
                job = await db.get(Job, job_id)
                if job and job.status not in (JobStatus.COMPLETE, JobStatus.FAILED):
                    job.status = JobStatus.FAILED
                    job.error_message = f"Pipeline error: {exc}"
                    await db.commit()
                    print(f"[PIPELINE] marked job {job_id} as FAILED", flush=True)
        except Exception as db_exc:
            print(f"[PIPELINE] could not update job status: {db_exc}", flush=True)
