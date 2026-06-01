"""
Runway Gen-4 Turbo wrapper for image-to-video generation.
Docs: https://docs.dev.runwayml.com/
"""
import asyncio
import httpx

from app.core.config import settings

_BASE = "https://api.dev.runwayml.com/v1"
_POLL_INTERVAL = 5  # seconds
_MAX_POLLS = 72     # 6 minutes max


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {settings.runway_api_key}",
        "X-Runway-Version": "2024-11-06",
        "Content-Type": "application/json",
    }


async def image_to_video(image_url: str, prompt: str, duration: int | None = None) -> bytes:
    """
    Submit an image-to-video task to Runway Gen-4 Turbo.
    Falls back to a static-image clip if Runway has no credits.
    Returns raw video bytes (MP4).
    """
    dur = duration or settings.runway_video_duration

    if not settings.runway_api_key:
        return await _static_clip(image_url, dur)

    payload = {
        "model": "gen4_turbo",
        "promptImage": image_url,
        "promptText": prompt,
        "duration": dur,
        "ratio": "1280:720",
    }
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(f"{_BASE}/image_to_video", headers=_headers(), json=payload)
        if not r.is_success:
            # No credits or API issue — fall back to static clip so the pipeline completes
            print(f"[RUNWAY] falling back to static clip: {r.status_code} {r.text[:200]}", flush=True)
            return await _static_clip(image_url, dur)
        task_id = r.json()["id"]

    return await _poll_task(task_id)


async def _static_clip(image_url: str, duration: int = 5) -> bytes:
    """Convert a static image to a short MP4 using ffmpeg (free fallback)."""
    import os
    import subprocess
    import tempfile

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            r = await client.get(image_url, timeout=15)
            img_bytes = r.content if r.is_success else None
        except Exception:
            img_bytes = None

    with tempfile.TemporaryDirectory() as tmpdir:
        img_path = os.path.join(tmpdir, "frame.jpg")
        vid_path = os.path.join(tmpdir, "clip.mp4")

        if img_bytes:
            with open(img_path, "wb") as f:
                f.write(img_bytes)
            input_args = ["-loop", "1", "-i", img_path]
        else:
            # No image available — generate a solid dark frame
            input_args = ["-f", "lavfi", "-i", "color=c=0x1a1a2e:s=1280x720"]

        subprocess.run(
            ["ffmpeg", "-y"] + input_args + [
                "-c:v", "libx264", "-t", str(duration),
                "-pix_fmt", "yuv420p", "-vf", "scale=1280:720",
                "-r", "24", vid_path,
            ],
            check=True, capture_output=True,
        )
        with open(vid_path, "rb") as f:
            return f.read()


async def _poll_task(task_id: str) -> bytes:
    async with httpx.AsyncClient(timeout=60) as client:
        for _ in range(_MAX_POLLS):
            await asyncio.sleep(_POLL_INTERVAL)
            r = await client.get(f"{_BASE}/tasks/{task_id}", headers=_headers())
            if not r.is_success:
                raise RuntimeError(f"Runway poll {r.status_code}: {r.text[:300]}")
            data = r.json()
            status = data.get("status")

            if status == "SUCCEEDED":
                video_url = data["output"][0]
                dl = await client.get(video_url, timeout=180)
                dl.raise_for_status()
                return dl.content

            if status in ("FAILED", "CANCELLED"):
                raise RuntimeError(
                    f"Runway task {task_id} {status}: {data.get('failure', data)}"
                )

    raise TimeoutError(f"Runway task {task_id} did not complete in {_MAX_POLLS * _POLL_INTERVAL}s")
