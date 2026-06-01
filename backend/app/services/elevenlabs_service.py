import httpx

from app.core.config import settings

_BASE = "https://api.elevenlabs.io/v1"


async def text_to_speech(text: str, voice_id: str | None = None) -> bytes:
    """Convert narration text to MP3.
    Priority: edge-tts (free) → ElevenLabs (paid) → silent fallback.
    """
    # 1. Free: Microsoft Edge neural TTS — no API key required
    try:
        return await _edge_tts(text)
    except Exception as e:
        print(f"[TTS] edge-tts failed ({e}), trying ElevenLabs", flush=True)

    # 2. ElevenLabs if key is set
    if settings.elevenlabs_api_key:
        try:
            return await _elevenlabs(text, voice_id)
        except Exception as e:
            print(f"[TTS] ElevenLabs failed ({e}), using silent fallback", flush=True)

    # 3. Silent audio via ffmpeg
    return _silent_mp3(len(text) // 15 + 5)


async def _edge_tts(text: str) -> bytes:
    """Generate MP3 using Microsoft Edge TTS (completely free, no key needed)."""
    import asyncio
    import tempfile
    import os
    import edge_tts

    # Warm, professional English voice suitable for property narration
    voice = "en-IN-NeerjaNeural"   # Indian English, female, clear
    communicate = edge_tts.Communicate(text, voice)

    with tempfile.TemporaryDirectory() as tmpdir:
        out = os.path.join(tmpdir, "narration.mp3")
        await communicate.save(out)
        with open(out, "rb") as f:
            return f.read()


async def _elevenlabs(text: str, voice_id: str | None) -> bytes:
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
        r = await client.post(url, json=payload, headers=headers)
        r.raise_for_status()
        return r.content


def _silent_mp3(duration_seconds: int = 30) -> bytes:
    import subprocess
    import tempfile
    import os

    with tempfile.TemporaryDirectory() as tmpdir:
        out = os.path.join(tmpdir, "silent.mp3")
        subprocess.run(
            ["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
             "-t", str(max(duration_seconds, 5)), "-c:a", "libmp3lame", "-b:a", "128k", out],
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
