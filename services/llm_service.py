from groq import AsyncGroq
from config import settings
from services import memory_service

_client: AsyncGroq | None = None


def _get_client() -> AsyncGroq:
    global _client
    if _client is None:
        _client = AsyncGroq(api_key=settings.GROQ_API_KEY)
    return _client


async def chat(user_message: str, user_id: str = "default") -> str:
    """
    Send a message to the LLM with context from stored memories.
    Detects if the user wants to remember something and stores it.
    Returns the LLM response text.
    """
    client = _get_client()

    # Retrieve existing memories for context
    memories = await memory_service.get_memories(user_id)

    # Build messages
    messages = [{"role": "system", "content": settings.SYSTEM_PROMPT}]

    if memories:
        memory_block = "\n".join(f"- {m}" for m in memories)
        messages.append({
            "role": "system",
            "content": f"Here are things the user has asked you to remember:\n{memory_block}",
        })

    messages.append({"role": "user", "content": user_message})

    # Call Groq LLM
    response = await client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=messages,
        temperature=0.7,
        max_tokens=256,
        top_p=0.9,
    )

    assistant_reply = response.choices[0].message.content.strip()

    # Detect memory requests — ask the LLM to extract them
    await _maybe_store_memory(client, user_message, user_id)

    return assistant_reply


async def _maybe_store_memory(client: AsyncGroq, user_message: str, user_id: str):
    """Use a fast small model to detect if the user wants to remember something."""
    detection = await client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a memory extraction tool. If the user is asking to remember, "
                    "save, or store some information, extract ONLY the fact to remember as "
                    "a short sentence. If the user is NOT asking to remember anything, "
                    "respond with exactly: NONE"
                ),
            },
            {"role": "user", "content": user_message},
        ],
        temperature=0,
        max_tokens=64,
    )

    result = detection.choices[0].message.content.strip()
    if result.upper() != "NONE" and len(result) < 200:
        await memory_service.store_memory(user_id, result)
