import aiosqlite
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "memories.db")


async def _ensure_table():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                memory TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        await db.commit()


_initialized = False


async def init():
    global _initialized
    if not _initialized:
        await _ensure_table()
        _initialized = True


async def store_memory(user_id: str, memory: str):
    """Store a memory for a user."""
    await init()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO memories (user_id, memory) VALUES (?, ?)",
            (user_id, memory),
        )
        await db.commit()


async def get_memories(user_id: str, limit: int = 20) -> list[str]:
    """Retrieve recent memories for a user."""
    await init()
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT memory FROM memories WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit),
        )
        rows = await cursor.fetchall()
        return [row[0] for row in reversed(rows)]


async def clear_memories(user_id: str):
    """Clear all memories for a user."""
    await init()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM memories WHERE user_id = ?", (user_id,))
        await db.commit()
