import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from routers import stt, llm, tts, conversation

app = FastAPI(
    title="Vocalizer API",
    description=(
        "High-performance voice conversation API for ESP32. "
        "Provides Speech-to-Text, LLM chat, Text-to-Speech, "
        "and a combined conversation endpoint."
    ),
    version="1.0.0",
)

# CORS — allow all for cloudflared tunnel usage
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Transcript", "X-Response"],
)

# Register routers
app.include_router(stt.router)
app.include_router(llm.router)
app.include_router(tts.router)
app.include_router(conversation.router)


@app.get("/health", tags=["Health"])
async def health():
    """Health check endpoint (no auth required)."""
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
    )
