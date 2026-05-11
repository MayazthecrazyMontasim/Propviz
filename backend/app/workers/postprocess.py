"""
Stage 5 — Postprocess
Stitches render clips + narration audio + branding into a final branded MP4.
Uses ffmpeg for video assembly (must be installed in the worker container).
Uploads final video to S3 and marks the job complete.
"""
import asyncio
import logging
import os
import subprocess
import tempfile
from typing import Any

from celery import shared_task

from app.core.database import AsyncSessionLocal
from app.models.job import Job, JobStatus
from app.models.asset import Asset, AssetType
from app.services import storage_service
from app.utils.helpers import output_s3_key

log = logging.getLogger(__name__)


@shared_task(bind=True, name="app.workers.postprocess.run", max_retries=2)
def run(self, job_id: str, synthesize_result: dict[str, Any]) -> dict[str, Any]:
    return asyncio.run(_run_async(self, job_id, synthesize_result))


async def _run_async(task, job_id: str, data: dict[str, Any]) -> dict[str, Any]:
    async with AsyncSessionLocal() as db:
        job = await db.get(Job, job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")

        job.status = JobStatus.POSTPROCESSING
        job.current_stage = "postprocess"
        job.progress_pct = 90
        await db.commit()

        try:
            render_keys = data.get("render_keys", [])
            narration_key = data.get("narration_key")

            with tempfile.TemporaryDirectory() as tmpdir:
                # Download render clips
                clip_paths: list[str] = []
                for idx, key in enumerate(render_keys):
                    clip_bytes = storage_service.download_bytes(key)
                    path = os.path.join(tmpdir, f"clip_{idx:02d}.mp4")
                    with open(path, "wb") as f:
                        f.write(clip_bytes)
                    clip_paths.append(path)

                # Download narration audio
                audio_path = None
                if narration_key:
                    audio_bytes = storage_service.download_bytes(narration_key)
                    audio_path = os.path.join(tmpdir, "narration.mp3")
                    with open(audio_path, "wb") as f:
                        f.write(audio_bytes)

                # Concatenate clips
                concat_path = os.path.join(tmpdir, "concat.mp4")
                _ffmpeg_concat(clip_paths, concat_path)

                # Mix narration over video
                final_path = os.path.join(tmpdir, "final.mp4")
                _ffmpeg_mix_audio(concat_path, audio_path, final_path)

                # Upload final video
                with open(final_path, "rb") as f:
                    final_bytes = f.read()

            final_key = output_s3_key(job_id, "final_tour.mp4")
            final_url = storage_service.upload_bytes(final_bytes, final_key, "video/mp4")

            asset = Asset(
                job_id=job_id,
                asset_type=AssetType.VIDEO_FINAL,
                original_filename="final_tour.mp4",
                s3_key=final_key,
                mime_type="video/mp4",
                size_bytes=len(final_bytes),
                cdn_url=final_url,
            )
            db.add(asset)

            job.status = JobStatus.COMPLETE
            job.current_stage = None
            job.progress_pct = 100
            job.output_url = final_url
            await db.commit()

            log.info("Job %s complete — video at %s", job_id, final_url)
            return {"job_id": job_id, "output_url": final_url}

        except Exception as exc:
            job.status = JobStatus.FAILED
            job.error_message = str(exc)
            await db.commit()
            raise task.retry(exc=exc, countdown=60)


def _ffmpeg_concat(clip_paths: list[str], output: str) -> None:
    if not clip_paths:
        # Create a 5-second black placeholder if no clips
        subprocess.run(
            ["ffmpeg", "-y", "-f", "lavfi", "-i", "color=black:s=1280x720:d=5",
             "-c:v", "libx264", output],
            check=True, capture_output=True,
        )
        return

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        for p in clip_paths:
            f.write(f"file '{p}'\n")
        list_path = f.name

    try:
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_path,
             "-c", "copy", output],
            check=True, capture_output=True,
        )
    finally:
        os.unlink(list_path)


def _ffmpeg_mix_audio(video: str, audio: str | None, output: str) -> None:
    if not audio:
        subprocess.run(["ffmpeg", "-y", "-i", video, "-c", "copy", output],
                       check=True, capture_output=True)
        return

    subprocess.run(
        ["ffmpeg", "-y",
         "-i", video, "-i", audio,
         "-map", "0:v:0", "-map", "1:a:0",
         "-c:v", "copy", "-c:a", "aac", "-shortest",
         output],
        check=True, capture_output=True,
    )
