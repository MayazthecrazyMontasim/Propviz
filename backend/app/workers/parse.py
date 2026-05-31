"""
Stage 2 — Parse
Runs Claude Vision on floor plan + brochure images to extract:
- Structured room data (name, dimensions, features)
- Property selling points and specs
Then triggers Stage 3 (reconstruct).
"""
import logging
from typing import Any

from celery import shared_task

from app.core.database import AsyncSessionLocal
from app.models.job import Job, JobStatus
from app.services import claude_service, storage_service

log = logging.getLogger(__name__)

# MIME types for images accepted by Claude Vision
_VISION_MIME = {"image/jpeg", "image/png", "image/webp", "image/gif"}


@shared_task(bind=True, name="app.workers.parse.run", max_retries=3)
def run(self, job_id: str, manifest: dict[str, Any]) -> dict[str, Any]:
    import asyncio
    return asyncio.run(_run_async(self, job_id, manifest))


async def _run_async(task, job_id: str, manifest: dict[str, Any]) -> dict[str, Any]:
    async with AsyncSessionLocal() as db:
        job = await db.get(Job, job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")

        job.status = JobStatus.PARSING
        job.current_stage = "parse"
        job.progress_pct = 25
        await db.commit()

        try:
            rooms: list[dict] = []
            brochure_data: dict = {}

            # Parse each floor plan image
            for key in manifest.get("floor_plan_keys", []):
                image_bytes = storage_service.download_bytes(key)
                mime = _infer_mime(key)
                if mime not in _VISION_MIME:
                    log.warning("Skipping floor plan %s — unsupported mime %s", key, mime)
                    continue
                extracted = await claude_service.parse_floor_plan(image_bytes, mime)
                rooms.extend(extracted)

            job.progress_pct = 40

            # Parse brochure images/PDFs for selling points
            for key in manifest.get("brochure_keys", []):
                mime = _infer_mime(key)
                if mime not in _VISION_MIME:
                    log.warning("Skipping brochure %s — not a vision-compatible image", key)
                    continue
                image_bytes = storage_service.download_bytes(key)
                data = await claude_service.parse_brochure(image_bytes, mime)
                brochure_data.update(data)

            job.progress_pct = 55
            job.parsed_rooms = {"rooms": rooms, "brochure": brochure_data}
            await db.commit()

            result = {"job_id": job_id, "rooms": rooms, "brochure": brochure_data}
            log.info("Parse complete for job %s — %d rooms found", job_id, len(rooms))
            return result

        except Exception as exc:
            job.status = JobStatus.FAILED
            job.error_message = str(exc)
            await db.commit()
            raise task.retry(exc=exc, countdown=60)


def _infer_mime(s3_key: str) -> str:
    import mimetypes
    mime, _ = mimetypes.guess_type(s3_key)
    return mime or "application/octet-stream"
