"""
Stage 1 — Ingest
Validates uploaded files, classifies asset types, persists records,
then triggers Stage 2 (parse).
"""
import logging
from typing import Any

from celery import shared_task
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.job import Job, JobStatus
from app.models.asset import Asset, AssetType
from app.services import storage_service
from app.utils.helpers import ALLOWED_IMAGE_MIME, ALLOWED_DOC_MIME

log = logging.getLogger(__name__)


def _classify(mime_type: str, filename: str) -> AssetType:
    name_lower = filename.lower()
    if mime_type in ALLOWED_DOC_MIME or "brochure" in name_lower or "spec" in name_lower:
        return AssetType.BROCHURE
    if "floor" in name_lower or "plan" in name_lower or "cad" in name_lower:
        return AssetType.FLOOR_PLAN
    return AssetType.PHOTO


@shared_task(bind=True, name="app.workers.ingest.run", max_retries=3)
def run(self, job_id: str) -> dict[str, Any]:
    import asyncio
    return asyncio.run(_run_async(self, job_id))


async def _run_async(task: Any, job_id: str) -> dict[str, Any]:
    async with AsyncSessionLocal() as db:
        job = await db.get(Job, job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")

        job.status = JobStatus.INGESTING
        job.current_stage = "ingest"
        job.progress_pct = 5
        await db.commit()

        try:
            # Validate all uploaded assets exist in S3
            missing = []
            for asset in job.assets:
                if asset.asset_type in (AssetType.RENDER, AssetType.NARRATION,
                                        AssetType.VIDEO_RAW, AssetType.VIDEO_FINAL):
                    continue
                if not storage_service.key_exists(asset.s3_key):
                    missing.append(asset.s3_key)

            if missing:
                raise FileNotFoundError(f"Missing S3 assets: {missing}")

            # Re-classify assets based on filename/mime
            for asset in job.assets:
                if asset.asset_type == AssetType.PHOTO:
                    asset.asset_type = _classify(asset.mime_type, asset.original_filename)

            job.progress_pct = 20
            await db.commit()

            manifest = {
                "job_id": job_id,
                "floor_plan_keys": [a.s3_key for a in job.assets if a.asset_type == AssetType.FLOOR_PLAN],
                "brochure_keys": [a.s3_key for a in job.assets if a.asset_type == AssetType.BROCHURE],
                "photo_keys": [a.s3_key for a in job.assets if a.asset_type == AssetType.PHOTO],
            }

            log.info("Ingest complete for job %s", job_id)
            return manifest

        except Exception as exc:
            job.status = JobStatus.FAILED
            job.error_message = str(exc)
            await db.commit()
            raise task.retry(exc=exc, countdown=30)
