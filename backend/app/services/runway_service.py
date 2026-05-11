"""
Runway Gen-4 Turbo wrapper for image-to-video generation.
Docs: https://docs.dev.runwayml.com/
"""
import asyncio
import httpx

from app.core.config import settings

_BASE = "https://api.dev.runwayml.com/v1"
_HEADERS = {
    "Authorization": f"Bearer {settings.runway_api_key}",
    "X-Runway-Version": "2024-11-06",
    "Content-Type": "application/json",
}
_POLL_INTERVAL = 5  # seconds
_MAX_POLLS = 60


async def image_to_video(image_url: str, prompt: str, duration: int | None = None) -> bytes:
    """
    Submit an image-to-video task to Runway Gen-4 Turbo.
    Returns raw video bytes (MP4).
    """
    dur = duration or settings.runway_video_duration
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            f"{_BASE}/image_to_video",
            headers=_HEADERS,
            json={
                "model": "gen4_turbo",
                "promptImage": image_url,
                "promptText": prompt,
                "duration": dur,
                "ratio": "16:9",
            },
        )
        r.raise_for_status()
        task_id = r.json()["id"]

    return await _poll_task(task_id)


async def _poll_task(task_id: str) -> bytes:
    async with httpx.AsyncClient(timeout=30) as client:
        for _ in range(_MAX_POLLS):
            await asyncio.sleep(_POLL_INTERVAL)
            r = await client.get(f"{_BASE}/tasks/{task_id}", headers=_HEADERS)
            r.raise_for_status()
            data = r.json()
            status = data.get("status")

            if status == "SUCCEEDED":
                video_url = data["output"][0]
                dl = await client.get(video_url, timeout=120)
                dl.raise_for_status()
                return dl.content

            if status in ("FAILED", "CANCELLED"):
                raise RuntimeError(f"Runway task {task_id} {status}: {data.get('failure', '')}")

    raise TimeoutError(f"Runway task {task_id} did not complete within poll limit")
