import io
from typing import Optional, Tuple

from django.conf import settings

# No heavy imports here; pyttsx3 and gTTS are imported inside helper functions with try/except.


def _try_pyttsx3(text: str, voice: Optional[str] = None) -> Optional[Tuple[bytes, str]]:
    """
    Try synthesizing speech with pyttsx3 into a WAV byte stream.
    Returns (audio_bytes, mime) on success or None on failure.
    """
    try:
        import pyttsx3  # type: ignore
        import tempfile
        import os

        engine = pyttsx3.init()
        if voice:
            # Attempt to set voice by id or name
            for v in engine.getProperty("voices"):
                if voice.lower() in (str(v.id).lower(), str(v.name).lower()):
                    engine.setProperty("voice", v.id)
                    break

        # pyttsx3 doesn't support direct in-memory export reliably; write to temp WAV then load bytes
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tf:
            tmp_name = tf.name
        try:
            engine.save_to_file(text, tmp_name)
            engine.runAndWait()
            with open(tmp_name, "rb") as f:
                data = f.read()
            return data, "audio/wav"
        finally:
            try:
                os.remove(tmp_name)
            except Exception:
                pass
    except Exception:
        return None


def _try_gtts(text: str, lang: str = "en") -> Optional[Tuple[bytes, str]]:
    """
    Try synthesizing with gTTS into MP3 in-memory. Returns (audio_bytes, mime) on success.
    """
    try:
        from gtts import gTTS  # type: ignore

        fp = io.BytesIO()
        tts = gTTS(text=text, lang=lang)
        tts.write_to_fp(fp)
        return fp.getvalue(), "audio/mpeg"
    except Exception:
        return None


# PUBLIC_INTERFACE
def synthesize_speech(text: str, voice: Optional[str] = None, engine: Optional[str] = None) -> Tuple[Optional[bytes], str, str]:
    """Synthesize text to speech, returning audio bytes, mime type, and engine used.

    Order:
      - If engine is 'pyttsx3' or default configured, try pyttsx3 to WAV.
      - If engine is 'gtts' or pyttsx3 fails, fallback to gTTS to MP3.

    Returns:
      (audio_bytes, mime_type, engine_used)
    """
    selected = (engine or getattr(settings, "TTS_ENGINE", "pyttsx3") or "pyttsx3").lower()

    if selected == "pyttsx3":
        res = _try_pyttsx3(text, voice)
        if res:
            audio, mime = res
            return audio, mime, "pyttsx3"
        # fallback to gTTS
        gtts = _try_gtts(text)
        if gtts:
            audio, mime = gtts
            return audio, mime, "gtts"
        return None, "application/json", "none"

    if selected == "gtts":
        gtts = _try_gtts(text)
        if gtts:
            audio, mime = gtts
            return audio, mime, "gtts"
        # fallback to pyttsx3
        res = _try_pyttsx3(text, voice)
        if res:
            audio, mime = res
            return audio, mime, "pyttsx3"
        return None, "application/json", "none"

    # Unknown engine - try both
    res = _try_pyttsx3(text, voice) or _try_gtts(text)
    if res:
        audio, mime = res
        # Decide engine based on mime
        eng = "pyttsx3" if mime == "audio/wav" else "gtts"
        return audio, mime, eng

    return None, "application/json", "none"
