"""
Stage 3 — Reconstruct
Generates AI interior renders for each room using:
1. Claude → render prompts per room
2. Runway Gen-4 Turbo → image-to-video short clips per room
Stores render assets, then triggers Stage 4 (synthesize).
"""
import logging
from typing import Any

from celery import shared_task

from app.core.database import AsyncSessionLocal
from app.models.job import Job, JobStatus
from app.models.asset import Asset, AssetType
from app.services import claude_service, runway_service, storage_service
from app.utils.helpers import output_s3_key

log = logging.getLogger(__name__)

# Rooms to render (skip utility spaces)
_SKIP_ROOMS = {"toilet", "bathroom", "lift", "stair", "lobby", "corridor", "store"}

# Use developer exterior rendering as the opening image reference
_EXTERIOR_PROMPT = (
    "Smooth cinematic pan of a modern residential building facade at golden hour, "
    "balconies with green plants, warm lighting, Dhaka Bangladesh setting"
)


@shared_task(bind=True, name="app.workers.reconstruct.run", max_retries=2)
def run(self, job_id: str, parse_result: dict[str, Any]) -> dict[str, Any]:
    import asyncio
    return asyncio.run(_run_async(self, job_id, parse_result))


async def _run_async(task, job_id: str, parse_result: dict[str, Any]) -> dict[str, Any]:
    async with AsyncSessionLocal() as db:
        job = await db.get(Job, job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")

        job.status = JobStatus.RECONSTRUCTING
        job.current_stage = "reconstruct"
        job.progress_pct = 58
        await db.commit()

        try:
            rooms: list[dict] = parse_result.get("rooms", [])
            brochure: dict = parse_result.get("brochure", {})

            # Filter to renderable rooms
            renderable = [
                r for r in rooms
                if not any(skip in r["name"].lower() for skip in _SKIP_ROOMS)
            ][:6]  # max 6 rooms

            # Ask Claude to write optimized render prompts
            style_hint = brochure.get("finishing_materials", [])
            style_str = ", ".join(style_hint[:3]) if style_hint else ""
            render_prompts = await claude_service.generate_render_prompts(renderable, style_str)

            render_keys: list[str] = []
            total = len(render_prompts)

            for idx, item in enumerate(render_prompts):
                room_name = item["room"]
                prompt = item["prompt"]
                log.info("Generating render %d/%d: %s", idx + 1, total, room_name)

                # Use a placeholder exterior image as the seed for Gen-4
                # In production this would be the actual developer exterior render
                seed_url = _get_seed_image_url(job_id, parse_result)
                video_bytes = await runway_service.image_to_video(seed_url, prompt, duration=5)

                key = output_s3_key(job_id, f"render_{idx:02d}_{room_name.replace(' ', '_')}.mp4")
                storage_service.upload_bytes(video_bytes, key, "video/mp4")

                asset = Asset(
                    job_id=job_id,
                    asset_type=AssetType.RENDER,
                    original_filename=f"render_{room_name}.mp4",
                    s3_key=key,
                    mime_type="video/mp4",
                    size_bytes=len(video_bytes),
                )
                db.add(asset)
                render_keys.append(key)

                progress = 58 + int((idx + 1) / total * 20)
                job.progress_pct = progress
                await db.commit()

            job.render_keys = render_keys
            await db.commit()

            result = {
                "job_id": job_id,
                "render_keys": render_keys,
                "rooms": rooms,
                "brochure": brochure,
            }
            log.info("Reconstruct complete for job %s — %d renders", job_id, len(render_keys))
            return result

        except Exception as exc:
            job.status = JobStatus.FAILED
            job.error_message = str(exc)
            await db.commit()
            raise task.retry(exc=exc, countdown=120)


def _get_seed_image_url(job_id: str, parse_result: dict) -> str:
    # Use the developer exterior rendering if stored in S3, else a neutral placeholder
    brochure = parse_result.get("brochure", {})
    if brochure.get("exterior_render_key"):
        return storage_service._url(brochure["exterior_render_key"])
    # Fallback: a neutral room image placeholder
    return "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=1280"
