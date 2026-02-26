from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from auth import verify_api_key
from services import llm_service, memory_service

router = APIRouter(prefix="/llm", tags=["LLM"])


class ChatRequest(BaseModel):
    message: str
    user_id: str = "default"


class ChatResponse(BaseModel):
    response: str


@router.post("/", response_model=ChatResponse)
async def chat(
    req: ChatRequest,
    _: str = Depends(verify_api_key),
):
    """
    Send a text message to the LLM and get a response.
    Supports memory — the LLM can remember things the user tells it.
    """
    reply = await llm_service.chat(req.message, user_id=req.user_id)
    return ChatResponse(response=reply)


@router.delete("/memories")
async def clear_memories(
    user_id: str = Query("default"),
    _: str = Depends(verify_api_key),
):
    """Clear all stored memories for a user."""
    await memory_service.clear_memories(user_id)
    return {"status": "ok", "message": f"Memories cleared for user '{user_id}'"}
