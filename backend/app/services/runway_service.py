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
    Returns raw video bytes (MP4).
    """
    dur = duration or settings.runway_video_duration
    payload = {
        "model": "gen4_turbo",
        "promptImage": image_url,
        "promptText": prompt,
        "duration": dur,
        "ratio": "1280:720",   # Runway expects WxH format, not "16:9"
    }
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(f"{_BASE}/image_to_video", headers=_headers(), json=payload)
        if not r.is_success:
            raise RuntimeError(
                f"Runway API {r.status_code}: {r.text[:500]}"
            )
        task_id = r.json()["id"]

    return await _poll_task(task_id)


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
