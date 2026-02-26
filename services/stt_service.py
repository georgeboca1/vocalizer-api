import io
from groq import AsyncGroq
from config import settings

_client: AsyncGroq | None = None


def _get_client() -> AsyncGroq:
    global _client
    if _client is None:
        _client = AsyncGroq(api_key=settings.GROQ_API_KEY)
    return _client


async def transcribe(audio_bytes: bytes, filename: str = "audio.wav") -> str:
    """Transcribe audio bytes to text using Groq Whisper. Returns the transcribed text."""
    client = _get_client()

    audio_file = (filename, io.BytesIO(audio_bytes))

    transcription = await client.audio.transcriptions.create(
        file=audio_file,
        model=settings.STT_MODEL,
        response_format="text",
        language="en",
    )

    return transcription.strip()
