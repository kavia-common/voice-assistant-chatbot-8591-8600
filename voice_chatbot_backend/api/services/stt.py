import io
import time
from typing import Dict, Any, Optional

import speech_recognition as sr
from django.conf import settings


def _recognize_with_sphinx(recognizer: sr.Recognizer, audio: sr.AudioData, language: Optional[str]) -> Optional[str]:
    """
    Try CMU Sphinx (offline). Returns None if not available or fails.
    """
    try:
        # language not directly supported by pocketsphinx via SpeechRecognition for many locales
        return recognizer.recognize_sphinx(audio)  # type: ignore[no-any-return]
    except Exception:
        return None


def _recognize_with_google(recognizer: sr.Recognizer, audio: sr.AudioData, language: Optional[str]) -> str:
    """
    Use Google Web Speech API without API key (free, rate-limited).
    """
    kwargs = {}
    if language:
        kwargs["language"] = language
    return recognizer.recognize_google(audio, **kwargs)  # type: ignore[no-any-return]


# PUBLIC_INTERFACE
def transcribe_file(file_bytes: bytes, language: Optional[str] = None) -> Dict[str, Any]:
    """Transcribe audio bytes using pocketsphinx if available, otherwise Google Web Speech.

    Returns:
      dict: { text: str, engine: str, duration_ms: int }
    """
    recognizer = sr.Recognizer()
    start = time.time()
    engine_used = None
    text = ""

    # Convert uploaded bytes to AudioData by first loading as an AudioFile
    with sr.AudioFile(io.BytesIO(file_bytes)) as source:
        audio = recognizer.record(source)

    preferred = getattr(settings, "STT_PREFERRED_ENGINE", "google") or "google"

    if preferred.lower() == "sphinx":
        result = _recognize_with_sphinx(recognizer, audio, language)
        if result:
            text = result
            engine_used = "pocketsphinx"
        else:
            # fallback to google
            try:
                text = _recognize_with_google(recognizer, audio, language)
                engine_used = "google"
            except Exception as e:
                raise RuntimeError(f"STT failed with both sphinx and google: {e}") from e
    else:
        # try google first
        try:
            text = _recognize_with_google(recognizer, audio, language)
            engine_used = "google"
        except Exception:
            # fallback to sphinx
            result = _recognize_with_sphinx(recognizer, audio, language)
            if result:
                text = result
                engine_used = "pocketsphinx"
            else:
                raise RuntimeError("STT failed: neither google nor pocketsphinx succeeded")

    duration_ms = int((time.time() - start) * 1000)
    return {"text": text, "engine": engine_used or "unknown", "duration_ms": duration_ms}
