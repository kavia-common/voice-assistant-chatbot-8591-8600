import os
from typing import Dict

from django.conf import settings

from .nlu import simple_nlu_reply

try:
    from openai import OpenAI  # openai>=1.0 style
except Exception:
    OpenAI = None  # type: ignore


def _use_openai() -> bool:
    key = getattr(settings, "OPENAI_API_KEY", None) or os.getenv("OPENAI_API_KEY")
    return bool(key) and OpenAI is not None


# PUBLIC_INTERFACE
def generate_reply(text: str) -> Dict[str, str]:
    """Generate a chat reply using OpenAI if configured; otherwise fallback to heuristic NLU.

    Returns:
        dict: {reply: str, provider: 'openai'|'heuristic'}
    """
    if not text or not text.strip():
        return {"reply": "Please provide some text.", "provider": "heuristic"}

    if _use_openai():
        try:
            client = OpenAI(api_key=getattr(settings, "OPENAI_API_KEY", None))
            # Use a small, widely available model name; adjust if environment differs
            model = getattr(settings, "OPENAI_MODEL", "gpt-4o-mini")
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": text},
                ],
                temperature=0.7,
                max_tokens=256,
            )
            reply = resp.choices[0].message.content if resp and resp.choices else None
            if reply:
                return {"reply": reply, "provider": "openai"}
        except Exception:
            # If OpenAI fails for any reason, fallback to heuristic
            pass

    return simple_nlu_reply(text)
