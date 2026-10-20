import logging
from typing import List, Dict, Optional
from google import genai
from google.genai import types
import config

logger = logging.getLogger(__name__)

# Google GenAI mijozi
_client: Optional[genai.Client] = None

def _get_client() -> Optional[genai.Client]:
    """GenAI mijozini xavfsiz initsializatsiya qilish."""
    global _client
    if _client is None:
        if not config.AI_API_KEY:
            logger.error("AI_API_KEY topilmadi! Iltimos, .env faylini to'ldiring.")
            return None
        _client = genai.Client(api_key=config.AI_API_KEY)
    return _client

async def get_reply(history: List[Dict[str, str]], user_text: str) -> Optional[str]:
    """
    Foydalanuvchi matni va chat tarixini olib, AI javobini qaytaradi.
    """
    client = _get_client()
    if not client:
        return None

    # Chat tarixini moslash
    contents = []
    for msg in history:
        role = "user" if msg.get("role") == "user" else "model"
        contents.append(
            types.Content(
                role=role,
                parts=[types.Part.from_text(text=msg.get("text", ""))]
            )
        )

    contents.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_text)]
        )
    )

    generate_config = types.GenerateContentConfig(
        system_instruction=config.SYSTEM_PROMPT,
        temperature=0.7,
    )

    # Google API so'ragan eng yangi va mavjud modellar
    candidate_models = [
        config.AI_MODEL,
        "gemini-3.8-flash",
        "gemini-3.5-flash",
        "gemini-2.5-pro",
    ]

    for model_name in candidate_models:
        if not model_name:
            continue
        try:
            response = await client.aio.models.generate_content(
                model=model_name,
                contents=contents,
                config=generate_config
            )
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            logger.warning("Model '%s' xatosi: %s. Keyingisi sinab ko'riladi...", model_name, e)
            continue

    logger.error("Barcha AI modellari bilan so'rov muvaffaqiyatsiz tugadi.")
    return None
