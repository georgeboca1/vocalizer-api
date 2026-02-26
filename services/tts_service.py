import asyncio
import io
from gtts import gTTS
from config import settings


def _generate_speech(text: str, lang: str) -> bytes:
    """Synchronous gTTS generation — runs in a thread pool."""
    tts = gTTS(text=text, lang=lang, slow=False)
    buffer = io.BytesIO()
    tts.write_to_fp(buffer)
    return buffer.getvalue()


async def synthesize(text: str) -> bytes:
    """
    Convert text to speech using Google Translate TTS.
    Returns MP3 audio bytes suitable for ESP32.
    """
    lang = settings.TTS_LANG
    audio_bytes = await asyncio.to_thread(_generate_speech, text, lang)
    return audio_bytes
