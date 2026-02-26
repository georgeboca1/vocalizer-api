from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import Response
from auth import verify_api_key
from services import stt_service, llm_service, tts_service

router = APIRouter(prefix="/conversation", tags=["Conversation"])


@router.post("/")
async def conversation(
    audio: UploadFile = File(...),
    user_id: str = Form("default"),
    _: str = Depends(verify_api_key),
):
    """
    Full conversation pipeline in a single request: Audio In → Text → LLM → Audio Out.

    This is the primary endpoint for the ESP32. It accepts an audio file,
    transcribes it, sends it to the LLM, converts the response to speech,
    and returns the audio response.

    Minimizes round-trips — one request, one response.

    Returns MP3 audio of the LLM's spoken response.
    The transcribed text and LLM response text are included in response headers
    for debugging (X-Transcript and X-Response).
    """
    # Step 1: Speech-to-Text
    audio_bytes = await audio.read()
    transcript = await stt_service.transcribe(audio_bytes, filename=audio.filename or "audio.wav")

    # Step 2: LLM
    llm_response = await llm_service.chat(transcript, user_id=user_id)

    # Step 3: Text-to-Speech
    speech_bytes = await tts_service.synthesize(llm_response)

    return Response(
        content=speech_bytes,
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": "inline; filename=response.mp3",
            "X-Transcript": transcript.replace("\n", " ")[:500],
            "X-Response": llm_response.replace("\n", " ")[:500],
        },
    )
