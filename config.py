import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    API_KEY: str = os.getenv("API_KEY", "change-me")

    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    TTS_LANG: str = os.getenv("TTS_LANG", "en")

    LLM_MODEL: str = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
    STT_MODEL: str = os.getenv("STT_MODEL", "whisper-large-v3")

    # LLM system prompt — kid-friendly, snarky, realistic
    SYSTEM_PROMPT: str = (
        "You are a witty, slightly snarky but friendly voice assistant. "
        "You talk to kids and young people, so keep things appropriate — no violence, "
        "no adult content, nothing scary. You can be playfully sarcastic and have a "
        "personality, but always stay kind underneath. Keep your answers SHORT and "
        "conversational — you're having a spoken conversation, not writing an essay. "
        "Aim for 1-3 sentences unless the user asks for more detail. "
        "Be realistic and honest. If you don't know something, say so with humor. "
        "Never use markdown, bullet points, or formatting — just natural speech. "
        "You have memory: if the user tells you to remember something, confirm it. "
        "If they ask about something they told you before, recall it."
    )


settings = Settings()
