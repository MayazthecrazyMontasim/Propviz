"""
Stage 4 — Synthesize
Generates the narration audio via ElevenLabs, then chains to postprocess.
Video assembly (stitching clips + audio) happens in Stage 5.
"""
import logging
from typing import Any

from celery import shared_task

from app.core.database import AsyncSessionLocal
from app.models.job import Job, JobStatus
from app.models.asset import Asset, AssetType
from app.services import claude_service, elevenlabs_service, storage_service
from app.utils.helpers import output_s3_key

log = logging.getLogger(__name__)


def _build_property_summary(brochure: dict, rooms: list[dict]) -> str:
    lines = []
    if brochure.get("project_name"):
        lines.append(f"Project: {brochure['project_name']}")
    if brochure.get("developer"):
        lines.append(f"Developer: {brochure['developer']}")
    if brochure.get("location"):
        lines.append(f"Location: {brochure['location']}")
    if rooms:
        room_summary = ", ".join(
            f"{r['name']} ({r.get('width_ft', '?')}x{r.get('height_ft', '?')} ft)"
            for r in rooms[:5]
        )
        lines.append(f"Rooms: {room_summary}")
    if brochure.get("amenities"):
        lines.append(f"Amenities: {', '.join(brochure['amenities'][:5])}")
    if brochure.get("handover_date"):
        lines.append(f"Handover: {brochure['handover_date']}")
    if brochure.get("price_range"):
        lines.append(f"Price: {brochure['price_range']}")
    return "\n".join(lines)


@shared_task(bind=True, name="app.workers.synthesize.run", max_retries=3)
def run(self, job_id: str, reconstruct_result: dict[str, Any]) -> dict[str, Any]:
    import asyncio
    return asyncio.run(_run_async(self, job_id, reconstruct_result))


async def _run_async(task, job_id: str, data: dict[str, Any]) -> dict[str, Any]:
    async with AsyncSessionLocal() as db:
        job = await db.get(Job, job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")

        job.status = JobStatus.SYNTHESIZING
        job.current_stage = "synthesize"
        job.progress_pct = 80
        await db.commit()

        try:
            brochure = data.get("brochure", {})
            rooms = data.get("rooms", [])

            # Generate narration script
            summary = _build_property_summary(brochure, rooms)
            script = await claude_service.generate_narration_script(summary)
            log.info("Narration script generated for job %s (%d chars)", job_id, len(script))

            # Convert to audio
            audio_bytes = await elevenlabs_service.text_to_speech(script)

            narration_key = output_s3_key(job_id, "narration.mp3")
            storage_service.upload_bytes(audio_bytes, narration_key, "audio/mpeg")

            narration_asset = Asset(
                job_id=job_id,
                asset_type=AssetType.NARRATION,
                original_filename="narration.mp3",
                s3_key=narration_key,
                mime_type="audio/mpeg",
                size_bytes=len(audio_bytes),
            )
            db.add(narration_asset)
            job.progress_pct = 88
            await db.commit()

            result = {
                "job_id": job_id,
                "narration_key": narration_key,
                "narration_script": script,
                "render_keys": data.get("render_keys", []),
                "brochure": brochure,
                "rooms": rooms,
            }

            log.info("Synthesize complete for job %s — triggering postprocess", job_id)
            from app.workers.postprocess import run as postprocess_run
            postprocess_run.delay(job_id, result)

            return result

        except Exception as exc:
            job.status = JobStatus.FAILED
            job.error_message = str(exc)
            await db.commit()
            raise task.retry(exc=exc, countdown=30)
