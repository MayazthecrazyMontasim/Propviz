"""
AI service — routes to Anthropic Claude or Google Gemini depending on which
API key is configured. Set ANTHROPIC_API_KEY for Claude, GEMINI_API_KEY for
Gemini (free tier). Gemini is used as a fallback when Claude is not configured.
"""
import base64
import json
import re
from typing import Any

from app.core.config import settings

# ── Prompts (shared between providers) ───────────────────────────────────────

FLOOR_PLAN_PROMPT = """You are an architectural assistant. Analyze this floor plan image and extract all rooms.

For each room return a JSON object with:
- "name": room name (e.g. "Master Bedroom", "Drawing Room", "Kitchen")
- "width_ft": approximate width in feet (numeric)
- "height_ft": approximate height in feet (numeric)
- "features": list of notable features (e.g. ["attached toilet", "verandah", "built-in wardrobe"])

Return ONLY a JSON array — no markdown, no explanation.
Example: [{"name":"Drawing Room","width_ft":10.5,"height_ft":9.1,"features":["verandah"]}]"""

BROCHURE_PROMPT = """Extract all property specifications from this brochure image.

Return a JSON object with these keys (omit any that are not present):
- "developer": developer company name
- "project_name": project name
- "location": full address
- "unit_types": list of unit type strings
- "total_floors": number
- "amenities": list of amenity strings
- "finishing_materials": list of finishing material descriptions
- "handover_date": handover/delivery date as string
- "price_range": price range as string
- "selling_points": list of up to 10 key selling points

Return ONLY valid JSON — no markdown, no explanation."""

NARRATION_PROMPT = """You are a warm, professional real estate narrator for a Bangladeshi audience.
Write a 90-second video narration script for this property:

{property_summary}

The buyer is a busy Dhaka professional couple making a major financial commitment.
Highlight: room sizes, natural light through verandahs, the finished home vision, location convenience.
End with a soft call to action. Keep it intimate and honest — not salesy.
Maximum 200 words. Return only the narration text."""


# ── Provider selection ────────────────────────────────────────────────────────

def _provider() -> str:
    if settings.groq_api_key and settings.groq_api_key not in ("", "your_groq_key"):
        return "groq"
    if settings.anthropic_api_key and settings.anthropic_api_key not in ("", "sk-ant-..."):
        return "anthropic"
    if settings.gemini_api_key:
        return "gemini"
    raise RuntimeError(
        "No AI provider configured. Set GROQ_API_KEY (free at console.groq.com), "
        "ANTHROPIC_API_KEY, or GEMINI_API_KEY."
    )


# ── Anthropic implementation ──────────────────────────────────────────────────

async def _anthropic_vision(image_bytes: bytes, mime_type: str, prompt: str) -> str:
    import anthropic
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    b64 = base64.standard_b64encode(image_bytes).decode()
    response = await client.messages.create(
        model=settings.claude_model,
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": mime_type, "data": b64}},
                {"type": "text", "text": prompt},
            ],
        }],
    )
    return response.content[0].text.strip()


async def _anthropic_text(prompt: str, max_tokens: int = 2048) -> str:
    import anthropic
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    response = await client.messages.create(
        model=settings.claude_model,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()


# ── Gemini implementation ─────────────────────────────────────────────────────

def _gemini_client():
    import google.generativeai as genai
    genai.configure(api_key=settings.gemini_api_key)
    return genai.GenerativeModel(model_name=settings.gemini_model)


async def _gemini_vision(image_bytes: bytes, mime_type: str, prompt: str) -> str:
    import asyncio

    def _call():
        import google.generativeai as genai
        model = _gemini_client()
        part = genai.protos.Blob(mime_type=mime_type, data=image_bytes)
        response = model.generate_content([part, prompt])
        return response.text.strip()

    return await asyncio.to_thread(_call)


async def _gemini_text(prompt: str) -> str:
    import asyncio

    def _call():
        model = _gemini_client()
        response = model.generate_content(prompt)
        return response.text.strip()

    return await asyncio.to_thread(_call)


# ── Groq implementation ───────────────────────────────────────────────────────

async def _groq_vision(image_bytes: bytes, mime_type: str, prompt: str) -> str:
    from groq import AsyncGroq
    b64 = base64.standard_b64encode(image_bytes).decode()
    client = AsyncGroq(api_key=settings.groq_api_key)
    response = await client.chat.completions.create(
        model=settings.groq_vision_model,
        messages=[{"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{b64}"}},
            {"type": "text", "text": prompt},
        ]}],
        max_tokens=2048,
    )
    return response.choices[0].message.content.strip()


async def _groq_text(prompt: str) -> str:
    from groq import AsyncGroq
    client = AsyncGroq(api_key=settings.groq_api_key)
    response = await client.chat.completions.create(
        model=settings.groq_text_model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2048,
    )
    return response.choices[0].message.content.strip()


# ── Public API (same interface regardless of provider) ────────────────────────

async def parse_floor_plan(image_bytes: bytes, mime_type: str) -> list[dict[str, Any]]:
    p = _provider()
    if p == "groq":
        raw = await _groq_vision(image_bytes, mime_type, FLOOR_PLAN_PROMPT)
    elif p == "anthropic":
        raw = await _anthropic_vision(image_bytes, mime_type, FLOOR_PLAN_PROMPT)
    else:
        raw = await _gemini_vision(image_bytes, mime_type, FLOOR_PLAN_PROMPT)
    return json.loads(_strip_fences(raw))


async def parse_brochure(image_bytes: bytes, mime_type: str) -> dict[str, Any]:
    p = _provider()
    if p == "groq":
        raw = await _groq_vision(image_bytes, mime_type, BROCHURE_PROMPT)
    elif p == "anthropic":
        raw = await _anthropic_vision(image_bytes, mime_type, BROCHURE_PROMPT)
    else:
        raw = await _gemini_vision(image_bytes, mime_type, BROCHURE_PROMPT)
    return json.loads(_strip_fences(raw))


async def generate_narration_script(property_summary: str) -> str:
    prompt = NARRATION_PROMPT.format(property_summary=property_summary)
    p = _provider()
    if p == "groq":
        return await _groq_text(prompt)
    if p == "anthropic":
        return await _anthropic_text(prompt, max_tokens=512)
    return await _gemini_text(prompt)


async def generate_render_prompts(rooms: list[dict[str, Any]], style_hint: str = "") -> list[dict[str, str]]:
    room_list = "\n".join(
        f"- {r['name']}: {r.get('width_ft', '?')}x{r.get('height_ft', '?')} ft, features: {r.get('features', [])}"
        for r in rooms
    )
    prompt = f"""For each room below, write a Midjourney-style image generation prompt for a finished, furnished apartment interior.
Style context: modern South Asian / Bangladeshi middle-class family home, warm natural light, realistic render quality.
{f'Additional style: {style_hint}' if style_hint else ''}

Rooms:
{room_list}

Return a JSON array where each item has:
- "room": room name
- "prompt": the image generation prompt (40-60 words, photorealistic, specific)

Return ONLY valid JSON."""

    p = _provider()
    if p == "groq":
        raw = await _groq_text(prompt)
    elif p == "anthropic":
        raw = await _anthropic_text(prompt, max_tokens=2048)
    else:
        raw = await _gemini_text(prompt)
    return json.loads(_strip_fences(raw))


def _strip_fences(text: str) -> str:
    return re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.MULTILINE).strip()
