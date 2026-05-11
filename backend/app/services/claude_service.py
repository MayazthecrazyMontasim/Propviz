import base64
import json
import re
from typing import Any

import anthropic

from app.core.config import settings

_client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

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


async def parse_floor_plan(image_bytes: bytes, mime_type: str) -> list[dict[str, Any]]:
    b64 = base64.standard_b64encode(image_bytes).decode()
    response = await _client.messages.create(
        model=settings.claude_model,
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": mime_type, "data": b64}},
                {"type": "text", "text": FLOOR_PLAN_PROMPT},
            ],
        }],
    )
    raw = response.content[0].text.strip()
    return json.loads(_strip_json_fences(raw))


async def parse_brochure(image_bytes: bytes, mime_type: str) -> dict[str, Any]:
    b64 = base64.standard_b64encode(image_bytes).decode()
    response = await _client.messages.create(
        model=settings.claude_model,
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": mime_type, "data": b64}},
                {"type": "text", "text": BROCHURE_PROMPT},
            ],
        }],
    )
    raw = response.content[0].text.strip()
    return json.loads(_strip_json_fences(raw))


async def generate_narration_script(property_summary: str) -> str:
    response = await _client.messages.create(
        model=settings.claude_model,
        max_tokens=512,
        messages=[{
            "role": "user",
            "content": NARRATION_PROMPT.format(property_summary=property_summary),
        }],
    )
    return response.content[0].text.strip()


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

    response = await _client.messages.create(
        model=settings.claude_model,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.content[0].text.strip()
    return json.loads(_strip_json_fences(raw))


def _strip_json_fences(text: str) -> str:
    return re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.MULTILINE).strip()
