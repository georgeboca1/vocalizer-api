from fastapi import APIRouter, Depends, File, UploadFile
from auth import verify_api_key
from services import stt_service

router = APIRouter(prefix="/stt", tags=["Speech-to-Text"])


@router.post("/")
async def speech_to_text(
    audio: UploadFile = File(...),
    _: str = Depends(verify_api_key),
):
    """
    Convert audio to text.

    Accepts audio files (WAV, MP3, OGG, FLAC, WebM, etc.).
    Returns the transcribed text.
    """
    audio_bytes = await audio.read()
    text = await stt_service.transcribe(audio_bytes, filename=audio.filename or "audio.wav")
    return {"text": text}
