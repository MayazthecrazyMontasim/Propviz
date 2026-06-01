import httpx

from app.core.config import settings

_BASE = "https://api.elevenlabs.io/v1"


async def text_to_speech(text: str, voice_id: str | None = None) -> bytes:
    """Convert narration text to MP3. Falls back to silent audio if ElevenLabs has no credits."""
    if not settings.elevenlabs_api_key:
        print("[ELEVENLABS] no key set, using silent audio fallback", flush=True)
        return _silent_mp3(len(text) // 15 + 5)

    vid = voice_id or settings.elevenlabs_voice_id
    url = f"{_BASE}/text-to-speech/{vid}"
    headers = {
        "xi-api-key": settings.elevenlabs_api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
    }
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(url, json=payload, headers=headers)
        if not response.is_success:
            print(f"[ELEVENLABS] {response.status_code} — using silent audio fallback", flush=True)
            return _silent_mp3(len(text) // 15 + 5)
        return response.content


def _silent_mp3(duration_seconds: int = 30) -> bytes:
    """Generate a minimal valid silent MP3 using ffmpeg."""
    import subprocess
    import tempfile
    import os

    with tempfile.TemporaryDirectory() as tmpdir:
        out = os.path.join(tmpdir, "silent.mp3")
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=stereo",
                "-t", str(max(duration_seconds, 5)),
                "-c:a", "libmp3lame", "-b:a", "128k",
                out,
            ],
            check=True, capture_output=True,
        )
        with open(out, "rb") as f:
            return f.read()


async def list_voices() -> list[dict]:
    headers = {"xi-api-key": settings.elevenlabs_api_key}
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(f"{_BASE}/voices", headers=headers)
        r.raise_for_status()
        return r.json().get("voices", [])
