from fastapi import APIRouter, Depends
from fastapi.responses import Response
from pydantic import BaseModel
from auth import verify_api_key
from services import tts_service

router = APIRouter(prefix="/tts", tags=["Text-to-Speech"])


class TTSRequest(BaseModel):
    text: str


@router.post("/")
async def text_to_speech(
    req: TTSRequest,
    _: str = Depends(verify_api_key),
):
    """
    Convert text to speech audio.

    Returns MP3 audio optimized for ESP32 (small file size).
    Voice/language is configured server-side via .env.
    """
    audio_bytes = await tts_service.synthesize(req.text)
    return Response(
        content=audio_bytes,
        media_type="audio/mpeg",
        headers={"Content-Disposition": "inline; filename=speech.mp3"},
    )
