import httpx

from app.core.config import settings

_BASE = "https://api.elevenlabs.io/v1"


async def text_to_speech(text: str, voice_id: str | None = None) -> bytes:
    """Convert narration text to MP3 audio bytes via ElevenLabs."""
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
        response.raise_for_status()
        return response.content


async def list_voices() -> list[dict]:
    headers = {"xi-api-key": settings.elevenlabs_api_key}
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(f"{_BASE}/voices", headers=headers)
        r.raise_for_status()
        return r.json().get("voices", [])
